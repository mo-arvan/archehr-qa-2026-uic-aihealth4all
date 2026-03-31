import json
import os
import re
from pathlib import Path

import hydra
import pandas as pd
import sklearn.metrics
from omegaconf import DictConfig, OmegaConf
from tqdm import tqdm

import qa_response
from qa_model import build_model
from task import build_task
from utils import configure_logger, load_env_variables

# Configure logger
logger = configure_logger()


def report_evaluation(evidence_relevance_list, out_dir):
    def normalize_label(label):
        label = label.lower().replace(" ", "-")
        return label

    all_true = []
    all_pred = []

    for obj in evidence_relevance_list:
        true_labels = [
            normalize_label(label) for label in obj["ground_truth_relevance"]
        ]
        pred_labels = [normalize_label(e) for e in obj["predicted_relevance"]]

        all_true.extend(true_labels)
        all_pred.extend(pred_labels)

    classes = ["essential", "supplementary", "not-relevant"]

    if len(all_true) == 0:
        logger.warning("No true labels found. Skipping metrics calculation.")
        return

    metrics = sklearn.metrics.classification_report(
        all_true, all_pred, labels=classes, zero_division=0, output_dict=True
    )
    confusion_matrix = sklearn.metrics.confusion_matrix(
        all_true, all_pred, labels=classes, normalize="true"
    )

    # Format and log metrics using a DataFrame
    logger.info("Metrics:")
    metrics_df = pd.DataFrame(metrics).transpose()
    logger.info(f"\n{metrics_df.to_string(float_format='%.4f')}\n")

    # Format and log confusion matrix using a DataFrame
    logger.info("Confusion Matrix:")
    confusion_matrix_df = pd.DataFrame(
        confusion_matrix,
        index=["Actual: " + label for label in classes],
        columns=["Predicted: " + label for label in classes],
    )
    logger.info(f"\n{confusion_matrix_df.to_string(float_format='%.4f')}\n")

    metrics_df.to_csv(out_dir / "metrics.csv", index=True, float_format="%.3f")
    confusion_matrix_df.to_csv(
        out_dir / "confusion_matrix.csv", index=True, float_format="%.3f"
    )

    # Map the original classes to binary classes
    class_mapping = {
        "essential": "relevant",
        "supplementary": "relevant",
        "not-relevant": "not-relevant",
    }
    all_true_binary = [class_mapping[label] for label in all_true]
    all_pred_binary = [class_mapping[label] for label in all_pred]
    binary_classes = ["relevant", "not-relevant"]
    binary_metrics = sklearn.metrics.classification_report(
        all_true_binary,
        all_pred_binary,
        labels=binary_classes,
        zero_division=0,
        output_dict=True,
    )
    binary_confusion_matrix = sklearn.metrics.confusion_matrix(
        all_true_binary, all_pred_binary, labels=binary_classes, normalize="true"
    )

    # Format and log binary metrics using a DataFrame
    logger.info("Binary Metrics:")
    binary_metrics_df = pd.DataFrame(binary_metrics).transpose()
    logger.info(f"\n{binary_metrics_df.to_string(float_format='%.4f')}\n")

    binary_confusion_matrix_df = pd.DataFrame(
        binary_confusion_matrix,
        index=["Actual: " + label for label in binary_classes],
        columns=["Predicted: " + label for label in binary_classes],
    )

    binary_metrics_df.to_csv(
        out_dir / "binary_metrics.csv", index=True, float_format="%.3f"
    )
    binary_confusion_matrix_df.to_csv(
        out_dir / "binary_confusion_matrix.csv", index=True, float_format="%.3f"
    )


def _normalize_relevance(label):
    """Normalize a relevance label to lowercase for comparison.

    Handles both RelevanceCategory enum values and plain strings from cached JSON.
    """
    if isinstance(label, qa_response.RelevanceCategory):
        return label.value.lower()
    return str(label).lower()


