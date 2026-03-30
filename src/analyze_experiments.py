#!/usr/bin/env python3
"""
Analyze experiment runs and generate all analysis artifacts.

Usage:
    python src/analyze_experiments.py hydra.run.dir=outputs/experiment_analysis/
    python src/analyze_experiments.py csv=outputs/log_analysis.csv hydra.run.dir=outputs/experiment_analysis/

Generates (in outputs/experiment_analysis/):
    Figures:
    - 01_iterative_correction_effectiveness.pdf
    - 02_error_type_breakdown.pdf
    - 03_case_difficulty_dev_set.pdf
    - 04_safety_refusal_top10.pdf
    Data:
    - 15_error_analysis_latex_table.tex
    - 16_key_statistics.json
    - 17_configuration_ranking_by_pass_rate.csv
    - 18_model_comparison_metrics.csv
    - 19_cumulative_compliance_by_attempt.csv
    - 20_pipeline_factors_aggregated_stats.csv
    - 21_content_safety_failures.csv
    Each figure (05, 06, 14) also outputs a companion .csv with the same basename.
"""

import json
import logging
from pathlib import Path

import hydra
import matplotlib
from omegaconf import DictConfig, OmegaConf

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load research_vibrant style
_STYLE_PATH = Path(__file__).parent / "research_vibrant.mplstyle"
if _STYLE_PATH.exists():
    plt.style.use(str(_STYLE_PATH))

logger = logging.getLogger(__name__)


def style_legend(ax, **kwargs):
    """Place legend between title and chart area."""
    kwargs.pop("loc", None)
    kwargs.setdefault("frameon", False)
    kwargs.setdefault("ncol", 4)
    kwargs.setdefault("fontsize", 9)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), **kwargs)


def compute_error_taxonomy(df: pd.DataFrame) -> dict[str, dict]:
    """Compute error counts by type for each dataset."""
    results = {}

    for ds_name, ds_df in df.groupby("dataset"):
        total = len(ds_df)
        valid = ds_df[~ds_df["pipeline_failed"]]

        # Error counts
        wc = valid["has_word_count_issue"].sum()
        cite = valid["has_citation_issue"].sum()
        refusal = ds_df["has_refusal"].sum()
        api_none = ds_df["has_api_none"].sum()
        pipeline = ds_df["pipeline_failed"].sum()

        # Total errors (sum of all failed_attempts + log errors)
        all_errors = wc + cite + refusal + api_none + pipeline
        # Schema errors from log_error_types
        schema = 0
        for val in ds_df["log_error_types"].dropna():
            if "schema_error" in str(val):
                schema += 1

        results[ds_name] = {
            "total_cases": total,
            "valid_cases": len(valid),
            "word_count": int(wc),
            "citation": int(cite),
            "api_content_filter": int(api_none),
            "model_refusal": int(refusal),
            "pipeline_failure": int(pipeline),
            "schema_error": schema,
            "all_errors": int(all_errors) + schema,
        }

    return results


def compute_cumulative_compliance(df: pd.DataFrame) -> dict[str, list[tuple[int, float]]]:
    """Compute cumulative compliance rate by attempt number for each dataset."""
    results = {}

    for ds_name, ds_df in df.groupby("dataset"):
        valid = ds_df[~ds_df["pipeline_failed"]]
        total = len(valid)
        if total == 0:
            continue

        # Bucket attempts: 1, 2, 3, 4, 5, 6+ (capped)
        attempts = valid["total_attempts"].clip(upper=6)
        buckets = attempts.value_counts().sort_index()

        cumulative = []
        running = 0
        for att in range(1, 7):
            running += buckets.get(att, 0)
            pct = running / total * 100
            cumulative.append((att, pct))

        results[ds_name] = cumulative

    return results


def compute_word_count_stats(df: pd.DataFrame) -> dict[str, dict]:
    """Compute word count overshoot statistics for each dataset."""
    results = {}

    for ds_name, ds_df in df.groupby("dataset"):
        valid = ds_df[~ds_df["pipeline_failed"]]
        wc_cases = valid[valid["has_word_count_issue"] == True]  # noqa: E712
        overshoots = wc_cases["first_attempt_word_count"].dropna() - 75

        if len(overshoots) == 0:
            results[ds_name] = {
                "count": 0,
                "median": 0,
                "mean": 0,
                "overshoots": [],
            }
            continue

        results[ds_name] = {
            "count": len(overshoots),
            "median": float(overshoots.median()),
            "mean": float(overshoots.mean()),
            "overshoots": overshoots.tolist(),
        }

    return results


