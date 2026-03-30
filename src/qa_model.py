import collections
import os
from collections import Counter
from typing import Dict, List, Union

import dotenv
from openai import OpenAI

import qa_response
from utils import configure_logger
from retry import call_with_retry, RetryConfig

# Configure logger
logger = configure_logger()

dotenv.load_dotenv()


class ChainOfThoughtsQuestionAnswering:
    """Legacy QA class - kept for backward compatibility."""

    def __init__(
        self,
        qa_prompt_file_path: str,
        model_name: str = "gpt-4o-mini",
        model_temperature: float = 1.0,
        reasoning_effort: str = None,
        max_retries: int = 5,
        max_answer_words: int = 75,
        **kwargs,
    ):
        with open(qa_prompt_file_path, "r") as file:
            self.qa_prompt = file.read()

        self.max_answer_words = max_answer_words
        self.max_retries = max_retries
        self.model_name = model_name
        self.model_temperature = model_temperature
        self.reasoning_effort = reasoning_effort

        # Prepare reasoning parameters for API calls
        self.reasoning_params = (
            {"reasoning": {"effort": reasoning_effort, "summary": "auto"}}
            if reasoning_effort
            else {}
        )

        # Initialize OpenAI client
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")

        self.client = OpenAI(
            base_url=endpoint + "/openai/v1/",
            api_key=api_key,
        )

    def answer(self, question: str, response_format, **kwargs):
        # Format prompt with question
        formatted_prompt = self.qa_prompt.format(question=question)

        # Call OpenAI Responses API
        if response_format is not None:
            response = self.client.responses.parse(
                model=self.model_name,
                input=formatted_prompt,
                text_format=response_format,
                **self.reasoning_params
            )
            # Get parsed Pydantic object and convert to dict
            parsed_result = response.output_parsed
            result = (
                parsed_result.model_dump()
                if hasattr(parsed_result, "model_dump")
                else parsed_result.dict()
            )
        else:
            logger.warning(
                "No response_format specified, using basic chat completion without structured parsing."
            )
            # For non-structured responses, use basic chat completion
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": formatted_prompt},
                ],
                temperature=self.model_temperature,
            )
            result = {"answer": response.choices[0].message.content}

        return result


def compare(x: list[str], y: list[str]) -> bool:
    """
    Compare two lists of strings and return True if they are equal, ignoring order.

    Args:
        x (list[str]): First list of strings.
        y (list[str]): Second list of strings.

    Returns:
        bool: True if the lists are equal, ignoring order; False otherwise.
    """
    return collections.Counter(x) == collections.Counter(y)


class BaseGQA:
    def get_answer_length(self, task_dict: Dict, answer_dict: Dict) -> None:
        """
        Placeholder method to get the length of an answer.

        Args:
            task_dict (Dict): Task dictionary containing task details.
            answer_dict (Dict): Answer dictionary containing answer details.

        Returns:
            None
        """
        pass

    def check_fail_count(
        self, fail_count: int, task_dict: Dict, context: str = ""
    ) -> None:
        """
        Check if the fail count exceeds the maximum retries and log an error.

        Args:
            fail_count (int): Current fail count.
            task_dict (Dict): Task dictionary containing task details.
            context (str): Optional context about what operation was being attempted.

        Raises:
            ValueError: If the fail count exceeds the maximum retries.
        """
        if fail_count >= self.max_retries:
            error_msg = f"Max retries ({self.max_retries}) reached for case {task_dict['case_id']}"
            if context:
                error_msg += f" during {context}"
            error_msg += ". Exiting."
            logger.error(error_msg)
            raise ValueError(error_msg)

    def validate_evidence_coverage(self, task_dict: Dict, answer_dict: Dict):
        """
        Validate if the length of LLM evidence_relevance_list matches the given input evidence_list.
        """
        evidence_count = len(task_dict["sentences"])
        pred_count = len(answer_dict.get("evidence_relevance_list", []))

        if pred_count != evidence_count:
            logger.debug(
                f"[case {task_dict['case_id']}] Evidence count mismatch: {pred_count} != {evidence_count}"
            )
            return False

        return True

    def get_valid_citations(self, task_dict: Dict, answer_dict: Dict):
        case_id = task_dict["case_id"]
        answer_text = answer_dict["final_answer"].strip()
        answer_sentences = []
        for line in answer_text.split("\n"):
            """
            e.g., The final negative retrograde cholangiogram result after the procedure confirms that ERCP was an effective treatment for the patient's condition. |8|
            """
            if not line.strip():
                continue
            line_parts = line.rsplit("|", maxsplit=2)
            if len(line_parts) < 3:
                # No citations found
                sent = line.strip()
                citations = []
            else:
                sent = line_parts[-3].strip()
                citation_part = line_parts[-2]
                citations = [c for c in citation_part.split(",") if c.strip()]

            # Add a period at the end of the sentence if it doesn't have one
            if sent and sent[-1] not in ".!?":
                sent += "."

            answer_sentences.append({"sentence": sent, "citations": citations})

        case_answer = " ".join(
            [sent["sentence"] for sent in answer_sentences if sent["sentence"]]
        )
        case_answer_words = [w for w in case_answer.split(" ") if w.strip()]

        case_citations = {
            citation for sent in answer_sentences for citation in sent["citations"]
        }
        return case_citations, len(case_answer_words)

    def check_answer_word_count(self, answer_length: int):
        return answer_length <= self.max_answer_words

    def check_answer_citation_coverage(
        self, evidence_dict: Dict, answer_citations: List
    ):
        """
        Check if the answer citations are covered by the evidence list.
        """
        issue_list = []
        evidence_list = evidence_dict.get("evidence_relevance_list", [])
        essential_evidence_list = [
            str(idx + 1)
            for idx, e in enumerate(evidence_list)
            if e == qa_response.RelevanceCategory.ESSENTIAL
        ]
        supplementary_evidence_list = [
            str(idx + 1)
            for idx, e in enumerate(evidence_list)
            if e == qa_response.RelevanceCategory.SUPPLEMENTARY
        ]

        # cited evidence in the answer must match the essential evidence.
        for citation in answer_citations:
            if citation not in essential_evidence_list:
                if (
                    self.include_supplementary
                    and citation in supplementary_evidence_list
                ):
                    continue
                issue_str = (
                    f"Answer citation {citation} is not in the essential evidence list."
                )
                issue_list.append(issue_str)

        for citation in essential_evidence_list:
            if citation not in answer_citations:
                issue_str = f"Essential evidence {citation} is not cited in the answer."
                issue_list.append(issue_str)
        issue_list_str = "\n".join(issue_list)

        no_issues_found = len(issue_list) == 0

        return no_issues_found, issue_list_str


