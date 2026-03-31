#!/usr/bin/env python3
"""
Linguistic Comparison: Model vs. Clinician Answers for ArchEHR-QA.

Literature-grounded analysis comparing AI-generated medical answers to
clinician-written reference answers across 7 dimensions:
  1. Lexical features (TTR, MTLD, hapax legomena)
  2. Syntactic features (POS distributions, parse depth, sentence patterns)
  3. Readability (Flesch-Kincaid, Coleman-Liau)
  4. Stylistic features (passive voice, function words, pronouns)
  5. Sentiment & tone (polarity, reassurance, warnings)
  6. Clinical communication (hedging, terminology, connectives)
  7. Variability analysis (cross-case variance comparison)

References:
  - Culda et al. 2025 (Comparative linguistic analysis framework)
  - Stelmakh et al. 2024 (Human Variability vs. Machine Consistency)
  - Bagdasarov & Alves 2025 (Like a Human?)
  - Contrasting Linguistic Patterns 2024
  - Tercon 2025 (Linguistic Characteristics of AI-Generated Text: A Survey)

Usage:
    # Single config:
    python src/linguistic_analysis.py \\
      submissions='[outputs/2026-selected/gpt-5.1-answer-first-v4-med-k3/results/submission_subtask3_with_phi.json]' \\
      labels='[Two-Step]' \\
      hydra.run.dir=outputs/linguistic_analysis/

    # All configs:
    python src/linguistic_analysis.py \\
      all_configs=outputs/2026-selected/ \\
      hydra.run.dir=outputs/linguistic_analysis_all/
"""

import json
import logging
import math
import re
import statistics
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
_STYLE_PATH = Path(__file__).resolve().parent / "research_vibrant.mplstyle"
if _STYLE_PATH.exists():
    plt.style.use(str(_STYLE_PATH))
import numpy as np
import pandas as pd
import hydra
import spacy
import textstat
from omegaconf import DictConfig, OmegaConf
from scipy import stats
from textblob import TextBlob

logger = logging.getLogger(__name__)

# Paul Tol Vibrant palette from the style
_COLORS = plt.rcParams["axes.prop_cycle"].by_key()["color"]


def _clean_label(raw: str) -> str:
    """Turn underscore feature names into readable labels.

    e.g. 'avg_word_length' -> 'Avg Word Length',
         'flesch_kincaid_grade' -> 'FK Grade',
         'ttr' -> 'TTR'.
    """
    _ABBREVS = {
        "ttr": "TTR",
        "mtld": "MTLD",
        "fk": "FK",
        "flesch_kincaid_grade": "FK Grade",
        "flesch_reading_ease": "FK Reading Ease",
        "coleman_liau": "Coleman-Liau",
        "avg_word_length": "Avg Word Len",
        "avg_sent_length": "Avg Sent Len",
        "avg_parse_depth": "Avg Parse Depth",
        "sent_length_std": "Sent Len Std",
        "opener_diversity": "Opener Diversity",
        "passive_voice_ratio": "Passive Voice",
        "function_word_pct": "Function Words",
        "adverb_pct": "Adverb %",
        "adjective_pct": "Adjective %",
        "noun_ratio": "Noun Ratio",
        "verb_ratio": "Verb Ratio",
        "adj_ratio": "Adj Ratio",
        "adv_ratio": "Adv Ratio",
        "det_ratio": "Det Ratio",
        "adp_ratio": "Adp Ratio",
        "pron_ratio": "Pronoun Ratio",
        "hapax_ratio": "Hapax Ratio",
        "word_count": "Word Count",
        "unique_words": "Unique Words",
        "sentence_count": "Sentence Count",
        "the_patient_count": "\"The Patient\"",
        "first_person_pronouns": "1st Person Pron",
        "second_person_pronouns": "2nd Person Pron",
        "third_person_pronouns": "3rd Person Pron",
        "polarity": "Polarity",
        "subjectivity": "Subjectivity",
        "reassurance_count": "Reassurance",
        "warning_count": "Warnings",
        "hedge_epistemic": "Hedge (Epistemic)",
        "hedge_evidential": "Hedge (Evidential)",
        "total_hedging": "Total Hedging",
        "certainty_markers": "Certainty",
        "hedge_certainty_ratio": "Hedge/Certainty",
        "causal_connectives": "Causal Conn",
        "temporal_connectives": "Temporal Conn",
        "contrastive_connectives": "Contrastive Conn",
        "total_connectives": "Total Conn",
        "meta_referential": "Meta-Referential",
        "medical_abbreviations": "Med Abbreviations",
        "non_ascii": "Non-ASCII",
        "budget_utilization": "Budget Util",
    }
    if raw in _ABBREVS:
        return _ABBREVS[raw]
    return raw.replace("_", " ").title()


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_reference_answers(path: str) -> dict[str, str]:
    """Load clinician reference answers keyed by case_id."""
    with open(path) as f:
        data = json.load(f)
    return {item["case_id"]: item["clinician_answer_without_citations"] for item in data}


def load_model_answers(path: str) -> dict[str, str]:
    """Load model submission answers keyed by case_id."""
    with open(path) as f:
        data = json.load(f)
    return {item["case_id"]: item["prediction"] for item in data}


