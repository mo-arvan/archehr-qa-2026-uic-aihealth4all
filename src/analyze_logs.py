#!/usr/bin/env python3
"""
Log & Result Analysis for ArchEHR-QA Experiments

Parses experiment JSON outputs and benchmark logs to report:
- Word count violation rates
- Model refusals, API failures, pipeline crashes
- Correction success rates
- Citation error rates
- Attempts distributions
- Error taxonomy (ALL error types)
- Model and method comparisons
- Latency analysis

Results are split by dataset (dev vs test) when both are present.

Usage:
    python src/analyze_logs.py hydra.run.dir=outputs/log_analysis/
    python src/analyze_logs.py verbose=true hydra.run.dir=outputs/log_analysis/
    python src/analyze_logs.py experiment_dirs='[outputs/2026-selected]' hydra.run.dir=outputs/log_analysis/
"""

import json
import logging
import re
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

import hydra
import pandas as pd
import yaml
from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


class IssueType(Enum):
    WORD_COUNT = "word_count"
    CITATION_MISSING = "citation_missing"
    CITATION_EXTRA = "citation_extra"
    COMBINED = "combined"
    REFUSAL = "refusal"
    API_NONE = "api_none"
    SCHEMA_ERROR = "schema_error"
    PIPELINE_FAILURE = "pipeline_failure"
    OTHER = "other"


@dataclass
class AttemptRecord:
    """A single failed validation attempt."""

    case_id: str
    attempt_number: int
    issue_type: IssueType
    issue_text: str
    word_count: int | None = None


@dataclass
class LogError:
    """An error from benchmark.log not captured in JSON."""

    case_id: str
    error_type: IssueType
    message: str
    experiment: str


@dataclass
class CaseRecord:
    """Aggregated data for a single case within one experiment."""

    case_id: str
    experiment: str
    model: str
    method: str
    reasoning_effort: str
    dataset: str = "unknown"
    total_attempts: int = 1
    failed_attempts: list[AttemptRecord] = field(default_factory=list)
    passed_first_try: bool = True
    max_retries_exceeded: bool = False
    final_word_count: int | None = None
    # answer-first specific
    num_candidates: int = 0
    candidate_attempt_counts: list[int] = field(default_factory=list)
    # timing (from log)
    duration_seconds: float | None = None
    # log-only errors
    log_errors: list[LogError] = field(default_factory=list)
    pipeline_failed: bool = False


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

RE_WORD_COUNT = re.compile(r"Answer is too long: (\d+) words \(limit: (\d+)\)")
RE_WORD_COUNT_ALT = re.compile(
    r"Answer word count exceeds the limit of (\d+) words.*?:\s*(\d+)"
)
RE_CITATION_MISSING = re.compile(r"Essential evidence (\S+) is not cited")
RE_CITATION_EXTRA = re.compile(r"Answer citation (\S+) is not in the essential")
RE_CITED_MISMATCH = re.compile(r"Cited evidence mismatch")
RE_CITATION_BLOCK = re.compile(r"\|[\d,\s]+\|")

RE_LOG_LINE = re.compile(
    r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\]"
    r"\[ehr-qa\]\[(\w+)\] - (.*)"
)
RE_CASE_ID = re.compile(r"\[case (\d+)\]")
RE_VALIDATION_FAILED = re.compile(
    r"\[case (\d+)\] Validation failed on attempt (\d+): (.*)"
)
RE_MAX_RETRIES = re.compile(r"Max retries \((\d+)\) exceeded for case (\d+)")
RE_ERROR_PROCESSING = re.compile(r"Error processing case (\d+): (.*)")