class GroundedQA(BaseGQA):
    """
    Grounded QA: Question answering where answers are grounded in evidence.

    Implements a two-stage pipeline:
    1. Classify evidence relevance (which sentences are relevant)
    2. Generate answer grounded in the relevant evidence

    Features:
    - Self-Consistency: Generate k independent samples and aggregate via majority voting
    - Pattern 1: ID→label mapping for structural validation
    - Conversation-based correction: Use previous_response_id for targeted repairs
    """

    def __init__(
        self,
        evidence_prompt_file_path: str,
        qa_prompt_file_path: str,
        model_name: str = "gpt-4o-mini",
        reasoning_effort: str = None,
        include_supplementary: bool = False,
        evidence_batch_size: Union[int, str] = 10,  # int or "use_all"
        evidence_batch_overlap: int = 0,
        max_retries: int = 5,
        max_answer_words: int = 75,
        num_samples: int = 1,  # k for Self-Consistency (1 = single sample)
        rewrite_prompt_file_path: str = None,
        **kwargs,
    ):
        # Note: temperature parameters removed - not supported by responses.parse() API
        # If passed in configs/kwargs, they are silently ignored for backward compatibility

        # Load prompts from files
        with open(evidence_prompt_file_path, "r") as file:
            self.evidence_prompt = file.read()
        with open(qa_prompt_file_path, "r") as file:
            self.qa_prompt = file.read()

        # Optional rewrite prompt (if provided, answers are rewritten after generation)
        if rewrite_prompt_file_path:
            with open(rewrite_prompt_file_path, "r") as file:
                self.rewrite_prompt = file.read()
        else:
            self.rewrite_prompt = None

        self.include_supplementary = include_supplementary
        self.evidence_batch_size = evidence_batch_size
        self.evidence_batch_overlap = evidence_batch_overlap
        self.max_answer_words = max_answer_words
        self.max_retries = max_retries
        self.model_name = model_name
        self.reasoning_effort = reasoning_effort

        # Prepare reasoning parameters for API calls
        self.reasoning_params = (
            {"reasoning": {"effort": reasoning_effort, "summary": "auto"}}
            if reasoning_effort
            else {}
        )

        # Self-Consistency parameters
        self.num_samples = num_samples

        # Initialize direct OpenAI client (replaces LangChain)
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")

        self.client = OpenAI(
            base_url=endpoint + "/openai/v1/",
            api_key=api_key,
        )

    def _format_evidence_prompt(
        self,
        task_dict: Dict,
        batch_sentences: List[Dict],
        evidence_formatted: str,
        initial_selection: str = None,
    ) -> str:
        """Format evidence classification prompt with variables."""
        prompt = self.evidence_prompt

        # Replace template variables
        prompt = prompt.replace(
            "{patient_narrative}", task_dict.get("patient_narrative", "")
        )
        prompt = prompt.replace(
            "{clinician_question}", task_dict.get("clinician_question", "")
        )
        prompt = prompt.replace("{evidence_list}", evidence_formatted)
        prompt = prompt.replace("{evidence_count}", str(len(batch_sentences)))

        # Handle optional initial_selection for refinement prompts
        if initial_selection is not None:
            prompt = prompt.replace("{initial_selection}", initial_selection)

        return prompt

    def _generate_classification_sample(
        self, task_dict: Dict, batch_sentences: List[Dict], evidence_formatted: str
    ) -> Dict:
        """
        Generate a single classification sample using Pattern 1 (ID→label dict).

        Returns dict format: {"sentence_evidence_dict": {"1": "ESSENTIAL", ...}} (converted from list internally)
        """

        # Format the evidence classification prompt
        evidence_prompt = self._format_evidence_prompt(
            task_dict, batch_sentences, evidence_formatted
        )

        expected_ids = {
            str(s.get("sentence_id", idx + 1)) for idx, s in enumerate(batch_sentences)
        }
        case_id = task_dict.get("case_id", "unknown")

        logger.debug(
            f"[case {case_id}] Starting classification sample generation. Expected {len(expected_ids)} sentence IDs"
        )

        # Define API call function
        def make_api_call():
            return self.client.responses.parse(
                model=self.model_name,
                input=evidence_prompt,
                text_format=qa_response.SentenceEvidenceDict,
                **self.reasoning_params
            )

        # Define validator function
        def validate_response(response):
            # Parse response to dict
            parsed_result = response.output_parsed
            sentence_evidence_dict = {
                str(item.sentence_id): item.relevance
                for item in parsed_result.sentence_evidence_list
            }
            result_dict = {
                "sentence_evidence_dict": sentence_evidence_dict,
                "reasoning": parsed_result.reasoning,
            }

            # Store in nonlocal for fallback if needed
            nonlocal last_result
            last_result = result_dict

            # Validate IDs
            actual_ids = set(result_dict["sentence_evidence_dict"].keys())
            if expected_ids == actual_ids:
                return True, None  # Valid!

            # Build error message for correction
            missing_ids = expected_ids - actual_ids
            extra_ids = actual_ids - expected_ids
            error_msg = f"Missing sentence IDs: {missing_ids}. Extra IDs: {extra_ids}. Please provide sentence_evidence_list with all required sentence numbers and their relevance labels."
            return False, error_msg

        # Define correction builder function
        def build_correction(response_id, error_msg):
            def correction_call():
                return self.client.responses.parse(
                    model=self.model_name,
                    previous_response_id=response_id,
                    input=error_msg,
                    text_format=qa_response.SentenceEvidenceDict,
                    **self.reasoning_params
                )

            return correction_call

        # Use retry logic
        last_result = None
        try:
            response = call_with_retry(
                api_call=make_api_call,
                validator=validate_response,
                correction_builder=build_correction,
                config=RetryConfig(max_retries=self.max_retries),
                case_id=case_id,
            )
            # Parse final valid response
            parsed_result = response.output_parsed
            sentence_evidence_dict = {
                str(item.sentence_id): item.relevance
                for item in parsed_result.sentence_evidence_list
            }
            return {
                "sentence_evidence_dict": sentence_evidence_dict,
                "reasoning": parsed_result.reasoning,
            }
        except RuntimeError as e:
            # Max retries exceeded - return best effort result
            logger.error(f"[case {case_id}] {e}")
            if last_result and "sentence_evidence_dict" in last_result:
                missing_count = len(
                    expected_ids - set(last_result["sentence_evidence_dict"].keys())
                )
                if missing_count > 0:
                    logger.warning(
                        f"[case {case_id}] Filling {missing_count} missing IDs with NOT_RELEVANT"
                    )
                    for missing_id in expected_ids - set(
                        last_result["sentence_evidence_dict"].keys()
                    ):
                        last_result["sentence_evidence_dict"][missing_id] = (
                            qa_response.RelevanceCategory.NOT_RELEVANT.value
                        )
                return last_result
            else:
                logger.warning(
                    f"[case {case_id}] No valid result generated, creating default classification with all NOT_RELEVANT"
                )
                return {
                    "sentence_evidence_dict": {
                        id: qa_response.RelevanceCategory.NOT_RELEVANT.value
                        for id in expected_ids
                    },
                    "reasoning": "Failed to generate valid classification",
                }

    def _aggregate_samples(self, samples: List[Dict]) -> Dict:
        """
        Perform majority voting across samples for each sentence ID.

        Args:
            samples: List of classification results (each with sentence_evidence_dict)

        Returns:
            Aggregated result with most common label per sentence ID
        """
        if not samples:
            return {"sentence_evidence_dict": {}, "reasoning": "No samples generated"}

        # Get all sentence IDs from first sample
        sentence_ids = list(samples[0]["sentence_evidence_dict"].keys())
        aggregated_dict = {}
        vote_counts = {}

        # Majority vote per sentence ID
        for sentence_id in sentence_ids:
            # Collect all labels for this ID across samples
            labels = [
                sample["sentence_evidence_dict"].get(
                    sentence_id, qa_response.RelevanceCategory.NOT_RELEVANT.value
                )
                for sample in samples
            ]

            # Get most common label
            counter = Counter(labels)
            most_common_label = counter.most_common(1)[0][0]

            aggregated_dict[sentence_id] = most_common_label
            vote_counts[sentence_id] = dict(counter)  # Store vote distribution

        # Calculate and log agreement statistics
        if self.num_samples > 1:
            k = self.num_samples
            unanimous = 0  # All k samples agree
            high_agreement = 0  # k-1 or k samples agree
            split_decisions = 0  # Less than k-1 agreement
            disagreements_by_label = {}  # Track which labels had disagreements

            for sentence_id, counter_dict in vote_counts.items():
                max_votes = max(counter_dict.values())

                if max_votes == k:
                    unanimous += 1
                elif max_votes >= k - 1:
                    high_agreement += 1
                else:
                    split_decisions += 1
                    # Track disagreement details
                    label = aggregated_dict[sentence_id]
                    if label not in disagreements_by_label:
                        disagreements_by_label[label] = []
                    disagreements_by_label[label].append(
                        f"ID {sentence_id}: {dict(counter_dict)}"
                    )

            total = len(sentence_ids)
            unanimous_pct = (unanimous / total * 100) if total > 0 else 0
            high_agreement_pct = (high_agreement / total * 100) if total > 0 else 0
            split_pct = (split_decisions / total * 100) if total > 0 else 0

            logger.debug(
                f"Self-consistency agreement (k={k}, n={total}): "
                f"Unanimous: {unanimous}/{total} ({unanimous_pct:.1f}%), "
                f"High agreement (≥{k - 1}): {high_agreement}/{total} ({high_agreement_pct:.1f}%), "
                f"Split decisions: {split_decisions}/{total} ({split_pct:.1f}%)"
            )

            # Log disagreement details if any
            if disagreements_by_label:
                logger.debug("Disagreements by majority label:")
                for label, examples in disagreements_by_label.items():
                    logger.debug(f"  {label}: {len(examples)} cases")
                    for ex in examples[:3]:  # Show first 3 examples
                        logger.debug(f"    {ex}")

        return {
            "sentence_evidence_dict": aggregated_dict,  # Dict: {"1": "ESSENTIAL", ...}
            "reasoning": samples[0].get(
                "reasoning", ""
            ),  # Use first sample's reasoning
            "samples": samples if self.num_samples > 1 else None,  # Store if k>1
            "vote_counts": vote_counts
            if self.num_samples > 1
            else None,  # Vote distribution
        }

    def _dict_to_array(self, sentence_dict: Dict[str, str]) -> List[str]:
        """Convert dict format to array for backward compatibility."""
        # Sort by sentence ID and extract labels in order
        sorted_ids = sorted(sentence_dict.keys(), key=lambda x: int(x))
        return [sentence_dict[id] for id in sorted_ids]

    def _generate_answer(
        self, prompt: str, task_dict: Dict, evidence_classification_pred_dict: Dict
    ) -> Dict:
        """
        Generate answer with automatic validation and retry using previous_response_id.

        Similar to _generate_classification_sample, this method handles:
        - Initial generation
        - Validation (citation coverage, length check)
        - Automatic retry with conversational correction if validation fails

        Args:
            prompt: Initial QA prompt
            task_dict: Task dictionary for validation
            evidence_classification_pred_dict: Evidence classification for citation validation

        Returns:
            Dict with validated answer (reasoning, final_answer) and retry history
        """

        case_id = task_dict.get("case_id", "unknown")
        answer_history = []

        # Define API call function
        def make_api_call():
            return self.client.responses.parse(
                model=self.model_name,
                input=prompt,
                text_format=qa_response.QAResponse,
                **self.reasoning_params
            )

        # Define validator function
        def validate_response(response):
            parsed_result = response.output_parsed
            result = {
                "reasoning": parsed_result.reasoning,
                "final_answer": parsed_result.final_answer,
            }

            # Validate answer
            answer_evidence_list, answer_word_count = self.get_valid_citations(
                task_dict, result
            )

            answer_citation_coverage, citation_detailed_issue = (
                self.check_answer_citation_coverage(
                    evidence_classification_pred_dict, answer_evidence_list
                )
            )
            # Skip word count check if rewrite step will handle it
            answer_length_check = True if self.rewrite_prompt else self.check_answer_word_count(answer_word_count)

            # Check if validation passed
            if answer_citation_coverage and answer_length_check:
                return True, None

            # Build error message for correction
            issue_list = []
            if not answer_citation_coverage:
                issue_list.append(f"Citation issues: {citation_detailed_issue}")
            if not answer_length_check:
                issue_list.append(
                    f"Answer is too long: {answer_word_count} words (limit: {self.max_answer_words}). Please shorten."
                )

            issue_str = "\n".join(issue_list)

            # Save to history for debugging
            result["issue"] = issue_str
            answer_history.append(result.copy())

            return False, f"Please fix the following issues:\n{issue_str}"

        # Define correction builder function
        def build_correction(response_id, error_msg):
            def correction_call():
                return self.client.responses.parse(
                    model=self.model_name,
                    previous_response_id=response_id,
                    input=error_msg,
                    text_format=qa_response.QAResponse,
                    **self.reasoning_params
                )

            return correction_call

        # Use retry logic
        response = call_with_retry(
            api_call=make_api_call,
            validator=validate_response,
            correction_builder=build_correction,
            config=RetryConfig(max_retries=self.max_retries),
            case_id=case_id,
        )

        # Parse final valid response
        parsed_result = response.output_parsed
        result = {
            "reasoning": parsed_result.reasoning,
            "final_answer": parsed_result.final_answer,
            "answer_history": answer_history if answer_history else None,
            "response_id": response.id,
        }
        return result

    def classify_evidence(
        self,
        task_dict: Dict,
        fail_count: int = 0,
    ):
        """
        Evidence classification using Self-Consistency with k samples.

        Returns dict with evidence_relevance_list for backward compatibility.
        """
        sentences = task_dict["sentences"]
        total_sentences = len(sentences)

        all_batch_results = []
        # Handle "use_all" as a special value for batch_size
        if self.evidence_batch_size == "use_all":
            batch_size = total_sentences
        else:
            batch_size = int(self.evidence_batch_size)

        start_idx = 0
        while start_idx < total_sentences:
            end_idx = min(start_idx + batch_size, total_sentences)
            batch_sentences = sentences[start_idx:end_idx]

            # Format batch sentences as numbered list strings
            if "sentence_id" in batch_sentences[0]:
                evidence_formatted = "\n".join(
                    f"{s['sentence_id']}: {s['text']}" for s in batch_sentences
                )
                batch_sentence_ids = [str(s["sentence_id"]) for s in batch_sentences]
            else:
                evidence_formatted = "\n".join(
                    f"{start_idx + i + 1}: {s['text']}"
                    for i, s in enumerate(batch_sentences)
                )
                batch_sentence_ids = [
                    str(start_idx + i + 1) for i in range(len(batch_sentences))
                ]

            # Generate k independent samples using Self-Consistency
            samples = []
            logger.debug(
                f"[case {task_dict['case_id']}] Generating {self.num_samples} samples for batch (sentences {start_idx + 1}-{end_idx})"
            )
            for sample_idx in range(self.num_samples):
                try:
                    logger.debug(
                        f"[case {task_dict['case_id']}] Generating sample {sample_idx + 1}/{self.num_samples}"
                    )
                    sample = self._generate_classification_sample(
                        task_dict, batch_sentences, evidence_formatted
                    )
                    samples.append(sample)
                except Exception as e:
                    logger.warning(
                        f"[case {task_dict['case_id']}] Error generating classification sample {sample_idx + 1}/{self.num_samples}: {type(e).__name__}: {e}"
                    )
                    # Continue with samples we have

            if not samples:
                logger.error(
                    f"[case {task_dict['case_id']}] Failed to generate any samples for batch (sentences {start_idx + 1}-{end_idx}). "
                    f"Reducing batch_size from {batch_size} to {max(2, int(batch_size / 2))}"
                )
                batch_size = max(2, int(batch_size / 2))
                fail_count += 1
                self.check_fail_count(
                    fail_count,
                    task_dict,
                    f"evidence classification for sentences {start_idx + 1}-{end_idx}",
                )
                continue

            # Aggregate samples via majority voting
            logger.debug(
                f"[case {task_dict['case_id']}] Aggregating {len(samples)} samples for batch"
            )
            aggregated = self._aggregate_samples(samples)

            # Validate: check if we got labels for all sentences in batch
            response_sentence_ids = list(aggregated["sentence_evidence_dict"].keys())

            passed_checks = False
            if len(response_sentence_ids) == len(batch_sentence_ids):
                if compare(batch_sentence_ids, response_sentence_ids):
                    logger.debug(
                        f"[case {task_dict['case_id']}] Batch validation passed for sentences {start_idx + 1}-{end_idx}"
                    )
                    all_batch_results.append(aggregated)
                    start_idx += batch_size - self.evidence_batch_overlap
                    passed_checks = True

            if not passed_checks:
                logger.warning(
                    f"[case {task_dict['case_id']}] Batch validation failed for sentences {start_idx + 1}-{end_idx}. "
                    f"Expected {len(batch_sentence_ids)} IDs, got {len(response_sentence_ids)}. "
                    f"Reducing batch_size from {batch_size} to {max(2, int(batch_size / 2))}"
                )
                batch_size = max(2, int(batch_size / 2))
                fail_count += 1
                self.check_fail_count(
                    fail_count,
                    task_dict,
                    f"evidence classification batch validation for sentences {start_idx + 1}-{end_idx}",
                )

        # Combine all batch results
        classification_dict = {}

        # Merge all sentence_evidence_dict from batches
        merged_sentence_dict = {}
        for batch_result in all_batch_results:
            merged_sentence_dict.update(batch_result["sentence_evidence_dict"])

        # Convert dict→array for backward compatibility with benchmark.py
        classification_dict["evidence_relevance_list"] = self._dict_to_array(
            merged_sentence_dict
        )

        # Convert string labels to RelevanceCategory enum
        classification_dict["evidence_relevance_list"] = [
            qa_response.RelevanceCategory(label) if isinstance(label, str) else label
            for label in classification_dict["evidence_relevance_list"]
        ]

        classification_dict["batch_results"] = all_batch_results
        classification_dict["sentence_evidence_dict"] = merged_sentence_dict

        return classification_dict

    def _rewrite_answer(self, answer_dict, task_dict):
        """Rewrite an answer for stylistic alignment using previous_response_id chaining.

        The model already has full context (question, evidence, reasoning, answer)
        from the original generation. Only the rewrite prompt is sent as new input.

        Args:
            answer_dict: Dict with 'final_answer', 'reasoning', 'response_id'
            task_dict: Task dict (for case_id logging)

        Returns:
            Updated answer_dict with rewritten answer, or original on failure.
        """
        case_id = task_dict.get("case_id", "unknown")
        original_response_id = answer_dict.get("response_id")

        if not original_response_id:
            logger.warning(f"[case {case_id}] No response_id available, skipping rewrite")
            return answer_dict

        logger.info(f"[case {case_id}] Rewriting answer for stylistic alignment")

        answer_history = []

        # Define API call — chains from original generation
        def make_api_call():
            return self.client.responses.parse(
                model=self.model_name,
                previous_response_id=original_response_id,
                input=self.rewrite_prompt,
                text_format=qa_response.QAResponse,
                **self.reasoning_params,
            )

        # Define validator — enforce word count in rewrite step
        def validate_response(response):
            parsed_result = response.output_parsed
            result = {
                "reasoning": parsed_result.reasoning,
                "final_answer": parsed_result.final_answer,
            }

            _, answer_word_count = self.get_valid_citations(task_dict, result)
            answer_length_check = self.check_answer_word_count(answer_word_count)

            if answer_length_check:
                return True, None

            error_msg = (
                f"Rewritten answer is too long: {answer_word_count} words "
                f"(limit: {self.max_answer_words}). Please shorten."
            )
            result["issue"] = error_msg
            answer_history.append(result.copy())
            return False, error_msg

        # Define correction builder for retries
        def build_correction(response_id, error_msg):
            def correction_call():
                return self.client.responses.parse(
                    model=self.model_name,
                    previous_response_id=response_id,
                    input=error_msg,
                    text_format=qa_response.QAResponse,
                    **self.reasoning_params,
                )
            return correction_call

        try:
            response = call_with_retry(
                api_call=make_api_call,
                validator=validate_response,
                correction_builder=build_correction,
                config=RetryConfig(max_retries=self.max_retries),
                case_id=case_id,
            )

            parsed_result = response.output_parsed
            logger.info(f"[case {case_id}] Answer rewrite successful")

            answer_dict["original_answer"] = answer_dict["final_answer"]
            answer_dict["final_answer"] = parsed_result.final_answer
            answer_dict["rewrite_reasoning"] = parsed_result.reasoning
            answer_dict["rewrite_history"] = answer_history if answer_history else None
            answer_dict["response_id"] = response.id

        except Exception as e:
            logger.error(
                f"[case {case_id}] Rewrite failed, keeping original answer: {e}"
            )

        return answer_dict

    def answer(self, task_dict: Dict, fail_count: int = 0, **kwargs):
        evidence_classification_pred_dict = self.classify_evidence(
            task_dict, fail_count
        )

        evidence_coveraged_reached = self.validate_evidence_coverage(
            task_dict, evidence_classification_pred_dict
        )
        if not evidence_coveraged_reached:
            # when the number of evidence is not equal to the number of sentences
            logger.warning(
                f"[case {task_dict['case_id']}] evidence count mismatch: {len(evidence_classification_pred_dict['evidence_relevance_list'])} != {len(task_dict['sentences'])}"
            )
            fail_count = fail_count + 1
            # should not happen
            raise ValueError(
                f"Evidence count mismatch: {len(evidence_classification_pred_dict['evidence_relevance_list'])} != {len(task_dict['sentences'])}"
            )

        essential_evidence = [
            str(idx + 1) + ": " + task_dict["sentences"][idx]["text"]
            for idx, e in enumerate(
                evidence_classification_pred_dict["evidence_relevance_list"]
            )
            if e == qa_response.RelevanceCategory.ESSENTIAL
        ]
        essential_evidence_str = "\n".join(essential_evidence)

        qa_prompt_input = {
            "patient_narrative": task_dict["patient_narrative"],
            "clinician_question": task_dict["clinician_question"],
            "essential_evidence": essential_evidence_str,
        }

        if self.include_supplementary:
            supplementary_evidence = [
                str(idx + 1) + ": " + task_dict["sentences"][idx]["text"]
                for idx, e in enumerate(
                    evidence_classification_pred_dict["evidence_relevance_list"]
                )
                if e == qa_response.RelevanceCategory.SUPPLEMENTARY
            ]
            supplementary_evidence_str = "\n".join(supplementary_evidence)

            qa_prompt_input["supplementary_evidence"] = (
                supplementary_evidence_str  # Add supplementary evidence to the prompt
            )

        # Format QA prompt using string formatting (no LangChain)
        qa_prompt = self.qa_prompt.format(**qa_prompt_input)

        # Generate answer with automatic validation and retry
        answer_response_dict = self._generate_answer(
            qa_prompt, task_dict, evidence_classification_pred_dict
        )

        # Optional rewrite step for stylistic alignment
        if self.rewrite_prompt:
            answer_response_dict = self._rewrite_answer(answer_response_dict, task_dict)

        out_dict = {
            "case_id": task_dict["case_id"],
            "evidence_classification": evidence_classification_pred_dict,
            "answer_history": answer_response_dict.pop("answer_history", []),
            "answer_generation": answer_response_dict,
        }

        return out_dict


