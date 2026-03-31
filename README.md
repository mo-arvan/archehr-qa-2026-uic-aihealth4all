# ArchEHR-QA 2026 -- UIC-AIHealth4All System

This repository contains the pipeline submitted by UIC-AIHealth4All to the ArchEHR-QA 2026 shared task (CL4Health @ LREC 2026). The system participates in Subtasks 2 (Evidence Identification), 3 (Answer Generation), and 4 (Answer-Evidence Alignment).

## Private / Restricted Files

The following are not included in this repository:

| Path | Reason |
| --- | --- |
| `data-restricted/` | Restricted dataset from PhysioNet (requires credentialed access) |
| `*with_phi*` | Files containing PHI from clinical notes (excluded via `.gitignore`) |
| `.env` | API credentials |

## Prerequisites

- Python 3.12+ with `uv` or standard `pip`
- Azure OpenAI access with GPT-5.1 and GPT-5.2 deployments
- ArchEHR-QA 2026 dataset (`data-restricted/v1.5/`) -- request access at [PhysioNet](https://physionet.org)

## Setup

```bash
uv sync                              # or: pip install .
cp .env.example .env                  # fill in Azure OpenAI credentials
```

`.env` variables:

```env
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
```

## Workflow

### 1. Run experiments (Subtasks 2 and 3)

Each run writes output to a Hydra-managed directory. Use `hydra.run.dir` to name it explicitly.

```bash
# Answer-first pipeline, GPT-5.1, prompt v4, medium reasoning, k=3
python src/benchmark.py \
  dataset=archehr-dev \
  method=answer_first \
  model=gpt-5.1 \
  "method.qa_prompt_file_path=prompts/answer-generation-answer-first-v4.txt" \
  "method.evidence_prompt_file_path=prompts/evidence-classification-answer-first-v4.txt" \
  method.k_candidates=3 \
  "hydra.run.dir=outputs/2026-selected/gpt-5.1-answer-first-v4-med-k3"

# Grounded baseline, GPT-5.2, medium reasoning
python src/benchmark.py \
  dataset=archehr-dev \
  method=baseline \
  model=gpt-5.2 \
  "hydra.run.dir=outputs/2026-selected/gpt-5.2-baseline-1-sample"
```

Switch to `dataset=archehr-test-2026` for test set runs. The `.hydra/overrides.yaml`
inside each output directory records the exact config used, enabling exact reproduction.

**Resume behavior**: rerunning with the same `hydra.run.dir` skips already-completed
cases and processes only the missing ones.

### 2. Run experiments (Subtask 4)

```bash
python src/benchmark.py \
  method=answer_evidence_alignment \
  model=gpt-5.2 \
  dataset=archehr-dev \
  method.alignment_prompt_file_path=prompts/answer-evidence-alignment-v5.txt \
  method.num_samples=5 \
  model.reasoning_effort=xhigh \
  hydra.run.dir=outputs/2026-subtask4-dev/gpt-5.2-xhigh-v5-n5
```

### 3. Score configurations

Requires the ground-truth key file from the dataset.

```bash
# Subtask 2 (dev experiments used v1.4)
python src/scoring_subtask2.py \
  --submission_path outputs/2026-selected/gpt-5.1-answer-first-v4-med-k3/results/submission_subtask2.json \
  --key_path data-restricted/v1.4/dev/archehr-qa_key.json \
  --out_file_path outputs/2026-selected/gpt-5.1-answer-first-v4-med-k3/results/official_task2_scores.json

# Subtask 4 (dev experiments used v1.5)
python src/scoring_subtask_4.py \
  --submission_path outputs/2026-subtask4-dev/gpt-5.2-xhigh-v5-n5/results/submission_subtask4.json \
  --key_path data-restricted/v1.5/dev/archehr-qa_key.json \
  --out_file_path outputs/2026-subtask4-dev/gpt-5.2-xhigh-v5-n5/results/subtask4_scores.json
```

### 4. Analyze experiment logs

Parses all experiment output directories and writes a consolidated CSV.

```bash
python src/analyze_logs.py hydra.run.dir=outputs/log_analysis/
```

By default reads from `outputs/2026-selected` and `outputs/2026-test`
(configured in `configs/log-analysis-config.yaml`). Override with:

```bash
python src/analyze_logs.py \
  experiment_dirs='[outputs/2026-selected,outputs/2026-test]' \
  hydra.run.dir=outputs/log_analysis/
```

### 5. Generate analysis artifacts

Produces all figures, tables, and narrative from the log CSV and dev F1 scores.

```bash
python src/analyze_experiments.py hydra.run.dir=outputs/experiment_analysis/
```

By default reads `outputs/log_analysis/log_analysis.csv` and `outputs/dev_official_scores.csv`
(configured in `configs/experiment-analysis-config.yaml`).

Outputs go to `outputs/experiment_analysis/`. See
`outputs/experiment_analysis/README.md` for a full index of the generated files.

## Key Source Files

| File | Description |
| --- | --- |
| `src/benchmark.py` | Main experiment runner (Hydra-configured) |
| `src/qa_model.py` | Pipeline implementations: answer-first, grounded, alignment |
| `src/analyze_logs.py` | Parses experiment outputs into `log_analysis.csv` |
| `src/analyze_experiments.py` | Generates all analysis artifacts |
| `src/scoring_subtask2.py` | Official Subtask 2 scorer |
| `src/scoring_subtask_3.py` | Official Subtask 3 scorer |
| `src/scoring_subtask_4.py` | Official Subtask 4 scorer |
| `prompts/` | Versioned prompt templates |
| `configs/` | Hydra configuration files (dataset, method, model) |

## Evaluation

[QuickUMLS](https://github.com/Georgetown-IR-Lab/QuickUMLS) is required for Subtask 3 evaluation. Build the evaluation Docker image:

```bash
docker build -t archehr-qa-eval -f eval.Dockerfile .
```

```bash
docker run --rm \
  -v "$PWD/outputs:/app/evaluation/outputs:rw" \
  -v "$PWD/data-restricted/v1.5:/app/evaluation/data_dir:ro" \
  -v "$PWD/quickumls:/app/evaluation/quickumls:rw" \
  archehr-qa-eval \
  python scoring_subtask_3.py \
    --submission_path outputs/2026-selected/gpt-5.1-answer-first-v9-med-k1/results/submission_subtask3_with_phi.json \
    --key_path data_dir/dev/archehr-qa_key.json \
    --data_path data_dir/dev/archehr-qa.xml \
    --quickumls_path quickumls/ \
    --out_file_path outputs/2026-selected/gpt-5.1-answer-first-v9-med-k1/results/scores_subtask3.json
```

## Project Structure

```text
.
+-- src/                         Source code
+-- configs/                     Hydra configs (dataset, method, model)
+-- prompts/                     Versioned prompt templates
+-- outputs/
|   +-- 2026-selected/           Dev experiment runs
|   +-- 2026-test/               Test experiment runs
|   +-- 2026-subtask4-dev/       Subtask 4 dev runs
|   +-- 2026-subtask4-test/      Subtask 4 test runs
|   +-- 2026-ensemble/           Ensemble voting results
|   +-- log_analysis.csv         Consolidated experiment log
|   +-- dev_official_scores.csv  Per-config Subtask 2 F1 scores
|   +-- experiment_analysis/     Figures, tables, and narrative
|   +-- linguistic_analysis/     Linguistic feature comparison
+-- data-restricted/             Dataset (not included, credentialed access required)
```

## Citation

```latex
To be added.
```

## License

CC BY 4.0 -- see [LICENSE](LICENSE).