def discover_all_configs(base_dir: str) -> list[Path]:
    """Find all submission_subtask3_with_phi.json files in config subdirectories."""
    base = Path(base_dir)
    paths = sorted(base.glob("*/results/submission_subtask3_with_phi.json"))
    return paths


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def split_sentences_simple(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def get_words(text: str) -> list[str]:
    return [w.lower() for w in text.split() if re.search(r"[a-zA-Z]", w)]


# ---------------------------------------------------------------------------
# Category 1: Lexical Features
# ---------------------------------------------------------------------------

def compute_mtld(words: list[str], threshold: float = 0.72) -> float:
    if len(words) < 10:
        return 0.0

    def _mtld_forward(word_list):
        factors = 0.0
        seg_types = set()
        seg_tokens = 0
        for w in word_list:
            seg_types.add(w)
            seg_tokens += 1
            ttr = len(seg_types) / seg_tokens
            if ttr <= threshold:
                factors += 1
                seg_types = set()
                seg_tokens = 0
        if seg_tokens > 0:
            ttr = len(seg_types) / seg_tokens
            factors += (1.0 - ttr) / (1.0 - threshold)
        return len(word_list) / factors if factors > 0 else len(word_list)

    forward = _mtld_forward(words)
    backward = _mtld_forward(list(reversed(words)))
    return (forward + backward) / 2.0


def compute_lexical_features(text: str) -> dict:
    words = get_words(text)
    word_count = len(words)
    unique_words = set(words)
    unique_count = len(unique_words)
    ttr = unique_count / word_count if word_count > 0 else 0.0
    freq = Counter(words)
    hapax = sum(1 for w, c in freq.items() if c == 1)
    avg_word_len = statistics.mean([len(w) for w in words]) if words else 0.0
    mtld = compute_mtld(words)

    return {
        "lex_word_count": word_count,
        "lex_budget_utilization": word_count / 75.0,
        "lex_unique_words": unique_count,
        "lex_ttr": ttr,
        "lex_hapax_legomena": hapax,
        "lex_hapax_ratio": hapax / word_count if word_count > 0 else 0.0,
        "lex_avg_word_length": avg_word_len,
        "lex_mtld": mtld,
    }


# ---------------------------------------------------------------------------
# Category 2: Syntactic Features
# ---------------------------------------------------------------------------

def compute_syntactic_features(text: str, nlp) -> dict:
    doc = nlp(text)
    sentences = list(doc.sents)
    n_sents = len(sentences)
    sent_lengths = [len([t for t in s if not t.is_space]) for s in sentences]
    avg_sent_len = statistics.mean(sent_lengths) if sent_lengths else 0.0
    sent_len_std = statistics.stdev(sent_lengths) if len(sent_lengths) > 1 else 0.0

    total_tokens = len([t for t in doc if not t.is_space and not t.is_punct])
    pos_counts = Counter(t.pos_ for t in doc if not t.is_space and not t.is_punct)

    def pos_ratio(pos_tag):
        return pos_counts.get(pos_tag, 0) / total_tokens if total_tokens > 0 else 0.0

    def tree_depth(token):
        depth = 0
        current = token
        while current.head != current:
            depth += 1
            current = current.head
        return depth

    max_depths = []
    for sent in sentences:
        depths = [tree_depth(t) for t in sent]
        max_depths.append(max(depths) if depths else 0)
    avg_parse_depth = statistics.mean(max_depths) if max_depths else 0.0

    openers = []
    for sent in sentences:
        tokens = [t.text.lower() for t in sent if not t.is_space][:3]
        openers.append(" ".join(tokens))
    unique_openers = len(set(openers))
    opener_diversity = unique_openers / n_sents if n_sents > 0 else 0.0

    return {
        "syn_sentence_count": n_sents,
        "syn_avg_sent_length": avg_sent_len,
        "syn_sent_length_std": sent_len_std,
        "syn_noun_ratio": pos_ratio("NOUN"),
        "syn_verb_ratio": pos_ratio("VERB"),
        "syn_adj_ratio": pos_ratio("ADJ"),
        "syn_adv_ratio": pos_ratio("ADV"),
        "syn_det_ratio": pos_ratio("DET"),
        "syn_adp_ratio": pos_ratio("ADP"),
        "syn_pron_ratio": pos_ratio("PRON"),
        "syn_avg_parse_depth": avg_parse_depth,
        "syn_opener_diversity": opener_diversity,
    }


# ---------------------------------------------------------------------------
# Category 3: Readability
# ---------------------------------------------------------------------------

def compute_readability(text: str) -> dict:
    return {
        "read_flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "read_flesch_reading_ease": textstat.flesch_reading_ease(text),
        "read_coleman_liau": textstat.coleman_liau_index(text),
    }


# ---------------------------------------------------------------------------
# Category 4: Stylistic Features
# ---------------------------------------------------------------------------

FUNCTION_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "can", "could", "must", "of", "in", "to",
    "for", "with", "on", "at", "from", "by", "as", "into", "through",
    "during", "before", "after", "above", "below", "between", "and", "but",
    "or", "nor", "not", "so", "yet", "both", "either", "neither", "each",
    "every", "all", "any", "few", "more", "most", "other", "some", "such",
    "no", "only", "own", "same", "than", "too", "very", "just", "also",
    "that", "this", "these", "those", "it", "its", "he", "she", "they",
    "them", "his", "her", "their", "my", "your", "our", "who", "which",
    "what", "where", "when", "how", "if", "then", "there", "here",
}