class MinimalSufficiencyMethod(GroundedQA):
    """
    Minimal Sufficiency variant: Identifies only essential evidence (minimal set).

    Differs from base GroundedQA in response format:
    - Expects: essential_sentence_ids (list of IDs that are essential)
    - Returns: evidence_relevance_list (ESSENTIAL or NOT_RELEVANT for each sentence)

    Uses same Self-Consistency and Pattern 1 approach as base class.
    """

    def _convert_ids_to_relevance_list(
        self, essential_ids: List[str], total_sentences: int
    ) -> List[qa_response.RelevanceCategory]:
        """
        Convert minimal sufficiency IDs to relevance list.

        Args:
            essential_ids: List of sentence IDs marked as essential
            total_sentences: Total number of sentences

        Returns:
            List of ESSENTIAL or NOT_RELEVANT for each sentence
        """
        essential_ids_set = {str(id) for id in essential_ids}

        relevance_list = []
        for idx in range(total_sentences):
            sentence_id = str(idx + 1)
            if sentence_id in essential_ids_set:
                relevance_list.append(qa_response.RelevanceCategory.ESSENTIAL)
            else:
                relevance_list.append(qa_response.RelevanceCategory.NOT_RELEVANT)

        return relevance_list

    def classify_evidence(self, task_dict: Dict, fail_count: int = 0) -> Dict:
        """
        Override: Handles minimal sufficiency response format.

        Expects response with essential_sentence_ids, converts to evidence_relevance_list.
        """
        # Call parent's classify_evidence to get base classification
        # (This works if the prompt returns standard format)
        try:
            response_dict = super().classify_evidence(task_dict, fail_count)

            # Check if response has essential_sentence_ids format
            if "essential_sentence_ids" in response_dict:
                # Convert IDs to relevance list
                total_sentences = len(task_dict["sentences"])
                relevance_list = self._convert_ids_to_relevance_list(
                    response_dict["essential_sentence_ids"], total_sentences
                )
                response_dict["evidence_relevance_list"] = relevance_list

            return response_dict

        except Exception as e:
            logger.error(f"Error in MinimalSufficiencyMethod.classify_evidence: {e}")
            raise