def generate_latex_table(
    df: pd.DataFrame,
    taxonomy: dict[str, dict],
    compliance: dict[str, list[tuple[int, float]]],
    wc_stats: dict[str, dict],
    output_path: Path,
) -> None:
    """Generate LaTeX table for paper (Table 2: Combined Error Analysis)."""

    # Determine dataset order: dev first, test second
    ds_order = sorted(taxonomy.keys(), key=lambda x: (0 if "dev" in x else 1, x))

    # Build short labels
    ds_labels = {}
    for ds in ds_order:
        n_exp = int(df[df["dataset"] == ds]["experiment"].nunique())
        label = "Dev" if "dev" in ds else "Test"
        ds_labels[ds] = f"{label} ({n_exp} exp)"

    ncols = len(ds_order)
    col_spec = "l" + "r" * ncols

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Error analysis and correction effectiveness across development and test sets.}")
    lines.append(r"\label{tab:error-analysis}")
    lines.append(r"\small")
    lines.append(r"\begin{tabular}{" + col_spec + "}")
    lines.append(r"\toprule")

    # Header
    header = " & ".join([""] + [ds_labels[ds] for ds in ds_order])
    lines.append(header + r" \\")
    lines.append(r"\midrule")

    # Cases
    row = ["Cases analyzed"]
    for ds in ds_order:
        row.append(str(taxonomy[ds]["total_cases"]))
    lines.append(" & ".join(row) + r" \\")

    # Cumulative compliance
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(ncols + 1) + r"}{l}{\textit{Cumulative compliance}} \\")

    attempt_labels = {1: "After attempt 1", 2: "After attempt 2", 3: "After attempt 3", 6: "Final"}
    for att, label in attempt_labels.items():
        row = [f"\\quad {label}"]
        for ds in ds_order:
            comp = compliance.get(ds, [])
            val = next((pct for a, pct in comp if a == att), None)
            if val is not None:
                row.append(f"{val:.1f}\\%")
            else:
                row.append("--")
        lines.append(" & ".join(row) + r" \\")

    # Error breakdown
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(ncols + 1) + r"}{l}{\textit{Error breakdown}} \\")

    error_rows = [
        ("Word count violation", "word_count"),
        ("API content filter", "api_content_filter"),
        ("Pipeline failure", "pipeline_failure"),
        ("Model refusal", "model_refusal"),
        ("Citation error", "citation"),
        ("Schema error", "schema_error"),
    ]

    for label, key in error_rows:
        row = [f"\\quad {label}"]
        for ds in ds_order:
            count = taxonomy[ds].get(key, 0)
            total_err = taxonomy[ds]["all_errors"]
            if count > 0:
                pct = count / total_err * 100 if total_err > 0 else 0
                row.append(f"{count} ({pct:.1f}\\%)")
            else:
                row.append("0")
        lines.append(" & ".join(row) + r" \\")

    # Word count detail
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{" + str(ncols + 1) + r"}{l}{\textit{Word count detail}} \\")

    row = ["\\quad Median overshoot"]
    for ds in ds_order:
        stats = wc_stats.get(ds, {})
        med = stats.get("median", 0)
        row.append(f"{med:.0f} words")
    lines.append(" & ".join(row) + r" \\")

    row = ["\\quad Mean overshoot"]
    for ds in ds_order:
        stats = wc_stats.get(ds, {})
        mean = stats.get("mean", 0)
        row.append(f"{mean:.1f} words")
    lines.append(" & ".join(row) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    tex = "\n".join(lines)
    output_path.write_text(tex)
    logger.info(f"LaTeX table saved to: {output_path}")
    logger.info(tex)


def log_summary_stats(df: pd.DataFrame) -> None:
    """Log key numbers for inline text in the paper."""
    logger.info("=" * 60)
    logger.info("KEY NUMBERS FOR PAPER TEXT")
    logger.info("=" * 60)

    for ds_name, ds_df in df.groupby("dataset"):
        valid = ds_df[~ds_df["pipeline_failed"]]
        n_exp = ds_df["experiment"].nunique()
        logger.info(f"{ds_name} ({n_exp} experiments, {len(ds_df)} cases):")

        # First-try pass
        pass1 = valid["passed_first_try"].sum()
        logger.info(f"  First-try pass: {pass1}/{len(valid)} ({pass1 / len(valid) * 100:.1f}%)")

        # By model
        for model, model_df in valid.groupby("model"):
            p = model_df["passed_first_try"].sum()
            wc = model_df["has_word_count_issue"].sum()
            logger.info(f"  {model}: first-try {p}/{len(model_df)} ({p / len(model_df) * 100:.1f}%), wc violations {wc}/{len(model_df)} ({wc / len(model_df) * 100:.1f}%)")

        # By method
        for method, method_df in valid.groupby("method"):
            p = method_df["passed_first_try"].sum()
            logger.info(f"  {method}: first-try {p}/{len(method_df)} ({p / len(method_df) * 100:.1f}%)")

        # Avg attempts
        mean_att = valid["total_attempts"].mean()
        logger.info(f"  Mean attempts: {mean_att:.2f}")

        # Latency
        durations = valid["duration_seconds"].dropna()
        if len(durations) > 0:
            logger.info(f"  Latency: mean={durations.mean():.1f}s, median={durations.median():.1f}s")


def _ds_label(ds_name: str) -> str:
    """Short human label for a dataset name."""
    return "dev" if "dev" in ds_name else "test"


def generate_key_numbers(
    df: pd.DataFrame,
    scores_df: pd.DataFrame | None,
    taxonomy: dict[str, dict],
    compliance: dict[str, list[tuple[int, float]]],
    wc_stats: dict[str, dict],
    output_path: Path,
) -> None:
    """Generate JSON with all key statistics for inline paper text."""
    numbers: dict = {}

    # Overall
    numbers["total_cases"] = len(df)
    numbers["total_experiments"] = int(df["experiment"].nunique())
    numbers["models"] = sorted(df["model"].dropna().unique().tolist())
    numbers["methods"] = sorted(df["method"].dropna().unique().tolist())

    # Per-dataset
    for ds_name, ds_df in df.groupby("dataset"):
        label = _ds_label(ds_name)
        valid = ds_df[~ds_df["pipeline_failed"]]
        n_exp = int(ds_df["experiment"].nunique())
        pass1 = int(valid["passed_first_try"].sum())
        total_valid = len(valid)

        numbers[f"{label}_cases"] = len(ds_df)
        numbers[f"{label}_valid_cases"] = total_valid
        numbers[f"{label}_experiments"] = n_exp
        numbers[f"{label}_first_try_pass"] = pass1
        numbers[f"{label}_first_try_pct"] = round(pass1 / total_valid * 100, 1) if total_valid else 0

        # Cumulative compliance milestones
        comp = compliance.get(ds_name, [])
        for att, pct in comp:
            att_label = f"{att}" if att < 6 else "final"
            numbers[f"{label}_compliance_after_{att_label}"] = round(pct, 1)

        # Error counts
        tax = taxonomy.get(ds_name, {})
        numbers[f"{label}_errors_total"] = tax.get("all_errors", 0)
        for key in ["word_count", "citation", "api_content_filter", "model_refusal", "pipeline_failure"]:
            numbers[f"{label}_errors_{key}"] = tax.get(key, 0)

        # Word count stats
        wcs = wc_stats.get(ds_name, {})
        numbers[f"{label}_wc_median_overshoot"] = round(wcs.get("median", 0), 1)
        numbers[f"{label}_wc_mean_overshoot"] = round(wcs.get("mean", 0), 1)
        numbers[f"{label}_wc_violation_count"] = wcs.get("count", 0)

        # Mean attempts and latency
        numbers[f"{label}_mean_attempts"] = round(float(valid["total_attempts"].mean()), 2)
        durations = valid["duration_seconds"].dropna()
        if len(durations) > 0:
            numbers[f"{label}_latency_mean"] = round(float(durations.mean()), 1)
            numbers[f"{label}_latency_median"] = round(float(durations.median()), 1)
            numbers[f"{label}_latency_p95"] = round(float(durations.quantile(0.95)), 1)

        # By model
        for model, model_df in valid.groupby("model"):
            model_key = model.replace(".", "").replace("-", "_")
            p = int(model_df["passed_first_try"].sum())
            wc = int(model_df["has_word_count_issue"].sum())
            numbers[f"{label}_{model_key}_first_try_pct"] = round(p / len(model_df) * 100, 1)
            numbers[f"{label}_{model_key}_wc_pct"] = round(wc / len(model_df) * 100, 1)

    # Best config from scores
    if scores_df is not None and len(scores_df) > 0:
        best = scores_df.iloc[0]
        numbers["best_config"] = best["configuration"]
        numbers["best_f1"] = round(float(best["overall_score"]), 2)
        numbers["num_scored_configs"] = len(scores_df)

    # Pipeline factor breakdowns
    valid = df[~df["pipeline_failed"]]
    for ds_name, ds_df in valid.groupby("dataset"):
        label = _ds_label(ds_name)

        # By method
        for method, mdf in ds_df.groupby("method"):
            key = method.replace("-", "_")
            p = mdf["passed_first_try"].sum() / len(mdf) * 100 if len(mdf) else 0
            numbers[f"{label}_method_{key}_pct"] = round(p, 1)
            numbers[f"{label}_method_{key}_n"] = len(mdf)

        # By reasoning effort
        for effort, edf in ds_df.groupby("reasoning_effort"):
            p = edf["passed_first_try"].sum() / len(edf) * 100 if len(edf) else 0
            numbers[f"{label}_reasoning_{effort}_pct"] = round(p, 1)
            numbers[f"{label}_reasoning_{effort}_n"] = len(edf)

        # By num_candidates (main values)
        for k in [0, 1, 3, 5]:
            kdf = ds_df[ds_df["num_candidates"] == k]
            if len(kdf) > 0:
                p = kdf["passed_first_try"].sum() / len(kdf) * 100
                numbers[f"{label}_k{k}_pct"] = round(p, 1)
                numbers[f"{label}_k{k}_n"] = len(kdf)

        # Latency by method
        for method, mdf in ds_df.groupby("method"):
            key = method.replace("-", "_")
            dur = mdf["duration_seconds"].dropna()
            if len(dur) > 0:
                numbers[f"{label}_latency_{key}_mean"] = round(float(dur.mean()), 1)
                numbers[f"{label}_latency_{key}_median"] = round(float(dur.median()), 1)

    # Rewrite experiment comparison
    rewrite_exp = valid[valid["experiment"].str.contains("rewrite", case=False)]
    no_rewrite_exp = valid[valid["experiment"].str.contains("no-rewrite", case=False)]
    rewrite_only = rewrite_exp[~rewrite_exp["experiment"].str.contains("no-rewrite", case=False)]
    if len(rewrite_only) > 0:
        p = rewrite_only["passed_first_try"].sum() / len(rewrite_only) * 100
        wc = int(rewrite_only["has_word_count_issue"].sum())
        dur = rewrite_only["duration_seconds"].dropna()
        numbers["rewrite_first_try_pct"] = round(p, 1)
        numbers["rewrite_wc_violations"] = wc
        numbers["rewrite_n"] = len(rewrite_only)
        if len(dur) > 0:
            numbers["rewrite_latency_mean"] = round(float(dur.mean()), 1)
    if len(no_rewrite_exp) > 0:
        p = no_rewrite_exp["passed_first_try"].sum() / len(no_rewrite_exp) * 100
        wc = int(no_rewrite_exp["has_word_count_issue"].sum())
        dur = no_rewrite_exp["duration_seconds"].dropna()
        numbers["no_rewrite_first_try_pct"] = round(p, 1)
        numbers["no_rewrite_wc_violations"] = wc
        numbers["no_rewrite_n"] = len(no_rewrite_exp)
        if len(dur) > 0:
            numbers["no_rewrite_latency_mean"] = round(float(dur.mean()), 1)

    output_path.write_text(json.dumps(numbers, indent=2))
    logger.info(f"Key numbers saved to: {output_path}")


def generate_config_ranking(
    df: pd.DataFrame,
    scores_df: pd.DataFrame | None,
    output_path: Path,
) -> None:
    """Generate CSV ranking configurations by first-try pass rate, merged with F1 scores."""
    rows = []
    for exp, exp_df in df.groupby("experiment"):
        valid = exp_df[~exp_df["pipeline_failed"]]
        if len(valid) == 0:
            continue
        pass1 = int(valid["passed_first_try"].sum())
        wc = int(valid["has_word_count_issue"].sum())
        api = int(exp_df["has_api_none"].sum())
        refusal = int(exp_df["has_refusal"].sum())
        pipeline = int(exp_df["pipeline_failed"].sum())
        rows.append({
            "experiment": exp,
            "dataset": exp_df["dataset"].iloc[0],
            "model": exp_df["model"].iloc[0],
            "method": exp_df["method"].iloc[0],
            "reasoning_effort": exp_df["reasoning_effort"].iloc[0] if "reasoning_effort" in exp_df.columns else "",
            "num_candidates": int(exp_df["num_candidates"].max()) if "num_candidates" in exp_df.columns else 1,
            "total_cases": len(exp_df),
            "valid_cases": len(valid),
            "first_try_pass": pass1,
            "first_try_pct": round(pass1 / len(valid) * 100, 1),
            "word_count_violations": wc,
            "api_content_filter": api,
            "model_refusal": refusal,
            "pipeline_failure": pipeline,
            "mean_attempts": round(float(valid["total_attempts"].mean()), 2),
            "mean_duration_s": round(float(valid["duration_seconds"].dropna().mean()), 1) if len(valid["duration_seconds"].dropna()) > 0 else None,
        })

    ranking = pd.DataFrame(rows).sort_values("first_try_pct", ascending=False)

    # Merge with official scores if available
    if scores_df is not None and len(scores_df) > 0:
        score_cols = ["configuration", "overall_score", "strict_micro_f1", "lenient_micro_f1"]
        available = [c for c in score_cols if c in scores_df.columns]
        scores_slim = scores_df[available].copy()
        ranking = ranking.merge(scores_slim, left_on="experiment", right_on="configuration", how="left")
        if "configuration" in ranking.columns:
            ranking.drop(columns=["configuration"], inplace=True)

    ranking.to_csv(output_path, index=False)
    logger.info(f"Config ranking saved to: {output_path} ({len(ranking)} configs)")


def generate_model_comparison(df: pd.DataFrame, output_path: Path) -> None:
    """Generate CSV comparing models across key metrics, per dataset."""
    rows = []
    for ds_name, ds_df in df.groupby("dataset"):
        valid = ds_df[~ds_df["pipeline_failed"]]
        for model, mdf in valid.groupby("model"):
            pass1 = int(mdf["passed_first_try"].sum())
            wc = int(mdf["has_word_count_issue"].sum())
            cite = int(mdf["has_citation_issue"].sum())
            durations = mdf["duration_seconds"].dropna()
            rows.append({
                "dataset": _ds_label(ds_name),
                "model": model,
                "cases": len(mdf),
                "first_try_pass": pass1,
                "first_try_pct": round(pass1 / len(mdf) * 100, 1),
                "word_count_violations": wc,
                "wc_pct": round(wc / len(mdf) * 100, 1),
                "citation_errors": cite,
                "mean_attempts": round(float(mdf["total_attempts"].mean()), 2),
                "latency_mean_s": round(float(durations.mean()), 1) if len(durations) > 0 else None,
                "latency_median_s": round(float(durations.median()), 1) if len(durations) > 0 else None,
            })

    pd.DataFrame(rows).to_csv(output_path, index=False)
    logger.info(f"Model comparison saved to: {output_path}")


def generate_cumulative_csv(
    compliance: dict[str, list[tuple[int, float]]],
    output_path: Path,
) -> None:
    """Generate CSV of cumulative compliance rates by attempt number."""
    rows = []
    for ds_name, comp in compliance.items():
        label = _ds_label(ds_name)
        for att, pct in comp:
            rows.append({
                "dataset": label,
                "after_attempt": att if att < 6 else "5+",
                "cumulative_compliance_pct": round(pct, 1),
            })

    pd.DataFrame(rows).to_csv(output_path, index=False)
    logger.info(f"Cumulative compliance saved to: {output_path}")


def generate_content_safety_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Export content safety failure cases (API filter and model refusal) as CSV."""
    rows = []
    for failure_type, col in [("api_content_filter", "has_api_none"), ("model_refusal", "has_refusal")]:
        cases = df[df[col] == True]  # noqa: E712
        for case_id, case_df in cases.groupby("case_id"):
            ds = _ds_label(case_df["dataset"].iloc[0])
            n_affected = int(case_df["experiment"].nunique())
            n_total = int(df[(df["case_id"] == case_id) & (df["dataset"] == case_df["dataset"].iloc[0])]["experiment"].nunique())
            rows.append({
                "case_id": case_id,
                "dataset": ds,
                "failure_type": failure_type,
                "experiments_affected": n_affected,
                "total_experiments_for_case": n_total,
                "pct_experiments_affected": round(n_affected / n_total * 100, 1) if n_total > 0 else 0,
            })
    pd.DataFrame(rows).to_csv(output_path, index=False)
    logger.info(f"Content safety CSV saved to: {output_path}")


def _save_fig(fig, output_dir: Path, basename: str) -> None:
    """Save figure as PDF + PNG and close."""
    fig.savefig(output_dir / f"{basename}.pdf")
    fig.savefig(output_dir / f"{basename}.png")
    plt.close(fig)


def _save_csv(data, output_dir: Path, basename: str) -> None:
    """Save dataframe or list-of-dicts as CSV alongside a figure."""
    df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    path = output_dir / f"{basename}.csv"
    df.to_csv(path, index=False)


def generate_combined_figures(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate pooled (dev+test) compliance curve (05) and error taxonomy (06)."""
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    valid = df[~df["pipeline_failed"]]
    total_valid = len(valid)
    if total_valid == 0:
        return

    # --- 05: Pooled compliance curve ---
    attempts = valid["total_attempts"].clip(upper=6)
    buckets = attempts.value_counts().sort_index()
    cum_attempts = []
    running = 0
    for att in range(1, 7):
        running += buckets.get(att, 0)
        cum_attempts.append((att, running / total_valid * 100))

    fig, ax = plt.subplots(figsize=(6, 4))
    xs = [a if a < 6 else 6 for a, _ in cum_attempts]
    ys = [p for _, p in cum_attempts]
    ax.plot(xs, ys, "o-", color=colors[0], markersize=8, linewidth=2.5)
    # Annotate first and last points
    ax.annotate(f"{ys[0]:.0f}%", (xs[0], ys[0]),
                textcoords="offset points", xytext=(-8, -14), fontsize=8, color=colors[0])
    if ys[-1] >= 99.9:
        ax.annotate("100%", (xs[-1], ys[-1]),
                    textcoords="offset points", xytext=(5, -10), fontsize=8, color=colors[0])
    ax.set_xlabel("Attempt number")
    ax.set_ylabel("Cumulative compliance (%)")
    ax.set_xticks([1, 2, 3, 4, 5, 6])
    ax.set_xticklabels(["1", "2", "3", "4", "5", "5+"])
    ax.set_ylim(55, 105)
    ax.set_title("Iterative Correction Effectiveness", pad=6)
    _save_fig(fig, output_dir, "01_iterative_correction_effectiveness")
    _save_csv(
        [{"attempt": a if a < 6 else "5+", "cumulative_compliance_pct": round(p, 1)} for a, p in cum_attempts],
        output_dir,
        "01_iterative_correction_effectiveness",
    )
    logger.info(f"Figure saved to: {output_dir / '01_iterative_correction_effectiveness'}.{{pdf,png}}")

    # --- 02: Error type breakdown ---
    all_errors = {
        "word_count": int(valid["has_word_count_issue"].sum()),
        "citation": int(valid["has_citation_issue"].sum()),
        "model_refusal": int(df["has_refusal"].sum()),
        "api_content_filter": int(df["has_api_none"].sum()),
        "pipeline_failure": int(df["pipeline_failed"].sum()),
    }
    schema = sum(1 for v in df["log_error_types"].dropna() if "schema_error" in str(v))
    all_errors["schema_error"] = schema
    total_err = sum(all_errors.values())

    if total_err > 0:
        error_types = [
            ("Word count", "word_count"),
            ("Citation", "citation"),
            ("Model refusal", "model_refusal"),
            ("API content filter", "api_content_filter"),
            ("Pipeline failure", "pipeline_failure"),
            ("Schema error", "schema_error"),
        ]
        # Sort descending so most-frequent error is at top after invert_yaxis
        error_types = sorted(error_types, key=lambda e: all_errors[e[1]], reverse=True)
        fig, ax = plt.subplots(figsize=(7, 3.5))
        labels = [e[0] for e in error_types]
        pcts = [all_errors[e[1]] / total_err * 100 for e in error_types]
        counts = [all_errors[e[1]] for e in error_types]
        y = np.arange(len(labels))
        bars = ax.barh(y, pcts, color=colors[0])
        for j, bar in enumerate(bars):
            if counts[j] > 0:
                ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
                        f"{pcts[j]:.1f}%", va="center", fontsize=8, color="#666666")
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.set_xlabel("")
        ax.tick_params(axis="x", bottom=False, labelbottom=False)
        ax.set_xlim(0, max(pcts) * 1.2)
        ax.set_title("Constraint Violations by Type", pad=6)
        ax.invert_yaxis()
        _save_fig(fig, output_dir, "02_error_type_breakdown")
        _save_csv(
            [{"error_type": e[0], "count": all_errors[e[1]], "pct_of_all_errors": round(all_errors[e[1]] / total_err * 100, 1)} for e in error_types],
            output_dir,
            "02_error_type_breakdown",
        )
        logger.info(f"Figure saved to: {output_dir / '02_error_type_breakdown'}.{{pdf,png}}")