def compute_stylistic_features(text: str, nlp) -> dict:
    doc = nlp(text)
    sentences = list(doc.sents)
    n_sents = len(sentences)

    passive_sents = 0
    for sent in sentences:
        for token in sent:
            if token.dep_ in ("nsubjpass", "auxpass"):
                passive_sents += 1
                break
    passive_ratio = passive_sents / n_sents if n_sents > 0 else 0.0

    words = get_words(text)
    func_word_count = sum(1 for w in words if w in FUNCTION_WORDS)
    func_word_pct = func_word_count / len(words) if words else 0.0

    total_tokens = len([t for t in doc if not t.is_space and not t.is_punct])
    pos_counts = Counter(t.pos_ for t in doc if not t.is_space and not t.is_punct)
    adv_pct = pos_counts.get("ADV", 0) / total_tokens if total_tokens > 0 else 0.0
    adj_pct = pos_counts.get("ADJ", 0) / total_tokens if total_tokens > 0 else 0.0

    pronoun_counts = Counter()
    for token in doc:
        low = token.text.lower()
        if low in ("i", "me", "my", "mine", "myself"):
            pronoun_counts["first_person"] += 1
        elif low in ("you", "your", "yours", "yourself"):
            pronoun_counts["second_person"] += 1
        elif low in ("he", "she", "him", "her", "his", "hers", "himself", "herself"):
            pronoun_counts["third_person_singular"] += 1
        elif low in ("they", "them", "their", "theirs", "themselves"):
            pronoun_counts["third_person_plural"] += 1

    the_patient_count = len(re.findall(r"\bthe patient\b", text, re.IGNORECASE))

    return {
        "sty_passive_voice_ratio": passive_ratio,
        "sty_function_word_pct": func_word_pct,
        "sty_adverb_pct": adv_pct,
        "sty_adjective_pct": adj_pct,
        "sty_first_person_pronouns": pronoun_counts.get("first_person", 0),
        "sty_second_person_pronouns": pronoun_counts.get("second_person", 0),
        "sty_third_person_pronouns": (
            pronoun_counts.get("third_person_singular", 0)
            + pronoun_counts.get("third_person_plural", 0)
        ),
        "sty_the_patient_count": the_patient_count,
    }


# ---------------------------------------------------------------------------
# Category 5: Sentiment & Tone
# ---------------------------------------------------------------------------

REASSURANCE_PATTERNS = [
    r"\bnormal\b", r"\bexpected\b", r"\bcommon\b", r"\btypical\b",
    r"\bwill improve\b", r"\bwill decrease\b", r"\bshould resolve\b",
    r"\bstable\b", r"\bimproved\b", r"\brecovering\b",
    r"\bno complications\b", r"\bno concerns\b",
]

WARNING_PATTERNS = [
    r"\breport\b", r"\bshould\b", r"\bimportant to\b", r"\bseek\b",
    r"\bconcerning\b", r"\bemergency\b", r"\bimmediately\b",
    r"\bworsen(?:s|ing)?\b", r"\bfollow[\s-]?up\b",
    r"\bwatch for\b", r"\bmonitor\b", r"\bcontact\b",
]


def compute_sentiment_tone(text: str) -> dict:
    blob = TextBlob(text)
    text_lower = text.lower()
    reassurance_count = sum(len(re.findall(p, text_lower)) for p in REASSURANCE_PATTERNS)
    warning_count = sum(len(re.findall(p, text_lower)) for p in WARNING_PATTERNS)
    return {
        "sent_polarity": blob.sentiment.polarity,
        "sent_subjectivity": blob.sentiment.subjectivity,
        "sent_reassurance_count": reassurance_count,
        "sent_warning_count": warning_count,
    }


# ---------------------------------------------------------------------------
# Category 6: Clinical Communication
# ---------------------------------------------------------------------------

HEDGE_EPISTEMIC = [
    r"\bmay\b", r"\bmight\b", r"\bpossibly\b", r"\bpossible\b",
    r"\blikely\b", r"\bprobably\b", r"\bperhaps\b",
    r"\bthought to be\b", r"\bconsidered to be\b", r"\bbelieved to be\b",
    r"\bsuspected\b",
]
HEDGE_EVIDENTIAL = [
    r"\bappears? to\b", r"\bsuggested\b", r"\bsuggestive\b",
    r"\bindicated\b", r"\bseemed\b", r"\bwas felt\b",
]
CERTAINTY_MARKERS = [
    r"\bconfirmed\b", r"\bshowed\b", r"\bdemonstrated\b",
    r"\brevealed\b", r"\bwas found\b", r"\bwas diagnosed\b",
    r"\bdefinitive\b", r"\bclearly\b",
]
CAUSAL_CONNECTIVES = [
    r"\bbecause\b", r"\bdue to\b", r"\bresulting in\b", r"\btherefore\b",
    r"\bso\b", r"\bas a result\b", r"\bcaused by\b", r"\bleading to\b",
    r"\bin order to\b", r"\bwhich led\b", r"\bwhich caused\b",
]
TEMPORAL_CONNECTIVES = [
    r"\bthen\b", r"\bafter\b", r"\bsubsequently\b", r"\binitially\b",
    r"\blater\b", r"\bfollowing\b", r"\bprior to\b", r"\bduring\b",
    r"\bupon\b", r"\bon repeat\b", r"\bpostoperatively\b",
    r"\bpost-operatively\b",
]
CONTRASTIVE_CONNECTIVES = [
    r"\bhowever\b", r"\bbut\b", r"\balthough\b", r"\bdespite\b",
    r"\byet\b", r"\bnevertheless\b", r"\bwhile\b", r"\bwhereas\b",
]
META_REFERENTIAL = [
    r"\bthe record shows\b", r"\bthe note(?:s)? (?:show|state|indicate|document)",
    r"\bthe chart\b", r"\bclinicians? (?:noted|documented|reported)\b",
    r"\baccording to the (?:note|record|chart)\b",
    r"\bit was (?:documented|noted|recorded) that\b",
    r"\bclinical documentation\b",
]


def count_patterns(text: str, patterns: list[str]) -> int:
    total = 0
    for p in patterns:
        if "[A-Z]" in p:
            total += len(re.findall(p, text))
        else:
            total += len(re.findall(p, text.lower()))
    return total