class AnswerFirstMethod(GroundedQA):
    """
    Answer-First variant: Generates answer first, then identifies supporting evidence.

    Differs from base GroundedQA in pipeline order:
    - Base: evidence → answer
    - This: answer → evidence

    Additional parameter:
    - k_candidates: Number of answer candidates to generate (default 1)
    """

    def __init__(self, k_candidates: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.k_candidates = k_candidates

    def _generate_answer_from_all_evidence(self, task_dict: Dict) -> Dict:
        """
        Generate answer using all available evidence with retry/correction logic.

        Uses basic validation (word count) since we don't have evidence classification yet.
        Full citation validation happens after evidence classification in step 2.
        """
        case_id = task_dict.get("case_id", "unknown")
        logger.info(f"[case {case_id}] Generating answer from all evidence")

        # Format all evidence
        all_evidence = [
            f"{idx + 1}: {s['text']}" for idx, s in enumerate(task_dict["sentences"])
        ]
        all_evidence_str = "\n".join(all_evidence)

        # Format QA prompt
        qa_prompt_input = {
            "patient_narrative": task_dict.get("patient_narrative", ""),
            "clinician_question": task_dict.get("clinician_question", ""),
            "all_evidence": all_evidence_str,
        }

        # Format QA prompt using string formatting
        qa_prompt = self.qa_prompt.format(**qa_prompt_input)

        answer_history = []

        # Define API call function
        def make_api_call():
            return self.client.responses.parse(
                model=self.model_name,
                input=qa_prompt,
                text_format=qa_response.QAResponse,
                **self.reasoning_params
            )

        # Define validator function (basic validation only)
        def validate_response(response):
            parsed_result = response.output_parsed
            result = {
                "reasoning": parsed_result.reasoning,
                "final_answer": parsed_result.final_answer,
            }

            # Basic validation: check word count only
            # (Citation validation requires evidence classification, which we don't have yet)
            # Skip word count check if rewrite step will handle it
            if self.rewrite_prompt:
                return True, None

            _, answer_word_count = self.get_valid_citations(task_dict, result)
            answer_length_check = self.check_answer_word_count(answer_word_count)

            if answer_length_check:
                return True, None

            # Build error message for correction
            error_msg = f"Answer is too long: {answer_word_count} words (limit: {self.max_answer_words}). Please shorten your answer."

            # Save to history
            result["issue"] = error_msg
            answer_history.append(result.copy())

            return False, error_msg

        # Define correction builder function
        def build_correction(response_id, error_msg):
            def correction_call():
                return self.client.responses.parse(
                    model=self.model_name,
                    previous_response_id=response_id,
                    input=error_msg,
                    text_format=qa_response.QAResponse,
                    **self.reasoning_params
                )
            return correction_call

        # Use retry logic
        response = call_with_retry(
            api_call=make_api_call,
            validator=validate_response,
            correction_builder=build_correction,
            config=RetryConfig(max_retries=self.max_retries),
            case_id=case_id,
        )

        # Parse final response
        parsed_result = response.output_parsed
        result = {
            "reasoning": parsed_result.reasoning,
            "final_answer": parsed_result.final_answer,
            "answer_history": answer_history if answer_history else None,
            "response_id": response.id,
        }

        logger.info(f"[case {case_id}] Successfully generated answer")
        return result

    def _classify_evidence_for_answers(
        self, task_dict: Dict, answer_responses: List[Dict]
    ) -> Dict:
        """
        Classify evidence based on k generated answers.

        Uses the answer-first evidence prompt which expects:
        - k_candidates: number of answer candidates
        - generated_answers: formatted string of the k answers
        - evidence_list: numbered sentences

        Returns evidence classification in dict format (1-1 sentence mapping).

        Args:
            task_dict: Task dictionary with sentences
            answer_responses: List of k answer dicts (each with "final_answer" and "reasoning")

        Returns:
            Evidence classification dict with sentence_evidence_dict
        """
        case_id = task_dict.get("case_id", "unknown")
        logger.info(
            f"[case {case_id}] Classifying evidence using {len(answer_responses)} generated answers"
        )

        # Format the k generated answers for the prompt
        formatted_answers = []
        for i, answer_resp in enumerate(answer_responses):
            formatted_answers.append(
                f"**Answer Candidate {i+1}:**\n{answer_resp['final_answer']}"
            )
        generated_answers_str = "\n\n".join(formatted_answers)

        # Format evidence list (numbered sentences)
        evidence_list = [
            f"{idx + 1}: {s['text']}" for idx, s in enumerate(task_dict["sentences"])
        ]
        evidence_formatted = "\n".join(evidence_list)

        # Build the evidence prompt with answer-first template
        evidence_prompt = self.evidence_prompt.replace(
            "{k_candidates}", str(len(answer_responses))
        )
        evidence_prompt = evidence_prompt.replace(
            "{generated_answers}", generated_answers_str
        )
        evidence_prompt = evidence_prompt.replace(
            "{clinician_question}", task_dict.get("clinician_question", "")
        )
        evidence_prompt = evidence_prompt.replace("{evidence_list}", evidence_formatted)
        evidence_prompt = evidence_prompt.replace(
            "{evidence_count}", str(len(task_dict["sentences"]))
        )

        expected_count = len(task_dict["sentences"])

        logger.debug(
            f"[case {case_id}] Calling evidence classifier (expecting {expected_count} labels)"
        )

        expected_ids = {
            str(s.get("sentence_id", idx + 1)) for idx, s in enumerate(task_dict["sentences"])
        }

        # Define API call function
        def make_api_call():
            return self.client.responses.parse(
                model=self.model_name,
                input=evidence_prompt,
                text_format=qa_response.SentenceEvidenceDict,
                **self.reasoning_params
            )

        # Define validator function
        def validate_response(response):
            parsed_result = response.output_parsed

            # Handle None response from API
            if parsed_result is None:
                return False, "API returned None. Please provide a valid JSON response with reasoning and sentence_evidence_list."

            sentence_evidence_dict = {
                str(item.sentence_id): item.relevance
                for item in parsed_result.sentence_evidence_list
            }

            # Validate IDs
            actual_ids = set(sentence_evidence_dict.keys())
            if expected_ids == actual_ids:
                return True, None  # Valid!

            # Build error message for correction
            missing_ids = expected_ids - actual_ids
            extra_ids = actual_ids - expected_ids
            error_msg = f"Missing sentence IDs: {missing_ids}. Extra IDs: {extra_ids}. Please provide sentence_evidence_list with all required sentence numbers and their relevance labels."
            return False, error_msg

        # Define correction builder function
        def build_correction(response_id, error_msg):
            def correction_call():
                return self.client.responses.parse(
                    model=self.model_name,
                    previous_response_id=response_id,
                    input=error_msg,
                    text_format=qa_response.SentenceEvidenceDict,
                    **self.reasoning_params
                )
            return correction_call

        # Use retry logic
        response = call_with_retry(
            api_call=make_api_call,
            validator=validate_response,
            correction_builder=build_correction,
            config=RetryConfig(max_retries=self.max_retries),
            case_id=case_id,
        )

        # Parse response
        parsed_result = response.output_parsed
        sentence_evidence_dict = {
            str(item.sentence_id): item.relevance
            for item in parsed_result.sentence_evidence_list
        }

        result = {
            "sentence_evidence_dict": sentence_evidence_dict,
            "reasoning": parsed_result.reasoning,
        }

        logger.info(
            f"[case {case_id}] Evidence classification completed: "
            f"{sum(1 for v in sentence_evidence_dict.values() if v == 'Essential')} Essential, "
            f"{sum(1 for v in sentence_evidence_dict.values() if v == 'Supplementary')} Supplementary, "
            f"{sum(1 for v in sentence_evidence_dict.values() if v == 'Not Relevant')} Not Relevant"
        )

        return result

    def answer(self, task_dict: Dict, fail_count: int = 0, **kwargs) -> Dict:
        """
        Override: Answer-first pipeline (generate answer → classify evidence).

        Steps:
        1. Generate k answer candidates from all evidence
        2. Classify evidence based on what supports those answers
        """
        case_id = task_dict.get("case_id", "unknown")
        logger.info(
            f"[case {case_id}] Starting answer-first pipeline with {self.k_candidates} candidates"
        )

        # Step 1: Generate k answers from all evidence
        logger.info(f"[case {case_id}] Step 1: Generating {self.k_candidates} answer candidates")
        answer_responses = []
        for i in range(self.k_candidates):
            try:
                logger.debug(f"[case {case_id}] Generating candidate {i+1}/{self.k_candidates}")
                answer_response = self._generate_answer_from_all_evidence(task_dict)
                answer_responses.append(answer_response)
            except Exception as e:
                logger.warning(f"[case {case_id}] Error generating answer candidate {i+1}: {e}")

        if not answer_responses:
            logger.error(
                f"[case {case_id}] Failed to generate any answer candidates"
            )
            raise ValueError("Failed to generate any answer candidates")

        logger.info(
            f"[case {case_id}] Successfully generated {len(answer_responses)}/{self.k_candidates} answer candidates"
        )

        # Step 2: Classify evidence based on generated answers
        logger.info(f"[case {case_id}] Step 2: Classifying evidence based on generated answers")
        evidence_classification = self._classify_evidence_for_answers(task_dict, answer_responses)

        # Convert dict→array for backward compatibility with benchmark.py
        evidence_classification["evidence_relevance_list"] = self._dict_to_array(
            evidence_classification["sentence_evidence_dict"]
        )

        # Convert string labels to RelevanceCategory enum
        evidence_classification["evidence_relevance_list"] = [
            qa_response.RelevanceCategory(label) if isinstance(label, str) else label
            for label in evidence_classification["evidence_relevance_list"]
        ]

        # Optional rewrite step for stylistic alignment (on primary answer only)
        if self.rewrite_prompt:
            answer_responses[0] = self._rewrite_answer(answer_responses[0], task_dict)

        logger.info(f"[case {case_id}] Answer-first pipeline completed successfully")

        return {
            "case_id": task_dict["case_id"],
            "evidence_classification": evidence_classification,
            "answer_history": answer_responses,  # All k candidates
            "answer_generation": answer_responses[0],  # Best answer
        }


class AnswerEvidenceAlignment:
    """
    Subtask 4: Answer-Evidence Alignment.

    For each sentence in a pre-written reference answer, identifies the note sentences
    that directly support it. Input: task_dict must include 'answer_sentences' (list of
    dicts with 'sentence_id' and 'text') in addition to the usual 'sentences' and questions.
    """

    def __init__(
        self,
        alignment_prompt_file_path: str,
        model_name: str = "gpt-4o-mini",
        reasoning_effort: str = None,
        max_retries: int = 5,
        num_samples: int = 1,
        **kwargs,
    ):
        with open(alignment_prompt_file_path, "r") as f:
            self.alignment_prompt = f.read()

        self.model_name = model_name
        self.max_retries = max_retries
        self.num_samples = num_samples
        self.reasoning_effort = reasoning_effort

        self.reasoning_params = (
            {"reasoning": {"effort": reasoning_effort, "summary": "auto"}}
            if reasoning_effort
            else {}
        )

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")

        self.client = OpenAI(
            base_url=endpoint + "/openai/v1/",
            api_key=api_key,
        )

    def _generate_single_alignment(self, prompt, expected_answer_ids, case_id):
        """Generate a single alignment response via API with retry."""
        def make_api_call():
            return self.client.responses.parse(
                model=self.model_name,
                input=prompt,
                text_format=qa_response.AnswerEvidenceAlignmentResponse,
                **self.reasoning_params,
            )

        def validate_response(response):
            parsed = response.output_parsed
            if parsed is None:
                return False, "API returned None. Please provide a valid JSON response."

            actual_ids = {item.answer_id for item in parsed.alignments}
            if expected_answer_ids == actual_ids:
                return True, None

            missing = expected_answer_ids - actual_ids
            extra = actual_ids - expected_answer_ids
            error_msg = (
                f"Missing answer IDs: {missing}. Extra IDs: {extra}. "
                "Please include every answer sentence ID in the alignments list."
            )
            return False, error_msg

        def build_correction(response_id, error_msg):
            def correction_call():
                return self.client.responses.parse(
                    model=self.model_name,
                    previous_response_id=response_id,
                    input=error_msg,
                    text_format=qa_response.AnswerEvidenceAlignmentResponse,
                    **self.reasoning_params,
                )
            return correction_call

        response = call_with_retry(
            api_call=make_api_call,
            validator=validate_response,
            correction_builder=build_correction,
            config=RetryConfig(max_retries=self.max_retries),
            case_id=case_id,
        )
        parsed = response.output_parsed
        alignments = [
            {"answer_id": item.answer_id, "evidence_id": item.evidence_id}
            for item in parsed.alignments
        ]
        alignments.sort(key=lambda x: int(x["answer_id"]))
        return alignments, parsed.reasoning

    def _aggregate_alignment_samples(self, samples, case_id):
        """Majority vote on (answer_id, evidence_id) pairs across N samples."""
        threshold = len(samples) / 2  # strict majority: > N/2

        # Collect all answer_ids from first sample
        all_answer_ids = {a["answer_id"] for a in samples[0]}

        aggregated = []
        for answer_id in sorted(all_answer_ids, key=int):
            # Count how many samples include each evidence_id for this answer_id
            evidence_counter = Counter()
            for sample in samples:
                for alignment in sample:
                    if alignment["answer_id"] == answer_id:
                        for eid in alignment["evidence_id"]:
                            evidence_counter[eid] += 1

            # Keep evidence_ids that appear in majority of samples
            majority_evidence = [
                eid for eid, count in evidence_counter.items()
                if count > threshold
            ]
            aggregated.append({
                "answer_id": answer_id,
                "evidence_id": sorted(majority_evidence, key=int) if majority_evidence else []
            })

        # Log agreement stats
        all_pairs = set()
        for sample in samples:
            for a in sample:
                for eid in a["evidence_id"]:
                    all_pairs.add((a["answer_id"], eid))
        unanimous = sum(
            1 for pair in all_pairs
            if all(
                pair[1] in next(
                    (a["evidence_id"] for a in sample if a["answer_id"] == pair[0]), []
                )
                for sample in samples
            )
        )
        logger.debug(
            f"[case {case_id}] Self-consistency (k={len(samples)}): "
            f"{len(all_pairs)} unique pairs, {unanimous} unanimous, "
            f"{sum(len(a['evidence_id']) for a in aggregated)} after majority vote"
        )

        return aggregated

    def answer(self, task_dict: Dict, **kwargs) -> Dict:
        case_id = task_dict.get("case_id", "unknown")
        answer_sentences = task_dict.get("answer_sentences", [])

        if not answer_sentences:
            raise ValueError(
                f"[case {case_id}] No answer_sentences in task_dict. "
                "Subtask 4 requires pre-written answer sentences to align."
            )

        # Format answer sentences as numbered list
        answer_formatted = "\n".join(
            f"{s['sentence_id']}: {s['text']}" for s in answer_sentences
        )
        expected_answer_ids = {str(s["sentence_id"]) for s in answer_sentences}

        # Format note sentences as numbered list
        note_sentences = task_dict.get("sentences", [])
        evidence_formatted = "\n".join(
            f"{s['sentence_id']}: {s['text']}" for s in note_sentences
        )

        # Build the prompt
        prompt = self.alignment_prompt.format(
            patient_narrative=task_dict.get("patient_narrative", ""),
            clinician_question=task_dict.get("clinician_question", ""),
            answer_sentences=answer_formatted,
            evidence_list=evidence_formatted,
            answer_count=len(answer_sentences),
        )

        logger.debug(
            f"[case {case_id}] Running answer-evidence alignment for "
            f"{len(answer_sentences)} answer sentences (num_samples={self.num_samples})"
        )

        try:
            # Generate num_samples independent alignment responses
            samples = []
            for sample_idx in range(self.num_samples):
                if self.num_samples > 1:
                    logger.debug(
                        f"[case {case_id}] Generating sample {sample_idx + 1}/{self.num_samples}"
                    )
                alignments, reasoning = self._generate_single_alignment(
                    prompt, expected_answer_ids, case_id
                )
                samples.append(alignments)

            # Aggregate via majority vote if multiple samples
            if self.num_samples > 1:
                final_alignments = self._aggregate_alignment_samples(samples, case_id)
                reasoning_note = f"[Aggregated from {len(samples)} samples via majority vote] {reasoning}"
            else:
                final_alignments = samples[0]
                reasoning_note = reasoning

            logger.debug(f"[case {case_id}] Alignment completed for {len(final_alignments)} answer sentences")
            result = {
                "case_id": case_id,
                "alignments": final_alignments,
                "reasoning": reasoning_note,
            }
            if self.num_samples > 1:
                result["raw_samples"] = samples
            return result
        except RuntimeError as e:
            logger.error(f"[case {case_id}] Alignment failed after max retries: {e}")
            raise


# Registry mapping method types to classes
METHOD_REGISTRY = {
    "grounded": GroundedQA,  # Base grounded QA (answer grounded in evidence)
    "minimal_sufficiency": MinimalSufficiencyMethod,  # Identifies minimal essential evidence
    "answer_first": AnswerFirstMethod,  # Answer-first pipeline
    "answer_evidence_alignment": AnswerEvidenceAlignment,  # Subtask 4: alignment
    "cot-qa": ChainOfThoughtsQuestionAnswering,  # Keep existing for backward compatibility
}


def build_model(model_config):
    """
    Build a QA model from configuration.

    Config example:
    {
        "method": "grounded",  # Changed from "system": "cot"
        "evidence_prompt_file_path": "prompts/evidence-classification-baseline.txt",
        "qa_prompt_file_path": "prompts/answer-generation.txt",
        "num_samples": 1,
        ...
    }
    """
    # Accept both "method" (new) and "system" (old) for backward compatibility
    method_type = model_config.get("method") or model_config.get("system", "grounded")

    # Map old "cot" to new "grounded" for backward compatibility
    if method_type == "cot":
        method_type = "grounded"

    if method_type not in METHOD_REGISTRY:
        raise ValueError(
            f"Unknown method: {method_type}. Available: {list(METHOD_REGISTRY.keys())}"
        )

    # Instantiate the class with all config parameters
    method_class = METHOD_REGISTRY[method_type]
    return method_class(**model_config)


def get_model_list():
    return ["grounded", "minimal_sufficiency", "answer_first", "cot-qa"]
