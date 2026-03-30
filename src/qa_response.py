from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


from enum import Enum

from pydantic import BaseModel, Field


class ThreeAnswerChoice(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class FourAnswerChoice(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class FiveAnswerChoice(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class TenAnswerChoice(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"


class ConfidenceLikertScale(str, Enum):
    HIGHLY_CONFIDENT = "Highly Confident"
    CONFIDENT = "Confident"
    SOMEWHAT_CONFIDENT = "Somewhat Confident"
    NOT_CONFIDENT = "Not Confident"


class MedQAResponse(BaseModel):
    reasoning: str = Field(
        ...,
        description="Explain the step-by-step thought process behind the provided values. ",
    )
    answer_choice: FiveAnswerChoice = Field(
        None, description="The answer choice selected by the model (A, B, C, D, E)"
    )
    confidence_level: ConfidenceLikertScale = Field(
        None,
        description="Confidence level of the answer (Highly Confident, Confident, Somewhat Confident, Not Confident)",
    )


class PubMedQAResponse(BaseModel):
    reasoning: str = Field(
        ...,
        description="Explain the step-by-step thought process behind the provided values. ",
    )
    answer_choice: ThreeAnswerChoice = Field(
        None, description="The answer choice selected by the model (A, B, C)"
    )
    confidence_level: ConfidenceLikertScale = Field(
        None,
        description="Confidence level of the answer (Highly Confident, Confident, Somewhat Confident, Not Confident)",
    )


class LongPubMedQAResponse(BaseModel):
    reasoning: str = Field(
        ...,
        description="Planning and step-by-step chain of thought process for answering the question. ",
    )
    long_answer: str = Field(None, description="The long answer for the given question")
    confidence_level: ConfidenceLikertScale = Field(
        None,
        description="Confidence level of the answer (Highly Confident, Confident, Somewhat Confident, Not Confident)",
    )


class MedMCQAResponse(BaseModel):
    reasoning: str = Field(
        ...,
        description="Explain the step-by-step thought process behind the provided values. ",
    )
    answer_choice: FourAnswerChoice = Field(
        None, description="The answer choice selected by the model (A, B, C, D)"
    )
    confidence_level: ConfidenceLikertScale = Field(
        None,
        description="Confidence level of the answer (Highly Confident, Confident, Somewhat Confident, Not Confident)",
    )


class MMLUProRespone(BaseModel):
    reasoning: str = Field(
        ...,
        description="Explain the step-by-step thought process behind the provided values. ",
    )
    answer_choice: TenAnswerChoice = Field(
        None,
        description="The answer choice selected by the model (A, B, C, D, E, F, G, H, I, J)",
    )
    confidence_level: ConfidenceLikertScale = Field(
        None,
        description="Confidence level of the answer (Highly Confident, Confident, Somewhat Confident, Not Confident)",
    )


class RelevanceCategory(str, Enum):
    """
    Enum for relevance categories.

    Attributes:
        ESSENTIAL (str): Essential relevance category.
        SUPPLEMENTARY (str): Supplementary relevance category.
        NOT_RELEVANT (str): Not relevant category.
    """

    ESSENTIAL = "Essential"
    SUPPLEMENTARY = "Supplementary"
    NOT_RELEVANT = "Not Relevant"


class SentenceRelevance(BaseModel):
    sentence_id: int = Field(
        ..., description="1-based sentence ID in the note excerpt."
    )
    relevance: RelevanceCategory = Field(
        ..., description="Relevance label of the sentence."
    )


class SentenceEvidenceWithRationale(BaseModel):
    sentence_id: int = Field(
        ..., description="1-based sentence ID in the note excerpt."
    )
    rationale: str = Field(..., description="Rationale for the relevance label.")
    relevance: RelevanceCategory = Field(
        ..., description="Relevance label of the sentence."
    )


class EHRRelevanceClassification(BaseModel):
    reasoning: str = Field(..., description="Reasoning for the evidence relevance.")
    sentence_evidence_list: List[SentenceRelevance] = Field(
        ...,
        description="List of evidence relevance entries, each with explicit sentence number and relevance.",
    )


class EHRArrayRelevanceClassification(BaseModel):
    reasoning: str = Field(..., description="Reasoning for the evidence relevance.")
    evidence_relevance_list: List[RelevanceCategory] = Field(
        ...,
        description="List of evidence relevance entries",
    )


class EHRRelevanceClassificationWithRationale(BaseModel):
    sentence_evidence_list: List[SentenceEvidenceWithRationale] = Field(
        ...,
        description="List of evidence relevance entries, each with explicit sentence number and relevance.",
    )


class SentenceEvidenceDict(BaseModel):
    """
    Response model using Pattern 1: ID→label mapping.

    Returns list format for structural validation. Enables detection of missing/extra IDs.
    """
    reasoning: str = Field(..., description="Reasoning for evidence classification.")
    sentence_evidence_list: List[SentenceRelevance] = Field(..., description="List of sentence evidence with sentence numbers and relevance labels.")


class AnswerSentenceAlignment(BaseModel):
    answer_id: str = Field(
        ..., description="Answer sentence ID (1-based string)."
    )
    evidence_id: List[str] = Field(
        ...,
        description="Note sentence IDs supporting this answer sentence. Use empty list if the sentence is not directly supported by the note.",
    )


class AnswerEvidenceAlignmentResponse(BaseModel):
    reasoning: str = Field(
        ..., description="Brief explanation of alignment decisions."
    )
    alignments: List[AnswerSentenceAlignment] = Field(
        ...,
        description="Alignment of each answer sentence to its supporting note sentences.",
    )


class QAResponse(BaseModel):
    reasoning: str = Field(..., description="Reasoning for the evidence relevance.")
    final_answer: str = Field(
        ..., description="Final answer to the clinician's question."
    )


# EvidenceSummary for array-like responses
class ArrayFullQAResponse(BaseModel):
    reasoning: str = Field(..., description="Reasoning for the evidence relevance.")
    evidence_relevance_list: List[RelevanceCategory] = Field(
        ...,
        description="List of evidence relevance entries, each with explicit sentence number and relevance.",
    )
    final_answer: str = Field(
        ..., description="Final answer to the clinician's question."
    )


class DictQAResponse(BaseModel):
    reasoning: str = Field(..., description="Reasoning for the evidence relevance.")
    sentence_evidence_list: List[SentenceRelevance] = Field(
        ...,
        description="List of evidence relevance entries, each with explicit sentence number and relevance.",
    )
    final_answer: str = Field(
        ..., description="Final answer to the clinician's question."
    )


# EvidenceClassification for group-like responses
class GroupedQAResponse(BaseModel):
    reasoning: str = Field(..., description="Reasoning for the evidence relevance.")
    essential_evidence_list: List[int] = Field(
        ..., description="List of sentence numbers that are essential evidence."
    )
    supplementary_evidence_list: List[int] = Field(
        ..., description="List of sentence numbers that are supplementary evidence."
    )
    not_relevant_evidence_list: List[int] = Field(
        ..., description="List of sentence numbers that are not relevant evidence."
    )
    final_answer: str = Field(
        ..., description="Final answer to the clinician's question."
    )


# DynamicEvidenceModel for dynamic-length responses
def create_dynamic_evidence_model(n: int) -> BaseModel:
    fields: Dict[str, tuple] = {
        "reasoning": (
            str,
            Field(..., description="Reasoning for the evidence relevance."),
        ),
    }

    for i in range(1, n + 1):
        fields[f"evidence_{i}_relevance"] = (
            RelevanceCategory,
            Field(..., description=f"Evidence relevance entry {i}."),
        )

    fields["final_answer"] = (
        str,
        Field(..., description="Final answer to the clinician's question."),
    )

    DynamicModel = type("DynamicEvidenceModel", (BaseModel,), fields)
    return DynamicModel


# Updated post-processing functions
def postprocess(raw_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-process raw output for array-like format.

    Args:
        raw_output (Dict[str, Any]): The raw output from the LLM.

    Returns:
        Dict[str, Any]: Validated and transformed output.
    """
    raw_output["evidence_relevance_list"] = [
        RelevanceCategory(entry) for entry in raw_output["evidence_relevance_list"]
    ]
    return ArrayFullQAResponse(**raw_output)


def postprocess_dict_response(raw_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-process raw output for dictionary-like format.

    Args:
        raw_output (Dict[str, Any]): The raw output from the LLM.

    Returns:
        Dict[str, Any]: Validated and transformed output.
    """
    # Convert the list of relevance strings to EvidenceRelevance enum values

    # sentence_evidence_list contains a dict with sentnce_id and relevance
    # sort the list by sentence_id

    sentence_evidence_list = sorted(
        raw_output["sentence_evidence_list"], key=lambda x: x["sentence_number"]
    )

    raw_output["evidence_relevance_list"] = [
        entry["relevance"] for entry in sentence_evidence_list
    ]
    return raw_output


def postprocess_grouped_response(raw_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-process raw output for group-like format.

    Args:
        raw_output (Dict[str, Any]): The raw output from the LLM.

    Returns:
        Dict[str, Any]: Validated and transformed output.
    """
    raise ValueError("Grouped response format is not supported for post-processing.")
    return ArrayFullQAResponse(**raw_output)


def postprocess_dynamic_response(raw_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-process raw output for dynamic-length format.

    Args:
        raw_output (Dict[str, Any]): The raw output from the LLM.
    Returns:
        Dict[str, Any]: Validated and transformed output.

    """
    # Convert the list of relevance strings to EvidenceRelevance enum values
    raise ValueError("Dynamic response format is not supported for post-processing.")
    # Convert the list of relevance strings to EvidenceRelevance enum values
    for key in raw_output.keys():
        if "evidence" in key:
            raw_output[key] = RelevanceCategory(raw_output[key])
    return ArrayFullQAResponse(**raw_output)


# Updated build_qa_response function
def build_qa_response(
    response_format: str, evidence_count: int = -1
) -> tuple[BaseModel, callable]:
    """
    Get the response structure and post-processing function based on the response format.

    Args:
        response_format (str): The response format to use.

    Returns:
        tuple[BaseModel, callable]: The appropriate response structure and post-processing function.
    """
    if response_format == "array_qa_response":
        return (EHRArrayRelevanceClassification, lambda x: x)
    elif response_format == "dict_qa_response":
        return (EHRRelevanceClassification, postprocess_dict_response)
    # elif response_format == "arrayqa_response":
    # return (EHRRelevanceClassification, postprocess_dict_response)
    elif response_format == "dict_qa_response_with_rationale":
        return (EHRRelevanceClassificationWithRationale, postprocess_dict_response)
    elif response_format == "grouped_qa_response":
        return (GroupedQAResponse, postprocess_grouped_response)
    elif response_format == "dynamic_qa_response":
        response_model_class = create_dynamic_evidence_model(evidence_count)
        return (response_model_class, postprocess_dynamic_response)
    elif response_format == "medqa_response":
        return (MedQAResponse, lambda x: x)
    elif response_format == "pubmedqa_response":
        return (PubMedQAResponse, lambda x: x)
    elif response_format == "long_pubmedqa_response":
        return (LongPubMedQAResponse, lambda x: x)
    elif response_format == "medmcqa_response":
        return (MedMCQAResponse, lambda x: x)
    elif response_format == "mmlu_pro_response":
        return (MMLUProRespone, lambda x: x)
    else:
        raise ValueError(f"Unknown response format: {response_format}")