def compute_clinical_communication(text: str) -> dict:
    hedge_epistemic = count_patterns(text, HEDGE_EPISTEMIC)
    hedge_evidential = count_patterns(text, HEDGE_EVIDENTIAL)
    certainty = count_patterns(text, CERTAINTY_MARKERS)
    total_hedge = hedge_epistemic + hedge_evidential
    causal = count_patterns(text, CAUSAL_CONNECTIVES)
    temporal = count_patterns(text, TEMPORAL_CONNECTIVES)
    contrastive = count_patterns(text, CONTRASTIVE_CONNECTIVES)
    meta_ref = count_patterns(text, META_REFERENTIAL)
    abbrevs = len(re.findall(r"\b[A-Z]{2,6}\b", text))
    non_ascii = sum(1 for ch in text if ord(ch) > 127)

    return {
        "clin_hedge_epistemic": hedge_epistemic,
        "clin_hedge_evidential": hedge_evidential,
        "clin_total_hedging": total_hedge,
        "clin_certainty_markers": certainty,
        "clin_hedge_certainty_ratio": (
            total_hedge / (total_hedge + certainty) if (total_hedge + certainty) > 0 else 0.5
        ),
        "clin_causal_connectives": causal,
        "clin_temporal_connectives": temporal,
        "clin_contrastive_connectives": contrastive,
        "clin_total_connectives": causal + temporal + contrastive,
        "clin_meta_referential": meta_ref,
        "clin_medical_abbreviations": abbrevs,
        "clin_non_ascii": non_ascii,
    }


# ---------------------------------------------------------------------------
# Compute all features for a single text
# ---------------------------------------------------------------------------

def compute_all_features(text: str, nlp) -> dict:
    features = {}
    features.update(compute_lexical_features(text))
    features.update(compute_syntactic_features(text, nlp))
    features.update(compute_readability(text))
    features.update(compute_stylistic_features(text, nlp))
    features.update(compute_sentiment_tone(text))
    features.update(compute_clinical_communication(text))
    return features


# ---------------------------------------------------------------------------
# Category 7: Variability Analysis
# ---------------------------------------------------------------------------