def generate_case_difficulty(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate per-case first-try pass rate bar chart (dev set, pooled across configs)."""
    dev_df = df[df["dataset"].str.contains("dev")].copy()
    if len(dev_df) == 0:
        return

    valid = dev_df[~dev_df["pipeline_failed"]]

    # Per-case pass rate pooled across all dev experiments
    case_stats = (
        valid.groupby("case_id")
        .agg(n_runs=("passed_first_try", "count"), pass_rate=("passed_first_try", "mean"))
        .reset_index()
    )
    case_stats["pass_pct"] = case_stats["pass_rate"] * 100
    # Sort ascending so easiest cases (highest pass rate) appear at top of chart
    case_stats = case_stats.sort_values("pass_pct", ascending=True).reset_index(drop=True)

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    fig, ax = plt.subplots(figsize=(5, 6))

    y = np.arange(len(case_stats))
    bars = ax.barh(y, case_stats["pass_pct"], color=colors[0], height=0.7)
    for bar, val in zip(bars, case_stats["pass_pct"]):
        ax.text(val + 0.8, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=8, color="#666666")

    ax.set_yticks(y)
    ax.set_yticklabels([f"Case {int(c)}" for c in case_stats["case_id"]], fontsize=8)
    ax.set_xlabel("")
    ax.tick_params(axis="x", bottom=False, labelbottom=False)
    ax.set_xlim(0, 100 * 1.2)
    ax.set_title("Per-Case Difficulty", pad=6)

    fig.tight_layout()
    _save_csv(
        case_stats[["case_id", "n_runs", "pass_pct"]].rename(columns={"pass_pct": "first_try_pass_rate_pct"}),
        output_dir,
        "03_case_difficulty_dev_set",
    )
    _save_fig(fig, output_dir, "03_case_difficulty_dev_set")
    logger.info(f"Figure saved to: {output_dir / '03_case_difficulty_dev_set'}.{{pdf,png}}")


def generate_safety_figure(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate top-10 cases by content safety and model refusal issues (dev and test)."""
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    # Per-case, per-dataset safety counts as % of experiments for that case
    rows = []
    for ds_name, ds_df in df.groupby("dataset"):
        ds_label = _ds_label(ds_name)
        for case_id, case_df in ds_df.groupby("case_id"):
            n_exps = int(case_df["experiment"].nunique())
            api_n = int(case_df["has_api_none"].sum())
            refusal_n = int(case_df["has_refusal"].sum())
            if api_n + refusal_n > 0:
                rows.append({
                    "case_id": case_id,
                    "dataset": ds_label,
                    "n_experiments": n_exps,
                    "api_content_filter": api_n,
                    "api_pct": round(api_n / n_exps * 100, 1),
                    "model_refusal": refusal_n,
                    "refusal_pct": round(refusal_n / n_exps * 100, 1),
                    "total": api_n + refusal_n,
                    "total_pct": round((api_n + refusal_n) / n_exps * 100, 1),
                })

    if not rows:
        logger.info("No safety/refusal issues found; skipping figure 04.")
        return

    issue_df = pd.DataFrame(rows)

    # Top 10 cases by total count
    top_cases = (
        issue_df.groupby("case_id")["total"].sum()
        .nlargest(10)
        .index.tolist()
    )
    issue_df = issue_df[issue_df["case_id"].isin(top_cases)].copy()

    # Sort ascending so highest appears at top
    case_order = issue_df.sort_values("total_pct", ascending=True)["case_id"].tolist()

    fig, ax = plt.subplots(figsize=(6, max(4, len(case_order) * 0.55 + 1.5)))
    y = np.arange(len(case_order))

    total_vals = [issue_df.loc[issue_df["case_id"] == c, "total_pct"].iloc[0] for c in case_order]
    bars = ax.barh(y, total_vals, color=colors[0], height=0.7)
    for bar, val in zip(bars, total_vals):
        ax.text(val + 0.8, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=8, color="#666666")

    ax.set_yticks(y)
    ax.set_yticklabels([f"Case {int(c)}" for c in case_order], fontsize=8)
    ax.set_xlabel("")
    ax.tick_params(axis="x", bottom=False, labelbottom=False)
    ax.set_xlim(0, max(total_vals) * 1.2)
    ax.set_title("Refusal Rate by Case", pad=6)
    fig.tight_layout()
    _save_csv(issue_df, output_dir, "04_safety_refusal_top10")
    _save_fig(fig, output_dir, "04_safety_refusal_top10")
    logger.info(f"Figure saved to: {output_dir / '04_safety_refusal_top10'}.{{pdf,png}}")


def compute_pipeline_factors(df: pd.DataFrame) -> pd.DataFrame:
    """Compute aggregated stats by pipeline factor (method, reasoning_effort, num_candidates)."""
    valid = df[~df["pipeline_failed"]].copy()
    rows = []

    factors = [
        ("method", "method"),
        ("reasoning_effort", "reasoning_effort"),
        ("num_candidates", "num_candidates"),
        ("model", "model"),
    ]

    for factor_name, col in factors:
        for ds_name, ds_df in valid.groupby("dataset"):
            ds_label = _ds_label(ds_name)
            for val, gdf in ds_df.groupby(col):
                if len(gdf) == 0:
                    continue
                # Skip edge-case k values from content-filtered candidates
                if col == "num_candidates" and val not in (0, 1, 3, 5):
                    continue
                durations = gdf["duration_seconds"].dropna()
                rows.append({
                    "factor": factor_name,
                    "value": str(val),
                    "dataset": ds_label,
                    "n_cases": len(gdf),
                    "first_try_pct": round(gdf["passed_first_try"].sum() / len(gdf) * 100, 1),
                    "wc_violation_pct": round(gdf["has_word_count_issue"].sum() / len(gdf) * 100, 1),
                    "mean_attempts": round(float(gdf["total_attempts"].mean()), 2),
                    "mean_latency_s": round(float(durations.mean()), 1) if len(durations) > 0 else None,
                    "median_latency_s": round(float(durations.median()), 1) if len(durations) > 0 else None,
                })

    return pd.DataFrame(rows)


def generate_readme(output_dir: Path) -> None:
    """Generate README index of all files in the output directory."""
    descriptions = {
        "README.md": "This file — index of all artifacts",
        "01_iterative_correction_effectiveness.pdf": "Figure: cumulative compliance rate over correction attempts (dev+test pooled)",
        "01_iterative_correction_effectiveness.png": "PNG version",
        "02_error_type_breakdown.pdf": "Figure: error type distribution by category (dev+test pooled)",
        "02_error_type_breakdown.png": "PNG version",
        "03_case_difficulty_dev_set.pdf": "Figure: per-case first-try pass rate on the dev set (bar chart, sorted by difficulty)",
        "03_case_difficulty_dev_set.png": "PNG version",
        "04_safety_refusal_top10.pdf": "Figure: top-10 cases by content safety and model refusal issues (grouped bar, dev and test)",
        "04_safety_refusal_top10.png": "PNG version",
        "15_error_analysis_latex_table.tex": "LaTeX table: error type breakdown and cumulative compliance (for paper)",
        "16_key_statistics.json": "Machine-readable JSON of all key statistics for inline paper text",
        "17_configuration_ranking_by_pass_rate.csv": "Per-configuration metrics and F1 scores sorted by first-try pass rate",
        "18_model_comparison_metrics.csv": "GPT-5.1 vs GPT-5.2 head-to-head metrics on dev and test sets",
        "19_cumulative_compliance_by_attempt.csv": "Cumulative compliance rate at each correction attempt (dev and test)",
        "20_pipeline_factors_aggregated_stats.csv": "Aggregated stats by pipeline factor: method, reasoning effort, candidate count k, model",
        "21_content_safety_failures.csv": "Per-case content safety failures: API content filter and model refusal instances with experiment counts",
        "01_iterative_correction_effectiveness.csv": "Data: cumulative compliance by attempt",
        "02_error_type_breakdown.csv": "Data: error type distribution",
        "03_case_difficulty_dev_set.csv": "Data: per-case first-try pass rate pooled across dev configurations",
        "04_safety_refusal_top10.csv": "Data: per-case content safety and refusal counts for top-10 affected cases",
    }

    lines = ["# Experiment Analysis Artifacts", ""]
    lines.append("Generated by `src/analyze_experiments.py` from `outputs/log_analysis.csv`.")
    lines.append("Regenerate: `python src/analyze_experiments.py`")
    lines.append("")

    lines.append("## Figures")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    for f in sorted(output_dir.glob("*.pdf")):
        desc = descriptions.get(f.name, "")
        lines.append(f"| `{f.name}` | {desc} |")
    lines.append("")

    lines.append("## Data")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    for ext in ["*.csv", "*.json", "*.tex"]:
        for f in sorted(output_dir.glob(ext)):
            desc = descriptions.get(f.name, "")
            lines.append(f"| `{f.name}` | {desc} |")
    lines.append("")

    (output_dir / "README.md").write_text("\n".join(lines))
    logger.info(f"README saved to: {output_dir / 'README.md'}")


@hydra.main(config_path="../configs", config_name="experiment-analysis-config", version_base=None)
def main(cfg: DictConfig):
    logger.info(f"Config:\n{OmegaConf.to_yaml(cfg)}")

    csv_path = Path(cfg.csv)
    scores_path = Path(cfg.scores)
    output_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)

    if not csv_path.exists():
        logger.error(f"{csv_path} not found. Run analyze_logs.py first.")
        return 1

    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} cases from {csv_path}")
    logger.info(f"Datasets: {sorted(df['dataset'].unique())}")
    logger.info(f"Experiments: {df['experiment'].nunique()}")

    # Load scores (optional)
    scores_df = None
    if scores_path.exists():
        scores_df = pd.read_csv(scores_path).sort_values("overall_score", ascending=False).reset_index(drop=True)
        logger.info(f"Loaded {len(scores_df)} scored configs from {scores_path}")

    # Compute aggregates
    taxonomy = compute_error_taxonomy(df)
    compliance = compute_cumulative_compliance(df)
    wc_stats = compute_word_count_stats(df)

    # LaTeX table (15)
    generate_latex_table(
        df, taxonomy, compliance, wc_stats,
        output_dir / "15_error_analysis_latex_table.tex",
    )

    # Figures (01, 02, 03, 04)
    generate_combined_figures(df, output_dir)
    generate_case_difficulty(df, output_dir)
    generate_safety_figure(df, output_dir)

    # Data exports (16–21)
    generate_key_numbers(df, scores_df, taxonomy, compliance, wc_stats,
                         output_dir / "16_key_statistics.json")
    generate_config_ranking(df, scores_df,
                            output_dir / "17_configuration_ranking_by_pass_rate.csv")
    generate_model_comparison(df, output_dir / "18_model_comparison_metrics.csv")
    generate_cumulative_csv(compliance, output_dir / "19_cumulative_compliance_by_attempt.csv")
    factors_df = compute_pipeline_factors(df)
    factors_df.to_csv(output_dir / "20_pipeline_factors_aggregated_stats.csv", index=False)
    logger.info(f"Pipeline factors saved to: {output_dir / '20_pipeline_factors_aggregated_stats.csv'}")
    generate_content_safety_csv(df, output_dir / "21_content_safety_failures.csv")

    # README index (must be last — lists all files present)
    generate_readme(output_dir)

    # Log summary stats
    log_summary_stats(df)

    logger.info(f"All outputs saved to: {output_dir}")
    return 0


if __name__ == "__main__":
    main()
