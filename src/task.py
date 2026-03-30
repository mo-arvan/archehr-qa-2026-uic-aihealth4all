import json
import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from datasets import Dataset

logger = logging.getLogger(__name__)


def load_archEHR_data(
    data_dir=None,
    dataset_type="dev",
):
    """
    Load the archEHR dataset (dev or test).

    Args:
        data_dir (str): Path to the directory containing the dataset files.
        dataset_type (str): Type of dataset to load ('dev' or 'test').

    Returns:
        Dataset: A Hugging Face Dataset object containing the processed data.

    Raises:
        FileNotFoundError: If the XML or JSON file is not found.
        ET.ParseError: If the XML file cannot be parsed.
        ValueError: If an invalid dataset_type is provided.
    """
    valid_types = ["dev", "test", "test-2026"]
    if dataset_type not in valid_types:
        logger.error(f"Invalid dataset_type: {dataset_type}. Must be one of {valid_types}.")
        raise ValueError(f"dataset_type must be one of {valid_types}")
    
    if data_dir is None:
        logger.error("data_dir must be provided.")
        raise ValueError("data_dir must be provided.")

    dataset_dir = Path(data_dir) / dataset_type
    xml_file_path = dataset_dir / "archehr-qa.xml"
    labels_file_path = dataset_dir / "archehr-qa_key.json"
    
    unlabled_set = False

    if not os.path.exists(xml_file_path):
        logger.error(f"XML file not found: {xml_file_path}")
        raise FileNotFoundError(f"XML file not found: {xml_file_path}")

    if not os.path.exists(labels_file_path):
        logger.debug(f"Labels file not found: {labels_file_path}")
        unlabled_set = True

    try:
        root = ET.parse(xml_file_path).getroot()
    except ET.ParseError as e:
        logger.error(f"Error parsing XML file: {e}")
        raise

    case_data = []

    for case in root.findall("case"):
        case_id = case.attrib.get("id")
        patient_narrative = case.find("patient_narrative")
        clinician_question = case.find("clinician_question")

        # Extract all sentences into a list of dicts
        sentence_elements = case.find("note_excerpt_sentences")
        sentences = []
        if sentence_elements is not None:
            for sentence in sentence_elements.findall("sentence"):
                sentence_info = {
                    "sentence_id": sentence.attrib.get("id"),
                    "paragraph_id": sentence.attrib.get("paragraph_id"),
                    "start_char_index": sentence.attrib.get("start_char_index"),
                    "length": sentence.attrib.get("length"),
                    "text": sentence.text.strip() if sentence.text else "",
                }
                sentences.append(sentence_info)
        sentence_list = [r["sentence_id"] + ": " + r["text"] for r in sentences]
        evidence_list = "\n".join(sentence_list)

        # Load answer sentences for Subtask 4 (included in test-2026 XML)
        answer_sentence_elements = case.find("answer_sentences")
        answer_sentences = []
        if answer_sentence_elements is not None:
            for ans_sent in answer_sentence_elements.findall("sentence"):
                answer_sentences.append(
                    {
                        "sentence_id": ans_sent.attrib.get("id"),
                        "text": ans_sent.text.strip() if ans_sent.text else "",
                    }
                )

        case_entry = {
            "case_id": case_id,
            "patient_narrative": patient_narrative.text.strip() if patient_narrative is not None else "",
            "clinician_question": clinician_question.text.strip() if clinician_question is not None else "",
            "sentences": sentences,  # store list of dictionaries
            "evidence_list": evidence_list,
        }
        if answer_sentences:
            case_entry["answer_sentences"] = answer_sentences

        case_data.append(case_entry)

    if not unlabled_set:
        with open(labels_file_path, "r") as f:
            labels = json.load(f)
    else:
        labels = []

    case_to_label_dict = {
        case["case_id"]: case["answers"]
        for case in labels
        if "answers" in case
    }

    # Answer sentences for Subtask 4 (from key.json when available)
    case_to_answer_sentences_dict = {
        case["case_id"]: [
            {"sentence_id": s["id"], "text": s["text"]}
            for s in case["clinician_answer_sentences"]
        ]
        for case in labels
        if "clinician_answer_sentences" in case
    }

    for case in case_data:
        case_id = case["case_id"]

        # Load answer sentences for Subtask 4 from key.json (overrides XML if present)
        if case_id in case_to_answer_sentences_dict:
            case["answer_sentences"] = sorted(
                case_to_answer_sentences_dict[case_id],
                key=lambda x: int(x["sentence_id"]),
            )

        if case_id in case_to_label_dict:
            case_sentence_labels = case_to_label_dict[case_id]
            case_sentence_labels = sorted(
                case_sentence_labels, key=lambda x: int(x["sentence_id"])
            )
            sentence_relevance_list = [l["relevance"] for l in case_sentence_labels]
            case["sentence_relevance"] = sentence_relevance_list
        else:
            if not unlabled_set:
                logger.debug(f"Case ID {case_id} has no relevance labels in key file.")

    arch_ehr_dataset = Dataset.from_list(case_data)
    return arch_ehr_dataset


TASKS_DICT = {
    "archehr-dev": lambda data_dir=None, dataset_type="dev": load_archEHR_data(data_dir, dataset_type),
    "archehr-test": lambda data_dir=None, dataset_type="test": load_archEHR_data(data_dir, dataset_type),
    "archehr-test-2026": lambda data_dir=None, dataset_type="test-2026": load_archEHR_data(data_dir, dataset_type),
}


def build_task(task_name, data_dir=None):
    """
    Build a task dataset based on the task name.

    Args:
        task_name (str): Name of the task to build.
        data_dir (str, optional): Path to the dataset directory. Defaults to None.

    Returns:
        Dataset: A Hugging Face Dataset object for the specified task.

    Raises:
        ValueError: If the task name is not supported.
    """
    if task_name not in TASKS_DICT:
        logger.error(f"Task {task_name} not supported.")
        raise ValueError(f"Task {task_name} not supported.")

    # Extract dataset_type: strip "archehr-" prefix to get "dev", "test", or "test-2026"
    dataset_type = task_name.removeprefix("archehr-")
    return TASKS_DICT[task_name](data_dir=data_dir, dataset_type=dataset_type) if data_dir else TASKS_DICT[task_name]()


def get_task_list():
    """
    Get the list of available tasks.

    Returns:
        list: A list of task names.
    """
    return list(TASKS_DICT.keys())
