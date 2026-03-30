"""
Threshold sweep for self-consistency alignment.

Reads raw_samples from response_output_with_phi files,
aggregates at each threshold (1/N through N/N),
and scores against gold standard.

Usage:
    python src/score_threshold_sweep.py \
        --response_dir outputs/2026-subtask4-dev/gpt-5.1-v5-n5/results/response_output_with_phi \
        --key_path data-restricted/v1.5/dev/archehr-qa_key.json
"""

import json
import glob
import os
from argparse import ArgumentParser
from collections import Counter


def load_gold(key_path):
    """Load gold alignments, handling empty citation strings."""
    with open(key_path) as f:
        key_data = json.load(f)

    gold_map = {}
    for case in key_data:
        cid = case["case_id"]
        pairs = set()
        for s in case["clinician_answer_sentences"]:
            cits = s["citations"]
            if isinstance(cits, str):
                cits = [c.strip() for c in cits.split(",") if c.strip()]
            for eid in cits:
                pairs.add((s["id"], eid))
        gold_map[cid] = pairs
    return gold_map


def aggregate_at_threshold(raw_samples, min_votes):
    """Aggregate raw_samples requiring min_votes for inclusion."""
    all_answer_ids = {a["answer_id"] for a in raw_samples[0]}
    pair_counter = Counter()

    for sample in raw_samples:
        for alignment in sample:
            aid = alignment["answer_id"]
            for eid in alignment["evidence_id"]:
                pair_counter[(aid, eid)] += 1

    pairs = set()
    for (aid, eid), count in pair_counter.items():
        if count >= min_votes:
            pairs.add((aid, eid))

    return pairs


def score(pred_pairs, gold_pairs):
    """Compute precision, recall, F1."""
    tp = len(pred_pairs & gold_pairs)
    p = tp / len(pred_pairs) * 100 if pred_pairs else 0
    r = tp / len(gold_pairs) * 100 if gold_pairs else 0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
    return p, r, f1


def main():
    parser = ArgumentParser()
    parser.add_argument("--response_dir", required=True,
                        help="Path to response_output_with_phi directory")
    parser.add_argument("--key_path", required=True,
                        help="Path to gold key JSON")
    args = parser.parse_args()

    gold_map = load_gold(args.key_path)

    # Load raw_samples from response files
    cases = {}
    for fpath in sorted(glob.glob(os.path.join(args.response_dir, "*.json"))):
        with open(fpath) as f:
            data = json.load(f)
        cid = str(data.get("case_id", data.get("pred", {}).get("case_id", "")))
        pred = data.get("pred", data)
        raw = pred.get("raw_samples")
        if raw is None:
            print(f"WARNING: No raw_samples in {fpath} — skipping")
            continue
        cases[cid] = raw

    if not cases:
        print("ERROR: No raw_samples found in any file. Were runs done with raw_samples storage?")
        return

    n_samples = len(next(iter(cases.values())))
    print(f"Loaded {len(cases)} cases with {n_samples} samples each")
    print()

    # Sweep thresholds
    print(f"{'Threshold':<12} {'Min Votes':<10} {'P':>7} {'R':>7} {'F1':>7}")
    print("-" * 50)

    for min_votes in range(1, n_samples + 1):
        total_tp = 0
        total_pred = 0
        total_gold = 0

        for cid, raw_samples in cases.items():
            gold = gold_map.get(cid, set())
            pred_pairs = aggregate_at_threshold(raw_samples, min_votes)

            tp = len(pred_pairs & gold)
            total_tp += tp
            total_pred += len(pred_pairs)
            total_gold += len(gold)

        p = total_tp / total_pred * 100 if total_pred else 0
        r = total_tp / total_gold * 100 if total_gold else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        label = f">={min_votes}/{n_samples}"
        print(f"{label:<12} {min_votes:<10} {p:>7.1f} {r:>7.1f} {f1:>7.1f}")

    # Also try cross-model ensemble if multiple submission files given
    print()
    print("Done.")


if __name__ == "__main__":
    main()