def extract_evidence_ids(evidence_relevance_list, include_supplementary=False):
    """
    Extract sentence IDs (1-based) from evidence classification results.

    For subtask 2 submission: returns list of sentence ID strings where
    classification is Essential (strict) or Essential + Supplementary (lenient).
    """
    ids = []
    for idx, label in enumerate(evidence_relevance_list):
        norm = _normalize_relevance(label)
        if norm == "essential":
            ids.append(str(idx + 1))
        elif include_supplementary and norm == "supplementary":
            ids.append(str(idx + 1))
    return ids


def strip_citations(answer_text):
    """
    Strip citation markers (e.g., |8| or |1,2,3|) from the answer text.

    For subtask 3 submission: returns plain answer text without citation markers.
    """
    # Remove citation patterns like |8| or |1,2,3| at end of lines
    stripped = re.sub(r"\s*\|[0-9,\s]+\|\s*", " ", answer_text)
    # Clean up extra whitespace
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return stripped


def run_benchmark(experiment_config: dict, env_vars: dict) -> None:
    """
    Benchmark the model with the given configuration.

    Args:
        experiment_config (dict): Configuration for the experiment.
        env_vars (dict): Environment variables.

    Returns:
        None
    """
    # Initialize the benchmark with the provided configuration
    # default will be exp + YYYYMMDD_HHMMSS

    output_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
    results_dir = output_dir / "results"

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    logger.info(f"Experiment Config: {experiment_config}")

    response_out_dir = results_dir / "response_output"
    model_output_with_phi_dir = results_dir / "response_output_with_phi"

    if not os.path.exists(response_out_dir):
        os.makedirs(response_out_dir)
    if not os.path.exists(model_output_with_phi_dir):
        os.makedirs(model_output_with_phi_dir)

    # Load the dataset
    task = build_task(
        experiment_config.dataset.dataset_name, experiment_config.dataset.data_dir
    )

    logger.info(f"Loaded dataset: {experiment_config['dataset']}")
    num_with_gt = sum(1 for d in task if d.get("sentence_relevance"))
    logger.info(
        f"Task has {len(task)} cases; {num_with_gt} have ground-truth sentence relevance "
        f"(from archehr-qa_key.json 'answers'). Evaluation runs only when this count > 0."
    )

    # Merge method and model configs (model params like model_name are now separate)
    method_config = OmegaConf.to_container(experiment_config.method, resolve=True)
    if hasattr(experiment_config, 'model'):
        model_config = OmegaConf.to_container(experiment_config.model, resolve=True)
        method_config.update(model_config)  # Add model_name, reasoning_effort, etc.

    qa_system = build_model(method_config)

    max_error_tolerance = 10
    error_count = 0

    include_supplementary = method_config.get("include_supplementary", False)
    is_subtask4 = method_config.get("method") == "answer_evidence_alignment"

    evidence_relevance_list = []
    submission_list = []
    subtask2_submission_list = []
    subtask3_submission_list = []
    subtask4_submission_list = []

    has_ground_truth = False

    for idx, data in tqdm(enumerate(task), total=len(task)):
        case_id = data["case_id"]

        output_file_name = f"{response_out_dir}/{case_id}.json"
        out = {}
        out_with_phi = {}

        if not os.path.exists(output_file_name):
            try:
                answer_dict = qa_system.answer(task_dict=data)

                if is_subtask4:
                    out["case_id"] = data["case_id"]
                    out["alignments"] = answer_dict["alignments"]
                else:
                    out["case_id"] = data["case_id"]
                    out["ground_truth_relevance"] = data.get("sentence_relevance", [])
                    out["predicted_relevance"] = answer_dict["evidence_classification"][
                        "evidence_relevance_list"
                    ]

                out_with_phi = data.copy()
                out_with_phi["pred"] = answer_dict

            except Exception as e:
                logger.error(f"Error processing case {case_id}: {e}")
                error_count += 1
                if error_count > max_error_tolerance:
                    logger.error(
                        "Max error tolerance reached. Exiting the benchmarking process."
                    )
                    break
                continue

            with open(output_file_name, "w") as f:
                json.dump(out, f, indent=4)
            with open(f"{model_output_with_phi_dir}/{case_id}.json", "w") as f:
                json.dump(out_with_phi, f, indent=4)

        else:
            with open(output_file_name, "r") as f:
                out = json.load(f)

            with open(f"{model_output_with_phi_dir}/{case_id}.json", "r") as f:
                out_with_phi = json.load(f)

        if is_subtask4:
            subtask4_submission_list.append(
                {
                    "case_id": case_id,
                    "prediction": out_with_phi["pred"]["alignments"],
                }
            )
            continue

        evidence_relevance_list.append(out)

        if out.get("ground_truth_relevance"):
            has_ground_truth = True

        # Legacy submission format
        submission_row = {
            "case_id": case_id,
            "answer": out_with_phi["pred"]["answer_generation"]["final_answer"],
        }
        submission_list.append(submission_row)

        # Subtask 2: Evidence Identification (sentence IDs)
        predicted_relevance = out_with_phi["pred"]["evidence_classification"][
            "evidence_relevance_list"
        ]
        evidence_ids = extract_evidence_ids(
            predicted_relevance, include_supplementary=include_supplementary
        )
        subtask2_submission_list.append(
            {
                "case_id": case_id,
                "prediction": evidence_ids,
            }
        )

        # Subtask 3: Answer Generation (plain text, no citations)
        raw_answer = out_with_phi["pred"]["answer_generation"]["final_answer"]
        plain_answer = strip_citations(raw_answer)
        subtask3_submission_list.append(
            {
                "case_id": case_id,
                "prediction": plain_answer,
            }
        )

    # save submission files
    if is_subtask4:
        num_completed = len(subtask4_submission_list)
        if num_completed != len(task):
            logger.warning(
                f"Mismatch in number of submission entries and task entries. "
                f"Submission: {num_completed}, Task: {len(task)}"
            )
        subtask4_file = f"{results_dir}/submission_subtask4.json"
        with open(subtask4_file, "w") as f:
            json.dump(subtask4_submission_list, f, indent=4)
        logger.info(f"Subtask 4 submission saved to {subtask4_file}")
        return

    num_completed = len(submission_list)
    if num_completed != len(task):
        logger.warning(
            f"Mismatch in number of submission entries and task entries. "
            f"Submission: {num_completed}, Task: {len(task)}"
        )

    # Legacy format (contains generated answers — PHI)
    submission_file_name = f"{results_dir}/submission_with_phi.json"
    with open(submission_file_name, "w") as f:
        json.dump(submission_list, f, indent=4)
    logger.info(f"Legacy submission file saved to {submission_file_name}")

    # 2026 subtask 2 submission
    subtask2_file = f"{results_dir}/submission_subtask2.json"
    with open(subtask2_file, "w") as f:
        json.dump(subtask2_submission_list, f, indent=4)
    logger.info(f"Subtask 2 submission saved to {subtask2_file}")

    # 2026 subtask 3 submission (contains generated answers — PHI)
    subtask3_file = f"{results_dir}/submission_subtask3_with_phi.json"
    with open(subtask3_file, "w") as f:
        json.dump(subtask3_submission_list, f, indent=4)
    logger.info(f"Subtask 3 submission saved to {subtask3_file}")

    # Report evaluation metrics (only when ground truth is available)
    if has_ground_truth:
        logger.info("Reporting evaluation metrics...")
        report_evaluation(evidence_relevance_list, results_dir)
    else:
        logger.info(
            "No ground truth labels available. Skipping evaluation metrics. "
            "Ground truth comes from the split's archehr-qa_key.json 'answers' field; "
            "dev has it, test does not. Use dataset=archehr-dev to run evaluation."
        )


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(experiment_config: DictConfig):
    """
    Main function to run the benchmark.
    """

    # Load environment variables
    env_vars = load_env_variables()

    # Run the benchmark
    run_benchmark(experiment_config, env_vars)


if __name__ == "__main__":
    main()