# New patterns for refusals, NoneType, ValidationError, pipeline failures
RE_NONETYPE_ERROR = re.compile(
    r"\[case (\d+)\] Unexpected error \(AttributeError\)"
)
RE_VALIDATION_ERROR = re.compile(
    r"\[case (\d+)\] Non-retryable error \(ValidationError\)"
)
RE_FAILED_CANDIDATES = re.compile(
    r"\[case (\d+)\] Failed to generate any answer candidates"
)
RE_ERROR_CANDIDATE = re.compile(
    r"\[case (\d+)\] Error generating answer candidate (\d+): (.*)"
)
RE_SUBMISSION_MISMATCH = re.compile(
    r"Mismatch.*Submission: (\d+), Task: (\d+)"
)
# Refusal detection in Pydantic error detail lines
RE_REFUSAL_TEXT = re.compile(
    r"I'm sorry|I cannot|cannot assist|I can't|I apologize",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def parse_issue_text(issue_text: str) -> tuple[IssueType, int | None]:
    """Parse an issue string to extract type and word count."""
    wc_match = RE_WORD_COUNT.search(issue_text)
    word_count = int(wc_match.group(1)) if wc_match else None

    if word_count is None:
        wc_alt = RE_WORD_COUNT_ALT.search(issue_text)
        if wc_alt:
            word_count = int(wc_alt.group(2))

    has_wc = "too long" in issue_text.lower() or "word count exceeds" in issue_text.lower()
    has_cite = (
        "citation" in issue_text.lower()
        or "not cited" in issue_text.lower()
        or "cited evidence mismatch" in issue_text.lower()
    )

    if has_wc and has_cite:
        issue_type = IssueType.COMBINED
    elif has_wc:
        issue_type = IssueType.WORD_COUNT
    elif has_cite:
        has_missing = bool(RE_CITATION_MISSING.search(issue_text))
        has_extra = bool(RE_CITATION_EXTRA.search(issue_text))
        has_mismatch = bool(RE_CITED_MISMATCH.search(issue_text))
        if (has_missing and has_extra) or has_mismatch:
            issue_type = IssueType.COMBINED
        elif has_extra:
            issue_type = IssueType.CITATION_EXTRA
        else:
            issue_type = IssueType.CITATION_MISSING
    else:
        issue_type = IssueType.OTHER

    return issue_type, word_count


def compute_word_count(answer: str) -> int:
    """Count words in an answer, stripping citation markers like |1,2,3|."""
    stripped = RE_CITATION_BLOCK.sub(" ", answer)
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return len(stripped.split()) if stripped else 0


def _extract_failures(history: list | None) -> list[AttemptRecord]:
    """Extract AttemptRecords from an answer_history array of failed attempts."""
    if not history:
        return []
    records = []
    for i, entry in enumerate(history):
        issue = entry.get("issue") if isinstance(entry, dict) else None
        if not issue:
            continue
        issue_type, word_count = parse_issue_text(issue)
        records.append(
            AttemptRecord(
                case_id="",  # filled by caller
                attempt_number=i + 1,
                issue_type=issue_type,
                issue_text=issue,
                word_count=word_count,
            )
        )
    return records


# ---------------------------------------------------------------------------
# Config parsing
# ---------------------------------------------------------------------------


def parse_experiment_config(exp_dir: Path, parent_dir_name: str = "") -> dict:
    """Extract experiment config from .hydra/config.yaml or directory name."""
    config = {
        "method": "unknown",
        "model": "unknown",
        "reasoning_effort": "unknown",
        "dataset": "unknown",
    }

    config_file = exp_dir / ".hydra" / "config.yaml"
    if config_file.exists():
        try:
            with open(config_file) as f:
                cfg = yaml.safe_load(f)
            config["method"] = cfg.get("method", {}).get("method", "unknown")
            config["model"] = cfg.get("model", {}).get("model_name", "unknown")
            config["reasoning_effort"] = cfg.get("model", {}).get(
                "reasoning_effort", "unknown"
            )
            config["dataset"] = cfg.get("dataset", {}).get(
                "dataset_name", "unknown"
            )
        except Exception:
            pass

    # Fallback: parse directory name
    name = exp_dir.name
    if config["model"] == "unknown":
        if "gpt-5.1" in name:
            config["model"] = "gpt-5.1"
        elif "gpt-5.2" in name:
            config["model"] = "gpt-5.2"
    if config["method"] == "unknown":
        if "answer-first" in name:
            config["method"] = "answer_first"
        elif "baseline" in name:
            config["method"] = "grounded"
        elif "tight" in name:
            config["method"] = "tight"

    if config["reasoning_effort"] == "unknown":
        if "-high-" in name:
            config["reasoning_effort"] = "high"
        elif "-med-" in name or "-medium-" in name:
            config["reasoning_effort"] = "medium"
        elif "-low-" in name:
            config["reasoning_effort"] = "low"

    # Dataset fallback from parent directory name
    if config["dataset"] == "unknown":
        ctx = parent_dir_name or ""
        if "selected" in ctx or "archive" in ctx:
            config["dataset"] = "archehr-dev"
        elif "test" in ctx:
            config["dataset"] = "archehr-test-2026"

    return config


# ---------------------------------------------------------------------------
# JSON response parsing
# ---------------------------------------------------------------------------


def parse_json_responses(exp_dir: Path, config: dict) -> list[CaseRecord]:
    """Parse all response_output_with_phi JSON files for an experiment."""
    json_dir = exp_dir / "results" / "response_output_with_phi"
    if not json_dir.exists():
        return []

    method = config["method"]
    cases = []

    for json_file in sorted(json_dir.glob("*.json")):
        try:
            with open(json_file) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        case_id = str(data.get("case_id", json_file.stem))
        pred = data.get("pred", {})

        if method == "answer_first":
            record = _parse_answer_first_case(case_id, pred, config, exp_dir.name)
        else:
            record = _parse_grounded_case(case_id, pred, config, exp_dir.name)

        record.dataset = config["dataset"]

        # Compute word count on final answer
        answer_gen = pred.get("answer_generation", {})
        if answer_gen and isinstance(answer_gen, dict):
            final = answer_gen.get("final_answer", "")
            if final:
                record.final_word_count = compute_word_count(final)

        cases.append(record)

    return cases


def _parse_grounded_case(
    case_id: str, pred: dict, config: dict, exp_name: str
) -> CaseRecord:
    """Parse a grounded/baseline case."""
    answer_history = pred.get("answer_history") or []

    answer_gen = pred.get("answer_generation", {})
    gen_history = (
        answer_gen.get("answer_history") if isinstance(answer_gen, dict) else None
    ) or []

    failures = _extract_failures(answer_history)
    failures.extend(_extract_failures(gen_history))

    for f in failures:
        f.case_id = case_id

    total_attempts = len(failures) + 1

    return CaseRecord(
        case_id=case_id,
        experiment=exp_name,
        model=config["model"],
        method=config["method"],
        reasoning_effort=config["reasoning_effort"],
        total_attempts=total_attempts,
        failed_attempts=failures,
        passed_first_try=len(failures) == 0,
        max_retries_exceeded=False,
    )


def _parse_answer_first_case(
    case_id: str, pred: dict, config: dict, exp_name: str
) -> CaseRecord:
    """Parse an answer-first case."""
    candidates = pred.get("answer_history") or []
    all_failures = []
    candidate_attempt_counts = []

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        nested = candidate.get("answer_history") or []
        sub_failures = _extract_failures(nested)
        for f in sub_failures:
            f.case_id = case_id
        all_failures.extend(sub_failures)
        candidate_attempt_counts.append(len(sub_failures) + 1)

    answer_gen = pred.get("answer_generation", {})
    gen_history = (
        answer_gen.get("answer_history") if isinstance(answer_gen, dict) else None
    ) or []
    final_failures = _extract_failures(gen_history)
    for f in final_failures:
        f.case_id = case_id
    all_failures.extend(final_failures)

    return CaseRecord(
        case_id=case_id,
        experiment=exp_name,
        model=config["model"],
        method=config["method"],
        reasoning_effort=config["reasoning_effort"],
        total_attempts=len(all_failures) + 1,
        failed_attempts=all_failures,
        passed_first_try=len(all_failures) == 0,
        max_retries_exceeded=False,
        num_candidates=len(candidates),
        candidate_attempt_counts=candidate_attempt_counts,
    )


# ---------------------------------------------------------------------------
# Benchmark log parsing
# ---------------------------------------------------------------------------


def parse_benchmark_log(exp_dir: Path, exp_name: str = "") -> dict:
    """Parse benchmark.log for timestamps, errors, refusals, and crashes.

    Returns dict with keys:
        'cases': dict[case_id] -> {duration_seconds, error}
        'log_errors': list[LogError]
        'all_case_ids': set of case IDs seen in log
        'submission_mismatch': (submitted, expected) or None
    """
    log_file = exp_dir / "benchmark.log"
    result = {
        "cases": {},
        "log_errors": [],
        "all_case_ids": set(),
        "submission_mismatch": None,
    }
    if not log_file.exists():
        return result

    case_times: dict[str, dict] = {}
    errors: dict[str, str] = {}
    log_errors: list[LogError] = []
    all_case_ids: set[str] = set()
    # Track multi-line context: after an ERROR line, the next few lines
    # may contain the refusal text or stack trace
    pending_error_case: str | None = None
    pending_error_lines: list[str] = []

    def _flush_pending():
        nonlocal pending_error_case, pending_error_lines
        if pending_error_case and pending_error_lines:
            full_text = "\n".join(pending_error_lines)
            if RE_REFUSAL_TEXT.search(full_text):
                log_errors.append(
                    LogError(
                        case_id=pending_error_case,
                        error_type=IssueType.REFUSAL,
                        message="Model refused to answer",
                        experiment=exp_name,
                    )
                )
        pending_error_case = None
        pending_error_lines = []

    try:
        with open(log_file) as f:
            for line in f:
                line = line.rstrip()
                m = RE_LOG_LINE.match(line)

                if not m:
                    # Continuation line (stack trace or error detail)
                    if pending_error_case:
                        pending_error_lines.append(line)
                    continue

                # New log line — flush pending context
                _flush_pending()

                timestamp_str, level, message = m.groups()
                ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")

                # Track per-case timestamps
                case_match = RE_CASE_ID.search(message)
                if case_match:
                    cid = case_match.group(1)
                    all_case_ids.add(cid)
                    if cid not in case_times:
                        case_times[cid] = {"start": ts, "end": ts}
                    else:
                        case_times[cid]["end"] = ts

                # --- ERROR / WARNING detection ---

                # NoneType error (content filter / API returned None)
                if RE_NONETYPE_ERROR.search(message):
                    cid = RE_NONETYPE_ERROR.search(message).group(1)
                    log_errors.append(
                        LogError(
                            case_id=cid,
                            error_type=IssueType.API_NONE,
                            message="API returned None (content filter)",
                            experiment=exp_name,
                        )
                    )

                # ValidationError (may be refusal — check subsequent lines)
                elif RE_VALIDATION_ERROR.search(message):
                    cid = RE_VALIDATION_ERROR.search(message).group(1)
                    log_errors.append(
                        LogError(
                            case_id=cid,
                            error_type=IssueType.SCHEMA_ERROR,
                            message="Pydantic ValidationError",
                            experiment=exp_name,
                        )
                    )
                    # Start collecting subsequent lines for refusal detection
                    pending_error_case = cid
                    pending_error_lines = [message]

                # Failed to generate any answer candidates (pipeline failure)
                elif RE_FAILED_CANDIDATES.search(message):
                    cid = RE_FAILED_CANDIDATES.search(message).group(1)
                    log_errors.append(
                        LogError(
                            case_id=cid,
                            error_type=IssueType.PIPELINE_FAILURE,
                            message="Failed to generate any answer candidates",
                            experiment=exp_name,
                        )
                    )

                # Error generating candidate (partial failure)
                elif RE_ERROR_CANDIDATE.search(message):
                    em = RE_ERROR_CANDIDATE.search(message)
                    cid = em.group(1)
                    candidate_num = em.group(2)
                    err_msg = em.group(3)
                    # Don't duplicate — NoneType and ValidationError already logged above
                    # This captures the candidate-level warning

                # Error processing case (top-level failure)
                elif RE_ERROR_PROCESSING.match(message):
                    em = RE_ERROR_PROCESSING.match(message)
                    errors[em.group(1)] = em.group(2)

                # Max retries exceeded
                elif RE_MAX_RETRIES.match(message):
                    em = RE_MAX_RETRIES.match(message)
                    errors[em.group(2)] = f"Max retries ({em.group(1)}) exceeded"

                # Submission mismatch
                elif RE_SUBMISSION_MISMATCH.search(message):
                    sm = RE_SUBMISSION_MISMATCH.search(message)
                    result["submission_mismatch"] = (
                        int(sm.group(1)),
                        int(sm.group(2)),
                    )

        # Flush any remaining pending context
        _flush_pending()

    except OSError:
        pass

    cases_data = {}
    for cid, times in case_times.items():
        duration = (times["end"] - times["start"]).total_seconds()
        cases_data[cid] = {
            "duration_seconds": duration,
            "error": errors.get(cid),
        }

    for cid, err in errors.items():
        if cid not in cases_data:
            cases_data[cid] = {"duration_seconds": None, "error": err}

    result["cases"] = cases_data
    result["log_errors"] = log_errors
    result["all_case_ids"] = all_case_ids
    return result


def merge_log_data(
    cases: list[CaseRecord],
    log_result: dict,
    config: dict,
    exp_name: str,
) -> list[CaseRecord]:
    """Merge log data into CaseRecords. Returns new CaseRecords for missing cases."""
    cases_data = log_result["cases"]
    log_errors = log_result["log_errors"]
    all_log_ids = log_result["all_case_ids"]

    # Attach timing and error info to existing cases
    for case in cases:
        info = cases_data.get(case.case_id)
        if not info:
            continue
        case.duration_seconds = info.get("duration_seconds")
        if info.get("error") and "Max retries" in info["error"]:
            case.max_retries_exceeded = True

    # Attach log errors to existing cases
    case_map = {c.case_id: c for c in cases}
    for le in log_errors:
        if le.case_id in case_map:
            case_map[le.case_id].log_errors.append(le)

    # Detect missing cases: in log but not in JSON = pipeline failure
    json_ids = set(c.case_id for c in cases)
    missing_ids = all_log_ids - json_ids

    new_cases = []
    for cid in sorted(missing_ids, key=int):
        # Find what errors this case had
        case_log_errors = [le for le in log_errors if le.case_id == cid]
        new_case = CaseRecord(
            case_id=cid,
            experiment=exp_name,
            model=config["model"],
            method=config["method"],
            reasoning_effort=config["reasoning_effort"],
            dataset=config["dataset"],
            total_attempts=0,
            passed_first_try=False,
            pipeline_failed=True,
            log_errors=case_log_errors,
        )
        info = cases_data.get(cid)
        if info:
            new_case.duration_seconds = info.get("duration_seconds")
        new_cases.append(new_case)

    return new_cases


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

SEPARATOR = "-" * 70


def _pct(num: int, den: int) -> str:
    if den == 0:
        return "N/A"
    return f"{num / den * 100:.1f}%"


def _bar(count: int, total: int, width: int = 30) -> str:
    if total == 0:
        return ""
    filled = round(count / total * width)
    return "#" * filled


def _print_dataset_report(
    dataset_label: str,
    experiments: dict[str, list[CaseRecord]],
    all_cases: list[CaseRecord],
    log_data_all: dict[str, dict],
    verbose: bool = False,
    section_offset: int = 0,
) -> None:
    """Print the full report for a single dataset group."""
    s = section_offset

    logger.info(f"{'=' * 70}")
    logger.info(f"  {dataset_label}")
    logger.info(f"{'=' * 70}")
    logger.info(f"  Experiments: {len(experiments)}")
    logger.info(f"  Total cases: {len(all_cases)}")
    models = sorted(set(c.model for c in all_cases))
    methods = sorted(set(c.method for c in all_cases))
    logger.info(f"  Models: {', '.join(models)}")
    logger.info(f"  Methods: {', '.join(methods)}")

    _print_overview_table(experiments, s + 1)
    _print_log_errors(all_cases, experiments, verbose, s + 2)
    _print_word_count_violations(all_cases, verbose, s + 3)
    _print_correction_success(all_cases, s + 4)
    _print_citation_errors(all_cases, s + 5)
    _print_attempts_distribution(all_cases, s + 6)
    _print_error_taxonomy(all_cases, s + 7)
    _print_model_comparison(all_cases, s + 8)
    _print_method_comparison(all_cases, s + 9)
    _print_word_count_distribution(all_cases, s + 10)
    _print_latency_analysis(all_cases, s + 11)
    _print_crash_failures(experiments, log_data_all, s + 12)


def _print_overview_table(
    experiments: dict[str, list[CaseRecord]], section: int
) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. OVERVIEW TABLE")
    logger.info(SEPARATOR)

    header = (
        f"{'Experiment':<45} {'Cases':>5} {'Pass1':>5} "
        f"{'Retry':>5} {'Fail':>4} {'Crash':>5}"
    )
    logger.info(header)
    logger.info("-" * len(header))

    for exp_name in sorted(experiments):
        cases = experiments[exp_name]
        n = len(cases)
        pass1 = sum(1 for c in cases if c.passed_first_try and not c.pipeline_failed)
        retried_ok = sum(
            1
            for c in cases
            if not c.passed_first_try
            and not c.max_retries_exceeded
            and not c.pipeline_failed
        )
        max_r = sum(1 for c in cases if c.max_retries_exceeded)
        crashed = sum(1 for c in cases if c.pipeline_failed)

        label = exp_name[:44]
        logger.info(
            f"{label:<45} {n:>5} {pass1:>5} {retried_ok:>5} "
            f"{max_r:>4} {crashed:>5}"
        )


def _print_log_errors(
    all_cases: list[CaseRecord],
    experiments: dict[str, list[CaseRecord]],
    verbose: bool,
    section: int,
) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. API ERRORS & MODEL REFUSALS (from benchmark.log)")
    logger.info(SEPARATOR)

    # Collect all log errors
    all_log_errors: list[LogError] = []
    for c in all_cases:
        all_log_errors.extend(c.log_errors)

    # Also count pipeline failures (cases with no JSON)
    pipeline_failed = [c for c in all_cases if c.pipeline_failed]

    if not all_log_errors and not pipeline_failed:
        logger.info("  No API errors, refusals, or pipeline failures found.")
        return

    # Count by type
    type_counts: dict[IssueType, int] = defaultdict(int)
    for le in all_log_errors:
        type_counts[le.error_type] += 1

    total = len(all_cases)
    affected_cases = set()
    for le in all_log_errors:
        affected_cases.add((le.experiment, le.case_id))
    for c in pipeline_failed:
        affected_cases.add((c.experiment, c.case_id))

    logger.info(f"  Cases with log-level errors: {len(affected_cases)}/{total} ({_pct(len(affected_cases), total)})")
    logger.info(f"  Pipeline failures (no output): {len(pipeline_failed)}")

    type_labels = {
        IssueType.REFUSAL: "Model refusal (sorry, cannot assist)",
        IssueType.API_NONE: "API returned None (content filter)",
        IssueType.SCHEMA_ERROR: "Pydantic schema error",
        IssueType.PIPELINE_FAILURE: "Pipeline failure (no candidates)",
    }
    for it, label in type_labels.items():
        count = type_counts.get(it, 0)
        if it == IssueType.PIPELINE_FAILURE:
            count = len(pipeline_failed)
        if count > 0:
            logger.info(f"  {label}: {count}")

    # Problematic cases: cases that fail across multiple experiments
    case_fail_experiments: dict[str, set[str]] = defaultdict(set)
    for le in all_log_errors:
        case_fail_experiments[le.case_id].add(le.experiment)
    for c in pipeline_failed:
        case_fail_experiments[c.case_id].add(c.experiment)

    repeat_cases = {
        cid: exps for cid, exps in case_fail_experiments.items() if len(exps) > 1
    }
    if repeat_cases:
        logger.info("  Problematic cases (errors in 2+ experiments):")
        for cid in sorted(repeat_cases, key=lambda x: len(repeat_cases[x]), reverse=True):
            exps = repeat_cases[cid]
            logger.info(f"    case {cid}: fails in {len(exps)} experiments")

    # By model
    model_errors: dict[str, int] = defaultdict(int)
    model_totals: dict[str, int] = defaultdict(int)
    for c in all_cases:
        model_totals[c.model] += 1
        if c.log_errors or c.pipeline_failed:
            model_errors[c.model] += 1
    if len(model_totals) > 1:
        logger.info("  By model:")
        for model in sorted(model_totals):
            err = model_errors.get(model, 0)
            tot = model_totals[model]
            logger.info(f"    {model}: {err}/{tot} ({_pct(err, tot)})")

    if verbose:
        logger.info("  All log errors:")
        for le in all_log_errors:
            logger.info(f"    [{le.experiment}] case {le.case_id}: {le.error_type.value} — {le.message}")
        if pipeline_failed:
            logger.info("  Pipeline failures (missing from JSON):")
            for c in pipeline_failed:
                logger.info(f"    [{c.experiment}] case {c.case_id}")


def _print_word_count_violations(
    all_cases: list[CaseRecord], verbose: bool, section: int
) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. WORD COUNT VIOLATION RATE")
    logger.info(SEPARATOR)

    # Exclude pipeline-failed cases
    valid_cases = [c for c in all_cases if not c.pipeline_failed]
    wc_cases = []
    for c in valid_cases:
        wc_fails = [
            f
            for f in c.failed_attempts
            if f.issue_type in (IssueType.WORD_COUNT, IssueType.COMBINED)
        ]
        if wc_fails:
            wc_cases.append(c)

    total = len(valid_cases)
    violated = len(wc_cases)
    logger.info(f"  Cases with word count violation: {violated}/{total} ({_pct(violated, total)})")

    # By model
    logger.info("  By model:")
    by_model: dict[str, list] = defaultdict(list)
    for c in valid_cases:
        by_model[c.model].append(c)
    for model in sorted(by_model):
        model_cases = by_model[model]
        model_violated = sum(
            1
            for c in model_cases
            if any(
                f.issue_type in (IssueType.WORD_COUNT, IssueType.COMBINED)
                for f in c.failed_attempts
            )
        )
        logger.info(
            f"    {model}: {model_violated}/{len(model_cases)} ({_pct(model_violated, len(model_cases))})"
        )

    # By method
    logger.info("  By method:")
    by_method: dict[str, list] = defaultdict(list)
    for c in valid_cases:
        by_method[c.method].append(c)
    for method in sorted(by_method):
        method_cases = by_method[method]
        method_violated = sum(
            1
            for c in method_cases
            if any(
                f.issue_type in (IssueType.WORD_COUNT, IssueType.COMBINED)
                for f in c.failed_attempts
            )
        )
        logger.info(
            f"    {method}: {method_violated}/{len(method_cases)} ({_pct(method_violated, len(method_cases))})"
        )

    if verbose and wc_cases:
        logger.info("  Verbose: cases with word count violations:")
        for c in wc_cases[:20]:
            wc_fail = next(
                f
                for f in c.failed_attempts
                if f.issue_type in (IssueType.WORD_COUNT, IssueType.COMBINED)
            )
            logger.info(
                f"    [{c.experiment}] case {c.case_id}: "
                f"{wc_fail.word_count} words on attempt {wc_fail.attempt_number}"
            )


def _print_correction_success(all_cases: list[CaseRecord], section: int) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. CORRECTION SUCCESS RATE")
    logger.info(SEPARATOR)

    valid_cases = [c for c in all_cases if not c.pipeline_failed]
    failed_cases = [c for c in valid_cases if not c.passed_first_try]
    if not failed_cases:
        logger.info("  All cases passed on first attempt!")
        return

    corrected = sum(1 for c in failed_cases if not c.max_retries_exceeded)
    max_retried = sum(1 for c in failed_cases if c.max_retries_exceeded)
    logger.info(f"  Cases that failed first attempt: {len(failed_cases)}")
    logger.info(
        f"  Corrected within retries:       {corrected}/{len(failed_cases)} ({_pct(corrected, len(failed_cases))})"
    )
    logger.info(
        f"  Max retries exceeded:           {max_retried}/{len(failed_cases)} ({_pct(max_retried, len(failed_cases))})"
    )

    # By model
    logger.info("  By model:")
    by_model: dict[str, list] = defaultdict(list)
    for c in failed_cases:
        by_model[c.model].append(c)
    for model in sorted(by_model):
        mc = by_model[model]
        cor = sum(1 for c in mc if not c.max_retries_exceeded)
        logger.info(f"    {model}: {cor}/{len(mc)} corrected ({_pct(cor, len(mc))})")

    # By error type
    logger.info("  By first failure type:")
    by_type: dict[IssueType, list] = defaultdict(list)
    for c in failed_cases:
        if c.failed_attempts:
            by_type[c.failed_attempts[0].issue_type].append(c)
    for issue_type in sorted(by_type, key=lambda t: t.value):
        tc = by_type[issue_type]
        cor = sum(1 for c in tc if not c.max_retries_exceeded)
        logger.info(
            f"    {issue_type.value}: {cor}/{len(tc)} corrected ({_pct(cor, len(tc))})"
        )


def _print_citation_errors(all_cases: list[CaseRecord], section: int) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. CITATION ERROR RATE")
    logger.info(SEPARATOR)

    valid_cases = [c for c in all_cases if not c.pipeline_failed]
    cite_cases = [
        c
        for c in valid_cases
        if any(
            f.issue_type
            in (IssueType.CITATION_MISSING, IssueType.CITATION_EXTRA, IssueType.COMBINED)
            for f in c.failed_attempts
        )
    ]
    total = len(valid_cases)
    logger.info(
        f"  Cases with citation errors: {len(cite_cases)}/{total} ({_pct(len(cite_cases), total)})"
    )

    missing_count = sum(
        1
        for c in valid_cases
        if any(
            f.issue_type in (IssueType.CITATION_MISSING, IssueType.COMBINED)
            for f in c.failed_attempts
        )
    )
    extra_count = sum(
        1
        for c in valid_cases
        if any(
            f.issue_type in (IssueType.CITATION_EXTRA, IssueType.COMBINED)
            for f in c.failed_attempts
        )
    )
    logger.info(f"  Essential not cited: {missing_count}")
    logger.info(f"  Extra citations:     {extra_count}")


def _print_attempts_distribution(all_cases: list[CaseRecord], section: int) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. ATTEMPTS DISTRIBUTION")
    logger.info(SEPARATOR)

    valid_cases = [c for c in all_cases if not c.pipeline_failed]
    total = len(valid_cases)
    if total == 0:
        return

    buckets = defaultdict(int)
    for c in valid_cases:
        att = min(c.total_attempts, 6)
        buckets[att] += 1

    labels = {
        1: "Attempt 1 (pass)",
        2: "Attempt 2",
        3: "Attempt 3",
        4: "Attempt 4",
        5: "Attempt 5",
        6: "Attempt 5+",
    }
    for att in sorted(labels.keys()):
        count = buckets.get(att, 0)
        bar = _bar(count, total)
        pct = _pct(count, total)
        logger.info(f"  {labels[att]:<18} {bar:<32} {count:>4} ({pct:>5})")

    # Cumulative compliance
    logger.info("  Cumulative compliance:")
    running = 0
    for att in sorted(labels.keys()):
        running += buckets.get(att, 0)
        logger.info(f"    After attempt {att if att < 6 else '5+'}: {running}/{total} ({running / total * 100:.1f}%)")


def _print_error_taxonomy(all_cases: list[CaseRecord], section: int) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. ERROR TAXONOMY (all sources)")
    logger.info(SEPARATOR)

    # JSON validation failures
    type_counts: dict[str, int] = defaultdict(int)
    for c in all_cases:
        for f in c.failed_attempts:
            type_counts[f.issue_type.value] += 1

    # Log-only errors
    for c in all_cases:
        for le in c.log_errors:
            type_counts[le.error_type.value] += 1

    # Pipeline failures
    pf_count = sum(1 for c in all_cases if c.pipeline_failed)
    if pf_count > 0:
        type_counts["pipeline_failure"] = type_counts.get("pipeline_failure", 0) + pf_count

    total = sum(type_counts.values())
    if total == 0:
        logger.info("  No errors found.")
        return

    logger.info(f"  Total errors (validation + API + pipeline): {total}")
    for error_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        pct = _pct(count, total)
        logger.info(f"  {error_type:<25} {count:>4} ({pct:>5})")


def _print_model_comparison(all_cases: list[CaseRecord], section: int) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. MODEL COMPARISON")
    logger.info(SEPARATOR)

    by_model: dict[str, list] = defaultdict(list)
    for c in all_cases:
        by_model[c.model].append(c)

    models = sorted(by_model.keys())
    if len(models) < 2:
        logger.info("  Only one model found, skipping comparison.")
        return

    col_w = 14
    header = f"  {'Metric':<30}" + "".join(f"{m:>{col_w}}" for m in models)
    logger.info(header)
    logger.info("  " + "-" * (30 + col_w * len(models)))

    def _first_try_rate(cases):
        valid = [c for c in cases if not c.pipeline_failed]
        return _pct(sum(1 for c in valid if c.passed_first_try), len(valid)) if valid else "N/A"

    def _wc_rate(cases):
        valid = [c for c in cases if not c.pipeline_failed]
        v = sum(
            1 for c in valid
            if any(f.issue_type in (IssueType.WORD_COUNT, IssueType.COMBINED) for f in c.failed_attempts)
        )
        return _pct(v, len(valid)) if valid else "N/A"

    def _cite_rate(cases):
        valid = [c for c in cases if not c.pipeline_failed]
        v = sum(
            1 for c in valid
            if any(f.issue_type in (IssueType.CITATION_MISSING, IssueType.CITATION_EXTRA, IssueType.COMBINED) for f in c.failed_attempts)
        )
        return _pct(v, len(valid)) if valid else "N/A"

    def _avg_attempts(cases):
        valid = [c for c in cases if not c.pipeline_failed]
        if not valid:
            return "N/A"
        return f"{statistics.mean(c.total_attempts for c in valid):.2f}"

    def _error_rate(cases):
        errs = sum(1 for c in cases if c.log_errors or c.pipeline_failed)
        return _pct(errs, len(cases))

    metrics = [
        ("First-try pass rate", _first_try_rate),
        ("Word count violation", _wc_rate),
        ("Citation error rate", _cite_rate),
        ("Avg attempts needed", _avg_attempts),
        ("API/refusal error rate", _error_rate),
        ("Total cases", lambda cases: str(len(cases))),
    ]

    for label, fn in metrics:
        vals = "".join(f"{fn(by_model[m]):>{col_w}}" for m in models)
        logger.info(f"  {label:<30}{vals}")


def _print_method_comparison(all_cases: list[CaseRecord], section: int) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. METHOD COMPARISON")
    logger.info(SEPARATOR)

    by_method: dict[str, list] = defaultdict(list)
    for c in all_cases:
        by_method[c.method].append(c)

    methods = sorted(by_method.keys())
    if len(methods) < 2:
        logger.info("  Only one method found, skipping comparison.")
        return

    col_w = 16
    header = f"  {'Metric':<30}" + "".join(f"{m:>{col_w}}" for m in methods)
    logger.info(header)
    logger.info("  " + "-" * (30 + col_w * len(methods)))

    def _first_try_rate(cases):
        valid = [c for c in cases if not c.pipeline_failed]
        return _pct(sum(1 for c in valid if c.passed_first_try), len(valid)) if valid else "N/A"

    def _wc_rate(cases):
        valid = [c for c in cases if not c.pipeline_failed]
        v = sum(
            1 for c in valid
            if any(f.issue_type in (IssueType.WORD_COUNT, IssueType.COMBINED) for f in c.failed_attempts)
        )
        return _pct(v, len(valid)) if valid else "N/A"

    def _cite_rate(cases):
        valid = [c for c in cases if not c.pipeline_failed]
        v = sum(
            1 for c in valid
            if any(f.issue_type in (IssueType.CITATION_MISSING, IssueType.CITATION_EXTRA, IssueType.COMBINED) for f in c.failed_attempts)
        )
        return _pct(v, len(valid)) if valid else "N/A"

    def _avg_attempts(cases):
        valid = [c for c in cases if not c.pipeline_failed]
        if not valid:
            return "N/A"
        return f"{statistics.mean(c.total_attempts for c in valid):.2f}"

    def _error_rate(cases):
        errs = sum(1 for c in cases if c.log_errors or c.pipeline_failed)
        return _pct(errs, len(cases))

    metrics = [
        ("First-try pass rate", _first_try_rate),
        ("Word count violation", _wc_rate),
        ("Citation error rate", _cite_rate),
        ("Avg attempts needed", _avg_attempts),
        ("API/refusal error rate", _error_rate),
        ("Total cases", lambda cases: str(len(cases))),
    ]

    for label, fn in metrics:
        vals = "".join(f"{fn(by_method[m]):>{col_w}}" for m in methods)
        logger.info(f"  {label:<30}{vals}")


def _print_word_count_distribution(all_cases: list[CaseRecord], section: int) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. WORD COUNT DISTRIBUTION (failed attempts)")
    logger.info(SEPARATOR)

    word_counts = []
    for c in all_cases:
        for f in c.failed_attempts:
            if f.word_count is not None:
                word_counts.append(f.word_count)

    if not word_counts:
        logger.info("  No word count violations found.")
        return

    overshoots = [wc - 75 for wc in word_counts]

    buckets = {
        "1-5 over": sum(1 for o in overshoots if 1 <= o <= 5),
        "6-10 over": sum(1 for o in overshoots if 6 <= o <= 10),
        "11-20 over": sum(1 for o in overshoots if 11 <= o <= 20),
        "21-50 over": sum(1 for o in overshoots if 21 <= o <= 50),
        "50+ over": sum(1 for o in overshoots if o > 50),
    }

    total = len(overshoots)
    logger.info("  Overshoot distribution (words over 75 limit):")
    for label, count in buckets.items():
        bar = _bar(count, total, 25)
        logger.info(f"    {label:<15} {bar:<27} {count:>3} ({_pct(count, total):>5})")

    logger.info(f"  Total violations: {total}")
    logger.info(f"  Median overshoot: {statistics.median(overshoots):.0f} words")
    logger.info(f"  Mean overshoot:   {statistics.mean(overshoots):.1f} words")
    logger.info(f"  Max overshoot:    {max(overshoots)} words ({max(word_counts)} words total)")

    valid_cases = [c for c in all_cases if not c.pipeline_failed]
    final_wcs = [c.final_word_count for c in valid_cases if c.final_word_count is not None]
    if final_wcs:
        over_limit = sum(1 for wc in final_wcs if wc > 75)
        logger.info(
            f"  Final answers still over 75 words: {over_limit}/{len(final_wcs)} ({_pct(over_limit, len(final_wcs))})"
        )
        logger.info(
            f"  Final answer word count: mean={statistics.mean(final_wcs):.1f}, "
            f"median={statistics.median(final_wcs):.0f}, max={max(final_wcs)}"
        )


def _print_latency_analysis(all_cases: list[CaseRecord], section: int) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. LATENCY ANALYSIS (from benchmark.log)")
    logger.info(SEPARATOR)

    timed = [
        c for c in all_cases if c.duration_seconds is not None and c.duration_seconds > 0
    ]
    if not timed:
        logger.info("  No timing data available.")
        return

    durations = [c.duration_seconds for c in timed]
    sorted_d = sorted(durations)
    p95_idx = int(len(sorted_d) * 0.95)

    logger.info(f"  Cases with timing data: {len(timed)}")
    logger.info(f"  Mean:   {statistics.mean(durations):.1f}s")
    logger.info(f"  Median: {statistics.median(durations):.1f}s")
    logger.info(f"  P95:    {sorted_d[min(p95_idx, len(sorted_d) - 1)]:.1f}s")
    logger.info(f"  Max:    {max(durations):.1f}s")

    by_method: dict[str, list] = defaultdict(list)
    for c in timed:
        by_method[c.method].append(c.duration_seconds)

    if len(by_method) > 1:
        logger.info("  Per-case duration by method:")
        for method in sorted(by_method):
            d = by_method[method]
            logger.info(
                f"    {method:<20} mean={statistics.mean(d):.1f}s, "
                f"median={statistics.median(d):.1f}s, n={len(d)}"
            )


def _print_crash_failures(
    experiments: dict[str, list[CaseRecord]],
    log_data_all: dict[str, dict],
    section: int,
) -> None:
    logger.info(SEPARATOR)
    logger.info(f"{section}. CRASH / FAILURE SUMMARY")
    logger.info(SEPARATOR)

    total_exp = len(experiments)
    total_cases = sum(len(cases) for cases in experiments.values())
    pipeline_failed = sum(
        1 for cases in experiments.values() for c in cases if c.pipeline_failed
    )
    max_retried = sum(
        1 for cases in experiments.values() for c in cases if c.max_retries_exceeded
    )

    logger.info(f"  Total experiments: {total_exp}")
    logger.info(f"  Total cases (incl. failed): {total_cases}")
    logger.info(f"  Pipeline failures: {pipeline_failed}")
    logger.info(f"  Max retries exceeded: {max_retried}")

    # Submission mismatches
    for exp_name, log_data in log_data_all.items():
        sm = log_data.get("submission_mismatch")
        if sm:
            logger.info(f"  Submission mismatch in {exp_name}: {sm[0]}/{sm[1]} cases submitted")


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------


def save_csv(all_cases: list[CaseRecord], output_path: Path) -> None:
    """Export per-case details to CSV."""
    rows = []
    for c in all_cases:
        wc_issues = [
            f
            for f in c.failed_attempts
            if f.issue_type in (IssueType.WORD_COUNT, IssueType.COMBINED)
        ]
        cite_issues = [
            f
            for f in c.failed_attempts
            if f.issue_type
            in (IssueType.CITATION_MISSING, IssueType.CITATION_EXTRA, IssueType.COMBINED)
        ]
        first_wc = wc_issues[0].word_count if wc_issues else None

        log_error_types = ",".join(sorted(set(le.error_type.value for le in c.log_errors))) if c.log_errors else ""

        rows.append(
            {
                "experiment": c.experiment,
                "case_id": c.case_id,
                "dataset": c.dataset,
                "model": c.model,
                "method": c.method,
                "reasoning_effort": c.reasoning_effort,
                "total_attempts": c.total_attempts,
                "passed_first_try": c.passed_first_try,
                "max_retries_exceeded": c.max_retries_exceeded,
                "pipeline_failed": c.pipeline_failed,
                "has_word_count_issue": len(wc_issues) > 0,
                "first_attempt_word_count": first_wc,
                "has_citation_issue": len(cite_issues) > 0,
                "has_refusal": any(le.error_type == IssueType.REFUSAL for le in c.log_errors),
                "has_api_none": any(le.error_type == IssueType.API_NONE for le in c.log_errors),
                "log_error_types": log_error_types,
                "final_word_count": c.final_word_count,
                "num_candidates": c.num_candidates,
                "duration_seconds": c.duration_seconds,
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    logger.info(f"Per-case analysis saved to: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _load_experiment(
    exp_dir: Path, parent_dir_name: str = ""
) -> tuple[str, dict, list[CaseRecord], dict] | None:
    """Load a single experiment directory. Returns (name, config, cases, log_result) or None."""
    config = parse_experiment_config(exp_dir, parent_dir_name)
    cases = parse_json_responses(exp_dir, config)
    exp_name = exp_dir.name
    log_result = parse_benchmark_log(exp_dir, exp_name)

    # Merge log data and detect missing cases
    new_cases = merge_log_data(cases, log_result, config, exp_name)
    cases.extend(new_cases)

    if not cases and not log_result["all_case_ids"]:
        return None

    return exp_name, config, cases, log_result


@hydra.main(config_path="../configs", config_name="log-analysis-config", version_base=None)
def main(cfg: DictConfig):
    logger.info(f"Config:\n{OmegaConf.to_yaml(cfg)}")

    output_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)

    # Expand experiment_dirs: each entry may be a directory or a glob-expandable parent
    experiment_dirs = []
    for d in cfg.experiment_dirs:
        p = Path(d)
        if p.is_dir():
            # Add all subdirectories (like shell glob outputs/2026-selected/*)
            experiment_dirs.extend(sorted(p.iterdir()))
        else:
            experiment_dirs.append(p)

    # Collect experiments
    experiments: dict[str, list[CaseRecord]] = {}
    log_data_all: dict[str, dict] = {}
    skipped = []

    logger.info(f"Loading {len(experiment_dirs)} experiment(s)...")

    for exp_dir in sorted(experiment_dirs):
        if not exp_dir.is_dir():
            continue

        # Skip ensemble directories
        if "ensemble" in exp_dir.name:
            skipped.append(exp_dir.name)
            continue

        # Determine parent dir name for dataset heuristic
        parent_name = exp_dir.parent.name if exp_dir.parent else ""

        # Check for sub-directories (e.g., 2026-03-01/21-08-28)
        json_dir = exp_dir / "results" / "response_output_with_phi"
        has_log = (exp_dir / "benchmark.log").exists()

        if not json_dir.exists() and not has_log:
            nested = list(exp_dir.glob("*/results/response_output_with_phi"))
            nested_logs = list(exp_dir.glob("*/benchmark.log"))
            if nested or nested_logs:
                sub_dirs = set()
                for n in nested:
                    sub_dirs.add(n.parent.parent)
                for n in nested_logs:
                    sub_dirs.add(n.parent)
                for sub_dir in sorted(sub_dirs):
                    result = _load_experiment(sub_dir, exp_dir.name)
                    if result:
                        ename, cfg, cases, log_result = result
                        ename = f"{exp_dir.name}/{ename}"
                        experiments[ename] = cases
                        log_data_all[ename] = log_result
                        ds = cfg["dataset"]
                        logger.info(f"  {ename}: {len(cases)} cases ({ds})")
                continue
            skipped.append(exp_dir.name)
            continue

        result = _load_experiment(exp_dir, parent_name)
        if not result:
            skipped.append(exp_dir.name)
            continue

        exp_name, config, cases, log_result = result

        # Disambiguate if same experiment name already loaded (e.g., dev + test)
        if exp_name in experiments:
            exp_name = f"{parent_name}/{exp_name}"

        experiments[exp_name] = cases
        log_data_all[exp_name] = log_result
        ds = config["dataset"]
        logger.info(
            f"  {exp_name}: {len(cases)} cases "
            f"({config['model']}, {config['method']}, {ds})"
        )

    if skipped:
        logger.info(
            f"  Skipped: {', '.join(skipped[:5])}"
            + (f" (+{len(skipped)-5} more)" if len(skipped) > 5 else "")
        )

    if not experiments:
        logger.error("No valid experiments found")
        return 1

    # Flatten all cases
    all_cases = [c for cases in experiments.values() for c in cases]

    # Group by dataset
    datasets: dict[str, list[str]] = defaultdict(list)
    for exp_name, cases in experiments.items():
        ds = cases[0].dataset if cases else "unknown"
        datasets[ds].append(exp_name)

    # Print report header
    logger.info("=" * 70)
    logger.info("LOG & RESULT ANALYSIS REPORT")
    logger.info("=" * 70)
    logger.info(f"Experiments analyzed: {len(experiments)}")
    logger.info(f"Total cases: {len(all_cases)}")
    models = sorted(set(c.model for c in all_cases))
    methods = sorted(set(c.method for c in all_cases))
    ds_names = sorted(datasets.keys())
    logger.info(f"Models: {', '.join(models)}")
    logger.info(f"Methods: {', '.join(methods)}")
    logger.info(f"Datasets: {', '.join(ds_names)}")

    # If multiple datasets, split the report
    if len(datasets) > 1:
        for ds_name in sorted(datasets.keys()):
            exp_names = datasets[ds_name]
            ds_experiments = {n: experiments[n] for n in exp_names}
            ds_cases = [c for cases in ds_experiments.values() for c in cases]
            ds_log_data = {n: log_data_all[n] for n in exp_names if n in log_data_all}

            label_map = {
                "archehr-dev": "DEV SET (archehr-dev)",
                "archehr-test-2026": "TEST SET (archehr-test-2026)",
            }
            label = label_map.get(ds_name, ds_name)
            _print_dataset_report(
                label, ds_experiments, ds_cases, ds_log_data,
                verbose=cfg.verbose,
            )
    else:
        _print_dataset_report(
            ds_names[0] if ds_names else "ALL",
            experiments, all_cases, log_data_all,
            verbose=cfg.verbose,
        )

    logger.info("=" * 70)

    # CSV export
    # Always save CSV to Hydra output directory
    csv_path = output_dir / "log_analysis.csv"
    save_csv(all_cases, csv_path)
    logger.info(f"CSV saved to: {csv_path}")

    logger.info(f"All outputs saved to: {output_dir}")
    return 0


if __name__ == "__main__":
    main()