def compute_variability_analysis(df: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    rows = []
    for col in feature_cols:
        clin_col = f"clinician_{col}"
        model_col = f"model_{col}"
        if clin_col in df.columns and model_col in df.columns:
            clin_vals = df[clin_col].dropna()
            model_vals = df[model_col].dropna()
            clin_var = clin_vals.var() if len(clin_vals) > 1 else 0.0
            model_var = model_vals.var() if len(model_vals) > 1 else 0.0
            var_ratio = clin_var / model_var if model_var > 0 else float("inf")
            clin_cv = clin_vals.std() / clin_vals.mean() if clin_vals.mean() != 0 else 0.0
            model_cv = model_vals.std() / model_vals.mean() if model_vals.mean() != 0 else 0.0
            rows.append({
                "feature": col,
                "clinician_mean": clin_vals.mean(),
                "clinician_std": clin_vals.std(),
                "clinician_cv": clin_cv,
                "model_mean": model_vals.mean(),
                "model_std": model_vals.std(),
                "model_cv": model_cv,
                "variance_ratio": var_ratio,
                "cv_ratio": clin_cv / model_cv if model_cv > 0 else float("inf"),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------

def run_statistical_tests(df: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    rows = []
    for col in feature_cols:
        clin_col = f"clinician_{col}"
        model_col = f"model_{col}"
        if clin_col in df.columns and model_col in df.columns:
            clin_vals = df[clin_col].values
            model_vals = df[model_col].values
            diff = clin_vals - model_vals
            clin_mean = np.mean(clin_vals)
            model_mean = np.mean(model_vals)
            non_zero_diff = diff[diff != 0]
            if len(non_zero_diff) >= 5:
                stat, p_value = stats.wilcoxon(non_zero_diff)
                n = len(non_zero_diff)
                r = 1 - (2 * stat) / (n * (n + 1))
            else:
                stat, p_value, r = np.nan, np.nan, np.nan
            diff_std = np.std(diff, ddof=1)
            cohens_d = np.mean(diff) / diff_std if diff_std > 0 else 0.0
            if np.isnan(p_value):
                sig = "n/a"
            elif p_value < 0.001:
                sig = "***"
            elif p_value < 0.01:
                sig = "**"
            elif p_value < 0.05:
                sig = "*"
            else:
                sig = "ns"
            rows.append({
                "feature": col,
                "clinician_mean": clin_mean,
                "model_mean": model_mean,
                "mean_diff": clin_mean - model_mean,
                "direction": "clinician > model" if clin_mean > model_mean else "model > clinician",
                "wilcoxon_stat": stat,
                "p_value": p_value,
                "significant": sig,
                "cohens_d": cohens_d,
                "rank_biserial_r": r,
            })
    result = pd.DataFrame(rows)

    # Benjamini-Hochberg FDR correction for multiple comparisons
    valid_mask = result["p_value"].notna()
    if valid_mask.any():
        from statsmodels.stats.multitest import multipletests

        raw_p = result.loc[valid_mask, "p_value"].values
        rejected, p_adj, _, _ = multipletests(raw_p, alpha=0.05, method="fdr_bh")
        result.loc[valid_mask, "p_adjusted"] = p_adj
        # Recompute significance from adjusted p-values
        sigs = []
        for p in p_adj:
            if p < 0.001:
                sigs.append("***")
            elif p < 0.01:
                sigs.append("**")
            elif p < 0.05:
                sigs.append("*")
            else:
                sigs.append("ns")
        result.loc[valid_mask, "significant"] = sigs
    if "p_adjusted" not in result.columns:
        result["p_adjusted"] = np.nan

    return result


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

CATEGORY_PREFIXES = {
    "Lexical": "lex_",
    "Syntactic": "syn_",
    "Readability": "read_",
    "Stylistic": "sty_",
    "Clinical": "clin_",
    "Sentiment": "sent_",
}


def _compute_grouped_scores(df: pd.DataFrame) -> tuple[dict[str, float], dict[str, float]]:
    """
    Compute 6 category-level composite scores for clinician and model using ALL features
    in each category (identified by prefix).

    Unit-circle normalization: clinician = 1.0 on every spoke.
    Each feature ratio = model_mean / max(|clinician_mean|, ε).
    Category score = mean of per-feature ratios.
    Clinician category score = 1.0 by construction.
    Flesch reading ease is inverted (100 - value) so all readability features
    point in the same direction (higher = harder to read).
    """
    clin_scores: dict[str, float] = {}
    model_scores: dict[str, float] = {}
    for cat, prefix in CATEGORY_PREFIXES.items():
        model_ratios = []
        feat_cols = [c for c in df.columns if c.startswith(f"clinician_{prefix}")]
        for clin_col in feat_cols:
            feat = clin_col.replace("clinician_", "")
            model_col = f"model_{feat}"
            if model_col not in df.columns:
                continue
            c = df[clin_col].mean()
            m = df[model_col].mean()
            if feat == "read_flesch_reading_ease":
                c = 100.0 - c
                m = 100.0 - m
            denom = max(abs(c), 1e-10)
            model_ratios.append(m / denom)
        if model_ratios:
            clin_scores[cat] = 1.0
            model_scores[cat] = float(np.mean(model_ratios))
    return clin_scores, model_scores


def generate_grouped_radar(
    config_dfs: dict[str, pd.DataFrame],
    output_path: Path,
) -> None:
    """
    6-spoke grouped radar: Clinician vs one or more model configs.
    config_dfs maps display label to paired_df (with clinician_ and model_ columns).
    Clinician scores are derived from the first df (reference is fixed across configs).
    """
    if not config_dfs:
        return

    first_df = next(iter(config_dfs.values()))
    clin_scores, _ = _compute_grouped_scores(first_df)
    categories = list(clin_scores.keys())
    n = len(categories)
    if n == 0:
        return

    angles = [i / n * 2 * math.pi for i in range(n)]
    angles_closed = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    # Clinician = unit circle at 1.0
    clin_vals = [1.0] * n + [1.0]
    ax.plot(angles_closed, clin_vals, "o-", color=_COLORS[0], label="Clinician",
            markersize=5, linewidth=2)
    ax.fill(angles_closed, clin_vals, alpha=0.12, color=_COLORS[0])

    all_model_vals = []
    for idx, (label, df) in enumerate(config_dfs.items()):
        _, model_scores = _compute_grouped_scores(df)
        model_vals = [model_scores.get(c, 1.0) for c in categories] + [model_scores.get(categories[0], 1.0)]
        all_model_vals.extend(model_vals)
        ax.plot(angles_closed, model_vals, "s-", color=_COLORS[idx + 1], label=label,
                markersize=5, linewidth=2, alpha=0.85)
        ax.fill(angles_closed, model_vals, alpha=0.08, color=_COLORS[idx + 1])

    # Y-axis: start at 0, extend just beyond the max ratio (cap at 1.5)
    y_max = min(max(all_model_vals + [1.0]) * 1.1, 1.5)
    ax.set_ylim(0, y_max)
    ax.set_rlabel_position(90)
    ax.spines["polar"].set_visible(False)
    ax.set_xticks(angles)
    ax.set_xticklabels(categories, size=10)
    ax.tick_params(axis="x", pad=20)
    ax.set_title("Clinician vs. Model Linguistic Profile", pad=15, fontsize=12, fontweight="bold")
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=len(config_dfs) + 1,
        frameon=False,
        fontsize=9,
    )

    stem = output_path.with_suffix("")
    plt.savefig(f"{stem}.png", bbox_inches="tight")
    plt.savefig(f"{stem}.pdf", bbox_inches="tight")
    plt.close()


def generate_case_heatmap(paired_df: pd.DataFrame, output_path: Path):
    """Per-case × per-feature heatmap showing divergence direction and magnitude."""
    key_features = [
        "lex_word_count", "lex_ttr", "syn_sentence_count", "syn_avg_sent_length",
        "read_flesch_kincaid_grade", "sty_passive_voice_ratio", "sty_the_patient_count",
        "sent_polarity", "clin_total_hedging", "clin_causal_connectives",
        "clin_temporal_connectives", "clin_certainty_markers",
    ]
    # Compute normalized divergence: (clinician - model) / max(|clin|, |model|)
    matrix = []
    case_ids = []
    for _, row in paired_df.iterrows():
        case_ids.append(str(row["case_id"]))
        row_vals = []
        for feat in key_features:
            c = row.get(f"clinician_{feat}", 0)
            m = row.get(f"model_{feat}", 0)
            mx = max(abs(c), abs(m), 1e-10)
            row_vals.append((c - m) / mx)
        matrix.append(row_vals)

    matrix = np.array(matrix)
    feat_labels = [_clean_label(f.split("_", 1)[1]) for f in key_features]

    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(matrix, cmap="RdBu", aspect="auto", vmin=-1, vmax=1)
    ax.set_xticks(range(len(feat_labels)))
    ax.set_xticklabels(feat_labels, rotation=45, ha="right")
    ax.set_yticks(range(len(case_ids)))
    ax.set_yticklabels([f"Case {cid}" for cid in case_ids])
    ax.set_title("Per-Case Feature Divergence")
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Clinician higher              Model higher",
                    fontsize=9, color="#666666")

    stem = output_path.with_suffix("")
    plt.savefig(f"{stem}.png")
    plt.savefig(f"{stem}.pdf")
    plt.close()


# ---------------------------------------------------------------------------
# Literature comparison
# ---------------------------------------------------------------------------

LITERATURE_FINDINGS = [
    ("Lower lexical diversity (TTR)", "All 5 papers", "lex_ttr", "model < clinician"),
    ("Fewer unique words", "Stelmakh+, Culda+", "lex_unique_words", "model < clinician"),
    ("More uniform sentence lengths", "All 5 papers", "syn_sent_length_std", "model < clinician"),
    ("More nouns, fewer adjectives/adverbs", "Tercon, Contrasting", "syn_adj_ratio", "model < clinician"),
    ("Less passive voice", "Culda et al.", "sty_passive_voice_ratio", "model < clinician"),
    ("More readable (lower grade level)", "Culda+, Stelmakh+", "read_flesch_kincaid_grade", "model < clinician"),
    ("More positive sentiment", "Stelmakh+, Contrasting", "sent_polarity", "model > clinician"),
    ("Lower subjectivity", "Stelmakh et al.", "sent_subjectivity", "model < clinician"),
    ("Higher consistency (lower variance)", "Stelmakh et al.", None, "model variance < clinician variance"),
]


def format_literature_table(stats_df: pd.DataFrame, var_df: pd.DataFrame) -> str:
    """Compare our findings against established literature. Returns markdown string."""
    rows = []
    for finding, source, feature, expected in LITERATURE_FINDINGS:
        if feature is None:
            finite_var = var_df[var_df["variance_ratio"] != float("inf")]
            if not finite_var.empty:
                median_vr = finite_var["variance_ratio"].median()
                observed = f"Median var ratio: {median_vr:.2f}"
                confirmed = "Partially" if median_vr > 1 else "No"
            else:
                observed = "N/A"
                confirmed = "N/A"
        else:
            match = stats_df[stats_df["feature"] == feature]
            if match.empty:
                observed = "Feature not found"
                confirmed = "N/A"
            else:
                r = match.iloc[0]
                clin, mod, sig = r["clinician_mean"], r["model_mean"], r["significant"]
                observed = f"clin={clin:.3f}, model={mod:.3f} ({sig})"
                if "model < clinician" in expected:
                    confirmed = "Yes" if mod < clin and sig in ("*", "**", "***") else ("Trend" if mod < clin else "No")
                else:
                    confirmed = "Yes" if mod > clin and sig in ("*", "**", "***") else ("Trend" if mod > clin else "No")
        rows.append({"Finding": finding, "Source": source, "Expected": expected, "Observed": observed, "Confirmed": confirmed})

    lit_df = pd.DataFrame(rows)
    return f"## Literature Comparison\n\nTesting established AI-text findings in the clinical QA domain:\n\n{lit_df.to_markdown(index=False)}\n"


# ---------------------------------------------------------------------------
# Cross-config comparison
# ---------------------------------------------------------------------------

def compute_linguistic_distance(model_means: dict, clinician_means: dict, clinician_stds: dict) -> float:
    """Standardized linguistic distance: mean of |model - clinician| / clinician_std."""
    distances = []
    for feat in model_means:
        if feat in clinician_means and feat in clinician_stds:
            std = clinician_stds[feat]
            if std > 0.001:
                distances.append(abs(model_means[feat] - clinician_means[feat]) / std)
    return statistics.mean(distances) if distances else float("inf")


def run_cross_config_analysis(
    config_dfs: dict[str, pd.DataFrame],
    clinician_stats: dict,
    feature_cols: list[str],
    output_dir: Path,
):
    """
    Compare all configs: rank by linguistic distance to clinician,
    show feature evolution across prompt versions.
    """
    # Compute clinician baselines
    clin_means = clinician_stats["means"]
    clin_stds = clinician_stats["stds"]

    # Compute distance per config
    ranking = []
    config_means_all = {}
    for config_name, df in config_dfs.items():
        model_means = {}
        for feat in feature_cols:
            col = f"model_{feat}"
            if col in df.columns:
                model_means[feat] = df[col].mean()
        config_means_all[config_name] = model_means
        dist = compute_linguistic_distance(model_means, clin_means, clin_stds)
        ranking.append({"config": config_name, "linguistic_distance": dist})

    ranking_df = pd.DataFrame(ranking).sort_values("linguistic_distance")
    ranking_df.to_csv(output_dir / "linguistic_distance_ranking.csv", index=False)

    # Key features for the comparison table
    key_feats = [
        "lex_word_count", "lex_ttr", "syn_sentence_count", "syn_avg_sent_length",
        "read_flesch_kincaid_grade", "sty_passive_voice_ratio", "sty_the_patient_count",
        "clin_total_hedging", "clin_temporal_connectives",
    ]

    # Write cross-config report
    lines = ["# Cross-Configuration Linguistic Comparison\n"]
    lines.append(f"**Configs analyzed**: {len(ranking_df)}\n")
    lines.append("## Linguistic Distance Ranking (closest to clinician first)\n")
    lines.append("| Rank | Configuration | Linguistic Distance |")
    lines.append("|------|--------------|-------------------|")
    for i, (_, row) in enumerate(ranking_df.iterrows(), 1):
        lines.append(f"| {i} | {row['config']} | {row['linguistic_distance']:.3f} |")
    lines.append("")

    # Feature comparison table for top and bottom configs
    lines.append("## Feature Comparison: Closest vs. Furthest Configs\n")
    all_configs = ranking_df["config"].tolist()
    if len(all_configs) <= 6:
        show_configs = all_configs
    else:
        top3 = all_configs[:3]
        bot3 = all_configs[-3:]
        show_configs = top3 + bot3

    header = "| Feature | Clinician |"
    sep = "|---------|-----------|"
    for cfg in show_configs:
        short = cfg[:45]
        header += f" {short} |"
        sep += "---------|"
    lines.append(header)
    lines.append(sep)

    for feat in key_feats:
        row_str = f"| {feat.split('_', 1)[1]} | {clin_means.get(feat, 0):.2f} |"
        for cfg in show_configs:
            val = config_means_all.get(cfg, {}).get(feat, 0)
            row_str += f" {val:.2f} |"
        lines.append(row_str)
    lines.append("")

    # Prompt evolution: group by prompt version
    version_groups = {}
    for cfg in config_means_all:
        # Extract version: look for v\d+ in name
        m = re.search(r"v(\d+)", cfg)
        version = f"v{m.group(1)}" if m else "base"
        if version not in version_groups:
            version_groups[version] = []
        version_groups[version].append(cfg)

    if len(version_groups) > 1:
        lines.append("## Prompt Version Evolution\n")
        lines.append("How key features change across prompt versions (mean across configs of each version):\n")

        sorted_versions = sorted(version_groups.keys(), key=lambda v: int(v[1:]) if v[1:].isdigit() else 0)
        header = "| Feature | Clinician |"
        sep = "|---------|-----------|"
        for v in sorted_versions:
            header += f" {v} (n={len(version_groups[v])}) |"
            sep += "---------|"
        lines.append(header)
        lines.append(sep)

        for feat in key_feats:
            row_str = f"| {feat.split('_', 1)[1]} | {clin_means.get(feat, 0):.2f} |"
            for v in sorted_versions:
                vals = [config_means_all[cfg].get(feat, 0) for cfg in version_groups[v]]
                avg = statistics.mean(vals) if vals else 0
                row_str += f" {avg:.2f} |"
            lines.append(row_str)
        lines.append("")

    generate_grouped_radar(config_dfs, output_dir / "cross_config_radar.png")

    (output_dir / "cross_config_report.md").write_text("\n".join(lines))
    return ranking_df


# ---------------------------------------------------------------------------
# Full report generation (no cherry-picking)
# ---------------------------------------------------------------------------

def generate_report(
    paired_df: pd.DataFrame,
    stats_df: pd.DataFrame,
    var_df: pd.DataFrame,
    clinician_answers: dict,
    model_answers: dict,
    config_name: str,
    output_path: Path,
):
    """Full report: all metrics, all cases, literature comparison."""
    sections = []

    # Section 1: Overview
    sig_count = len(stats_df[stats_df["significant"].isin(["*", "**", "***"])])
    sections.append(
        f"# Linguistic Comparison Report: Model vs. Clinician\n\n"
        f"**Configuration**: {config_name}\n\n"
        f"## 1. Overview\n\n"
        f"- Cases analyzed: {len(paired_df)}\n"
        f"- Features compared: {len(stats_df)}\n"
        f"- Statistically significant differences (BH-adjusted p<0.05): {sig_count} of {len(stats_df)}\n"
    )

    # Section 2: Full feature comparison tables by category
    categories = {
        "Lexical Features": "lex_",
        "Syntactic Features": "syn_",
        "Readability": "read_",
        "Stylistic Features": "sty_",
        "Sentiment & Tone": "sent_",
        "Clinical Communication": "clin_",
    }

    cat_parts = ["## 2. Full Feature Comparison\n"]
    display_cols = ["feature", "clinician_mean", "model_mean", "mean_diff", "p_value", "p_adjusted", "significant", "cohens_d"]
    col_rename = {
        "feature": "Feature", "clinician_mean": "Clinician", "model_mean": "Model",
        "mean_diff": "Δ", "p_value": "p", "p_adjusted": "p_adj", "significant": "Sig", "cohens_d": "d",
    }
    for cat_name, prefix in categories.items():
        cat_stats = stats_df[stats_df["feature"].str.startswith(prefix)].copy()
        if cat_stats.empty:
            continue
        cat_stats["feature"] = cat_stats["feature"].str.replace(prefix, "", n=1)
        cat_table = cat_stats[display_cols].rename(columns=col_rename)
        cat_parts.append(f"### {cat_name}\n\n{cat_table.to_markdown(index=False, floatfmt='.4f')}\n")
    sections.append("\n".join(cat_parts))

    # Section 3: Variability analysis
    var_sorted = var_df[
        (var_df["clinician_std"] > 0.001) | (var_df["model_std"] > 0.001)
    ].sort_values("variance_ratio", ascending=False).copy()

    var_table = var_sorted[["feature", "clinician_mean", "clinician_std", "model_mean", "model_std", "variance_ratio"]].rename(
        columns={"feature": "Feature", "clinician_mean": "Clin Mean", "clinician_std": "Clin Std",
                 "model_mean": "Model Mean", "model_std": "Model Std", "variance_ratio": "Var Ratio"}
    )
    finite_ratios = var_sorted[var_sorted["variance_ratio"] != float("inf")]
    median_note = f"\nMedian variance ratio: {finite_ratios['variance_ratio'].median():.2f}\n" if not finite_ratios.empty else ""
    sections.append(
        f"## 3. Variability Analysis\n\n"
        f"Variance ratio = clinician variance / model variance. >1 means clinician adapts more per case.\n\n"
        f"{var_table.to_markdown(index=False, floatfmt='.3f')}\n{median_note}"
    )

    # Section 4: Literature comparison
    sections.append(format_literature_table(stats_df, var_df))

    # Section 5: Full case gallery
    feature_cols = [c.replace("clinician_", "") for c in paired_df.columns if c.startswith("clinician_")]
    gallery_df = paired_df.copy()
    gallery_df["divergence"] = gallery_df.apply(
        lambda row: np.mean([
            abs(row.get(f"clinician_{f}", 0) - row.get(f"model_{f}", 0)) / max(abs(row.get(f"clinician_{f}", 0)), abs(row.get(f"model_{f}", 0)), 1e-10)
            for f in feature_cols
            if not np.isnan(row.get(f"clinician_{f}", np.nan)) and not np.isnan(row.get(f"model_{f}", np.nan))
        ]),
        axis=1,
    )
    gallery_df = gallery_df.sort_values("divergence", ascending=False)

    case_parts = ["## 5. Full Case Gallery\n\nAll paired cases with key per-case metrics.\n"]
    for _, row in gallery_df.iterrows():
        case_id = row["case_id"]
        case_summary = pd.DataFrame({
            "Metric": ["Words", "Sentences", "FK Grade"],
            "Clinician": [
                f"{row.get('clinician_lex_word_count', 0):.0f}",
                f"{row.get('clinician_syn_sentence_count', 0):.0f}",
                f"{row.get('clinician_read_flesch_kincaid_grade', 0):.1f}",
            ],
            "Model": [
                f"{row.get('model_lex_word_count', 0):.0f}",
                f"{row.get('model_syn_sentence_count', 0):.0f}",
                f"{row.get('model_read_flesch_kincaid_grade', 0):.1f}",
            ],
        })
        case_parts.append(
            f"### Case {case_id} (divergence: {row['divergence']:.3f})\n\n"
            f"{case_summary.to_markdown(index=False)}\n\n"
            f"**Clinician**: {clinician_answers.get(case_id, 'N/A')}\n\n"
            f"**Model**: {model_answers.get(case_id, 'N/A')}\n\n---\n"
        )
    sections.append("\n".join(case_parts))

    output_path.write_text("\n".join(sections))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

@hydra.main(config_path="../configs", config_name="linguistic-analysis-config", version_base=None)
def main(cfg: DictConfig):
    logger.info(f"Config:\n{OmegaConf.to_yaml(cfg)}")

    output_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)

    # Collect submission paths and labels
    submission_paths = []
    if cfg.all_configs:
        submission_paths = discover_all_configs(cfg.all_configs)
        logger.info(f"Discovered {len(submission_paths)} configs in {cfg.all_configs}")
    elif cfg.submissions:
        submission_paths = [Path(p) for p in cfg.submissions]
    else:
        raise ValueError("Provide submissions or all_configs in config")

    labels = list(cfg.labels) if cfg.labels else []
    if labels and len(labels) != len(submission_paths):
        raise ValueError(f"labels count ({len(labels)}) must match submissions count ({len(submission_paths)})")

    logger.info("Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")

    logger.info("Loading reference answers...")
    clinician_answers = load_reference_answers(cfg.reference)
    logger.info(f"  Loaded {len(clinician_answers)} clinician answers")

    # Pre-compute clinician features once
    logger.info("Computing clinician features...")
    clinician_features = {}
    for case_id, text in clinician_answers.items():
        clinician_features[case_id] = compute_all_features(text, nlp)

    # Get feature column names
    sample_feats = list(next(iter(clinician_features.values())).keys())

    # Clinician stats for cross-config comparison
    clin_means = {}
    clin_stds = {}
    for feat in sample_feats:
        vals = [clinician_features[cid][feat] for cid in clinician_features]
        clin_means[feat] = statistics.mean(vals)
        clin_stds[feat] = statistics.stdev(vals) if len(vals) > 1 else 0.0
    clinician_stats = {"means": clin_means, "stds": clin_stds}

    # Process each config
    all_config_dfs = {}
    for i, sub_path in enumerate(submission_paths):
        config_name = labels[i] if i < len(labels) else sub_path.parent.parent.name
        logger.info(f"Processing: {config_name}...")

        model_answers = load_model_answers(str(sub_path))
        common_ids = sorted(
            set(clinician_answers.keys()) & set(model_answers.keys()),
            key=lambda x: int(x) if x.isdigit() else x,
        )

        rows = []
        for case_id in common_ids:
            clin_feats = clinician_features[case_id]
            model_feats = compute_all_features(model_answers[case_id], nlp)
            row = {"case_id": case_id}
            for k, v in clin_feats.items():
                row[f"clinician_{k}"] = v
            for k, v in model_feats.items():
                row[f"model_{k}"] = v
            rows.append(row)

        paired_df = pd.DataFrame(rows)
        all_config_dfs[config_name] = paired_df

        feature_cols = sorted(set(
            c.replace("clinician_", "").replace("model_", "")
            for c in paired_df.columns
            if c.startswith("clinician_") or c.startswith("model_")
        ))

        # Per-config output
        config_dir = output_dir / config_name
        config_dir.mkdir(parents=True, exist_ok=True)
        paired_df.to_csv(config_dir / "paired_metrics.csv", index=False)

        stats_df = run_statistical_tests(paired_df, feature_cols)
        stats_df.to_csv(config_dir / "statistical_tests.csv", index=False)

        var_df = compute_variability_analysis(paired_df, feature_cols)
        var_df.to_csv(config_dir / "variance_analysis.csv", index=False)

        generate_grouped_radar({config_name: paired_df}, config_dir / "divergence_radar.png")
        generate_case_heatmap(paired_df, config_dir / "case_heatmap.png")

        generate_report(
            paired_df, stats_df, var_df,
            clinician_answers, model_answers, config_name,
            config_dir / "report.md",
        )

        sig_count = len(stats_df[stats_df["significant"].isin(["*", "**", "***"])])
        logger.info(f"  {config_name}: {sig_count} sig features")

    # Cross-config comparison (if multiple configs)
    if len(all_config_dfs) > 1:
        logger.info(f"Cross-config comparison ({len(all_config_dfs)} configs)")

        ranking_df = run_cross_config_analysis(
            all_config_dfs, clinician_stats, sample_feats, output_dir,
        )

        logger.info("Linguistic distance ranking (closest to clinician):")
        for i, (_, row) in enumerate(ranking_df.head(10).iterrows(), 1):
            logger.info(f"  {i:2d}. {row['config']:<45s} dist={row['linguistic_distance']:.3f}")

        logger.info("Furthest from clinician:")
        for _, row in ranking_df.tail(3).iterrows():
            logger.info(f"      {row['config']:<45s} dist={row['linguistic_distance']:.3f}")

    logger.info(f"All outputs saved to: {output_dir}")


if __name__ == "__main__":
    main()
