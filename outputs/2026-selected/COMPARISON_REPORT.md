# Comprehensive Results Comparison - outputs/2026-selected

**Date**: 2026-02-14
**Experiments Analyzed**: 15 configurations (including GPT-5.2 answer-first variants and v2 prompts)
**Dataset**: archehr-dev
**Competition**: Subtask 2 - Evidence Identification

---

## Competition Evaluation Criteria

The competition evaluates using **Evidence F1 scores**, NOT 3-class accuracy:

### **Strict Evaluation** (Primary Metric)

- Only "essential" sentences count as gold evidence
- Metric: Essential Precision, Recall, **F1**
- File: `metrics.csv` → "essential" row

### **Lenient Evaluation** (Alternative Metric)

- Supplementary predictions are not penalized (essential + supplementary = relevant)
- Metric: Relevant (binary) Precision, Recall, **F1**
- File: `binary_metrics.csv` → "relevant" row

---

## 🏆 Competition Results - Top Performers

### Top 5 by Strict F1 (Essential Evidence) - PRIMARY COMPETITION METRIC

| Rank | Experiment | Strict F1 | Precision | Recall | Lenient F1 |
|------|------------|-----------|-----------|--------|------------|
| 🥇 1 | **gpt-5.2-med-answer-first-k3** | **0.669** | 0.661 | 0.678 | 0.678 |
| 🥇 1 | **gpt-5.2-answer-first-high-k5** | **0.669** | 0.650 | 0.686 | 0.672 |
| 🥉 3 | **gpt-5.2-high-answer-first-k3** | **0.633** | 0.612 | 0.653 | 0.690 |
| 4 | **gpt-5.1-answer-first-3** | 0.628 | 0.562 | 0.711 | 0.652 |
| 5 | **gpt-5.1-tight-v2** | 0.621 | 0.573 | 0.678 | 0.651 |

### Top 5 by Lenient F1 (Relevant Evidence) - ALTERNATIVE COMPETITION METRIC

| Rank | Experiment | Lenient F1 | Precision | Recall | Strict F1 |
|------|------------|------------|-----------|--------|-----------|
| 🥇 1 | **gpt-5.2-high-answer-first-k3** | **0.690** | 0.632 | 0.759 | 0.633 |
| 🥈 2 | **gpt-5.2-med-answer-first-k3** | **0.678** | 0.573 | 0.830 | **0.669** |
| 🥉 3 | **gpt-5.1-med-baseline** | 0.677 | 0.623 | 0.741 | 0.485 |
| 4 | **gpt-5.1-baseline-1** | 0.674 | 0.561 | 0.844 | 0.511 |
| 5 | **gpt-5.2-answer-first-high-k5** | 0.672 | 0.602 | 0.762 | **0.669** |

### 🎯 Winner: **gpt-5.2-med-answer-first-k3** (or gpt-5.2-answer-first-high-k5)

Both achieve:
- ✅ **Best Strict F1: 0.669** (tied, 6.5% better than previous best)
- ✅ **Strong Lenient F1**: 0.678/0.672
- ✅ Use answer-first method optimized for recall
- ✅ GPT-5.2 model with appropriate reasoning effort

**Recommendation**: Use `gpt-5.2-med-answer-first-k3` (slightly better lenient F1, lower cost)

---

## Complete Rankings

### By Strict F1 (Essential Evidence) - Competition Primary Metric

| Rank | Experiment | Strict F1 | Precision | Recall | 3-Class Acc |
|------|------------|-----------|-----------|--------|-------------|
| 1 | **gpt-5.2-med-answer-first-k3** | **0.669** | 0.661 | 0.678 | 67.3% |
| 1 | **gpt-5.2-answer-first-high-k5** | **0.669** | 0.650 | 0.686 | 67.5% |
| 3 | **gpt-5.2-high-answer-first-k3** | 0.633 | 0.612 | 0.653 | 69.4% |
| 4 | gpt-5.1-answer-first-3 | 0.628 | 0.562 | 0.711 | 59.3% |
| 5 | gpt-5.1-tight-v2 | 0.621 | 0.573 | 0.678 | 72.7% |
| 6 | gpt-5.1-answer-first-v2-med-k3 | 0.604 | 0.639 | 0.571 | 71.5% |
| 7 | gpt-5.2-answer-first-v2-med-k3 | 0.554 | 0.730 | 0.446 | 74.3% |
| 8 | gpt-5.2-med-baseline | 0.549 | 0.675 | 0.463 | 63.1% |
| 9 | gpt-5.1-baseline-1 | 0.511 | 0.780 | 0.380 | 57.9% |
| 10 | gpt-5.2-baseline-3 | 0.508 | 0.681 | 0.405 | 64.0% |
| 11 | gpt-5.2-baseline-1 | 0.503 | 0.662 | 0.405 | 64.7% |
| 12 | gpt-5.1-tight-v1 | 0.494 | 0.811 | 0.355 | 72.9% |
| 13 | gpt-5.1-med-baseline | 0.485 | 0.854 | 0.339 | 63.6% |
| 14 | gpt-5.1-baseline-3 | 0.453 | 0.683 | 0.339 | 58.2% |
| 15 | gpt-5.1-tight-1 | 0.438 | 0.897 | 0.289 | 72.7% |

### By Lenient F1 (Relevant Evidence) - Competition Alternative Metric

| Rank | Experiment | Lenient F1 | Precision | Recall | 3-Class Acc |
|------|------------|------------|-----------|--------|-------------|
| 1 | **gpt-5.2-high-answer-first-k3** | **0.690** | 0.632 | 0.759 | 69.4% |
| 2 | **gpt-5.2-med-answer-first-k3** | **0.678** | 0.573 | 0.830 | 67.3% |
| 3 | gpt-5.1-med-baseline | 0.677 | 0.623 | 0.741 | 63.6% |
| 4 | gpt-5.1-baseline-1 | 0.674 | 0.561 | 0.844 | 57.9% |
| 5 | gpt-5.2-answer-first-high-k5 | 0.672 | 0.602 | 0.762 | 67.5% |
| 6 | gpt-5.1-baseline-3 | 0.661 | 0.559 | 0.810 | 58.2% |
| 7 | gpt-5.1-answer-first-3 | 0.652 | 0.514 | 0.891 | 59.3% |
| 8 | gpt-5.1-tight-v2 | 0.651 | 0.649 | 0.653 | 72.7% |
| 9 | gpt-5.2-med-baseline | 0.645 | 0.571 | 0.741 | 63.1% |
| 10 | gpt-5.2-baseline-3 | 0.631 | 0.588 | 0.680 | 64.0% |
| 11 | gpt-5.2-baseline-1 | 0.630 | 0.608 | 0.653 | 64.7% |
| 12 | gpt-5.1-tight-v1 | 0.621 | 0.830 | 0.497 | 72.9% |
| 13 | gpt-5.1-answer-first-v2-med-k3 | 0.601 | 0.652 | 0.558 | 71.5% |
| 14 | gpt-5.2-answer-first-v2-med-k3 | 0.567 | 0.767 | 0.449 | 74.3% |
| 15 | gpt-5.1-tight-1 | 0.429 | 0.857 | 0.286 | 72.7% |

---

## Critical Insights

### 1. 🔥 GPT-5.2 + Answer-First Method Dominates

**MAJOR FINDING**: GPT-5.2 with answer-first method significantly outperforms all other configurations:

| Model | Method | Strict F1 | Improvement over Previous Best |
|-------|--------|-----------|-------------------------------|
| GPT-5.2 | answer-first (med, k=3) | **0.669** | **+6.5%** vs gpt-5.1-answer-first |
| GPT-5.2 | answer-first (high, k=5) | **0.669** | **+6.5%** vs gpt-5.1-answer-first |
| GPT-5.2 | answer-first (high, k=3) | 0.633 | +0.8% vs gpt-5.1-answer-first |
| GPT-5.1 | answer-first (k=3) | 0.628 | (previous best) |

**Key Takeaway**: The initial conclusion "GPT-5.1 > GPT-5.2" was wrong - it compared GPT-5.2 baseline vs GPT-5.1 advanced methods. Fair comparison shows **GPT-5.2 wins decisively**.

### 2. 🚨 Prompt Version Matters: v1 >> v2

**v2 prompts optimize for precision/accuracy but DESTROY F1 scores:**

#### GPT-5.1 Comparison:
- **v1** (answer-first-3): Strict F1 = 0.628, Lenient F1 = 0.652
- **v2** (answer-first-v2-med-k3): Strict F1 = 0.604, Lenient F1 = 0.601
- **Impact**: -3.8% strict, -7.8% lenient

#### GPT-5.2 Comparison:
- **v1** (med-answer-first-k3): Strict F1 = 0.669, Lenient F1 = 0.678
- **v2** (answer-first-v2-med-k3): Strict F1 = 0.554, Lenient F1 = 0.567
- **Impact**: -17.2% strict, -16.4% lenient ❌

**Why v2 Fails:**
- v2 prioritizes precision (73.0% vs 66.1%)
- But sacrifices recall (44.6% vs 67.8%)
- Result: Higher 3-class accuracy (74.3% vs 67.3%) but much worse F1
- **Competition measures F1, not accuracy!**

**Conclusion**: ⚠️ **NEVER use v2 prompts for competition** - stick with v1

### 3. The Competition Metric vs Accuracy Trade-off (Still True)

| Method | Strict F1 | 3-Class Acc | Rank |
|--------|-----------|-------------|------|
| gpt-5.2-answer-first-v2 | 0.554 | **74.3%** ← Highest! | #7 ❌ |
| gpt-5.1-tight-v1 | 0.494 | 72.9% | #12 ❌ |
| gpt-5.2-med-answer-first | **0.669** 🥇 | 67.3% | **#1** ✅ |
| gpt-5.1-answer-first | 0.628 | 59.3% ← Lowest! | #4 |

**Visualization:**

```
Strict F1 (Competition Metric)
      ↑
0.67  | • 5.2-med-ans-first (0.669, 67.3%) ← WINNER 🏆
      | • 5.2-high-ans-first (0.669, 67.5%) ← CO-WINNER 🏆
0.63  | • 5.2-high-ans-first-k3 (0.633, 69.4%)
      | • 5.1-answer-first (0.628, 59.3%)
0.62  | • 5.1-tight-v2 (0.621, 72.7%)
      |
0.60  | • 5.1-ans-first-v2 (0.604, 71.5%)
      |
0.55  | • 5.2-ans-first-v2 (0.554, 74.3%) ← High acc, low F1!
      | • 5.2-med-baseline (0.549, 63.1%)
      |
0.49  | • 5.1-tight-v1 (0.494, 72.9%)     ← High acc, low F1!
      |
  0.4 └─────────────────────────────────→
           3-Class Accuracy
      55%    60%     65%     70%    75%
```

**The winning method has MIDDLE accuracy but HIGHEST F1!**

### 4. Reasoning Effort Comparison (GPT-5.2)

| Config | Reasoning | k | Strict F1 | Lenient F1 |
|--------|-----------|---|-----------|------------|
| med-answer-first-k3 | medium | 3 | **0.669** | 0.678 |
| answer-first-high-k5 | high | 5 | **0.669** | 0.672 |
| high-answer-first-k3 | high | 3 | 0.633 | **0.690** |

**Insights:**
- Medium reasoning with k=3 achieves best strict F1
- High reasoning with k=5 ties on strict F1 but slightly lower lenient
- High reasoning with k=3 has best lenient F1 but lower strict
- **Recommendation**: Use medium reasoning (lower cost, best strict F1)

### 5. Recall is King for F1 Scores

**Top performers all have high recall:**

| Method | Strict Recall | Strict F1 | Rank |
|--------|--------------|-----------|------|
| gpt-5.1-answer-first | **71.1%** ← Highest | 0.628 | #4 |
| gpt-5.2-answer-first-high-k5 | 68.6% | **0.669** | #1 |
| gpt-5.2-med-answer-first | 67.8% | **0.669** | #1 |
| gpt-5.2-high-answer-first | 65.3% | 0.633 | #3 |

**Low recall methods fail despite high precision:**

| Method | Strict Precision | Strict Recall | Strict F1 | Rank |
|--------|-----------------|--------------|-----------|------|
| gpt-5.1-tight-1 | **89.7%** | 28.9% ❌ | 0.438 | #15 |
| gpt-5.1-med-baseline | 85.4% | 33.9% ❌ | 0.485 | #13 |
| gpt-5.2-answer-first-v2 | 73.0% | 44.6% ❌ | 0.554 | #7 |

**F1 Formula Reminder**: F1 = 2 × (P × R) / (P + R)
- Low recall creates a bottleneck that high precision can't overcome
- Balanced or high-recall approaches maximize F1

---

## Detailed Analysis: Top Methods

### 🏆 #1: gpt-5.2-med-answer-first-k3 (WINNER)

**Competition Metrics:**
```
Strict (Essential):
  Precision: 0.661
  Recall:    0.678
  F1:        0.669  ← BEST (tied) 🥇

Lenient (Relevant):
  Precision: 0.573
  Recall:    0.830
  F1:        0.678  ← 2nd best
```

**Other Metrics:**
- 3-Class Accuracy: 67.3%
- Binary Accuracy: 76.4%

**Why It Wins:**
- ✅ Best strict F1 (competition primary metric)
- ✅ Strong lenient F1
- ✅ Excellent recall (67.8% essential, 83.0% relevant)
- ✅ Balanced precision/recall
- ✅ GPT-5.2 with medium reasoning (cost-effective)
- ✅ Uses v1 prompts (optimized for recall)

**Configuration:**
- Model: GPT-5.2
- Reasoning effort: medium
- Method: answer_first
- Prompt version: v1
- Sampling: k=3

---

### 🏆 #1 (tied): gpt-5.2-answer-first-high-k5

**Competition Metrics:**
```
Strict (Essential):
  Precision: 0.650
  Recall:    0.686
  F1:        0.669  ← BEST (tied) 🥇

Lenient (Relevant):
  Precision: 0.602
  Recall:    0.762
  F1:        0.672  ← 5th best
```

**Other Metrics:**
- 3-Class Accuracy: 67.5%
- Binary Accuracy: 76.9%

**Comparison to med-k3:**
- Same strict F1 (0.669)
- Slightly lower lenient F1 (-0.006)
- Uses high reasoning + k=5 (higher cost)
- **Recommendation**: Use med-k3 instead (same performance, lower cost)

---

### 🥉 #3: gpt-5.2-high-answer-first-k3

**Competition Metrics:**
```
Strict (Essential):
  Precision: 0.612
  Recall:    0.653
  F1:        0.633  ← 3rd best

Lenient (Relevant):
  Precision: 0.632
  Recall:    0.759
  F1:        0.690  ← BEST 🥇
```

**Why It's Interesting:**
- Best lenient F1 (if supplementary matters)
- Good balance across metrics
- High reasoning effort
- **Use case**: If lenient evaluation is more important than strict

---

### #4: gpt-5.1-answer-first-3 (Previous Best)

**Competition Metrics:**
```
Strict (Essential):
  Precision: 0.562
  Recall:    0.711  ← Highest recall!
  F1:        0.628

Lenient (Relevant):
  Precision: 0.514
  Recall:    0.891  ← Highest recall!
  F1:        0.652
```

**Why It's Now #4:**
- Was previous winner (before finding GPT-5.2 answer-first)
- Still has highest recall (71.1% essential, 89.1% relevant)
- But lower precision hurts F1
- GPT-5.2 achieves better precision/recall balance

---

### ❌ AVOID: v2 Prompt Methods

**gpt-5.2-answer-first-v2-med-k3** (Rank #7):
```
Strict F1: 0.554 (-17.2% vs v1)
Lenient F1: 0.567 (-16.4% vs v1)
3-Class Acc: 74.3% ← Misleadingly high!
```

**gpt-5.1-answer-first-v2-med-k3** (Rank #6):
```
Strict F1: 0.604 (-3.8% vs v1)
Lenient F1: 0.601 (-7.8% vs v1)
3-Class Acc: 71.5%
```

**Why v2 Fails:**
- Optimizes for wrong metric (accuracy vs F1)
- Achieves high precision but kills recall
- Result: High accuracy, poor competition score

---

## Model Comparison: GPT-5.1 vs GPT-5.2

### Fair Comparison (Same Method)

**Answer-First Method:**

| Model | Config | Strict F1 | Lenient F1 |
|-------|--------|-----------|------------|
| GPT-5.2 | med, k=3 | **0.669** | **0.678** |
| GPT-5.2 | high, k=5 | **0.669** | 0.672 |
| GPT-5.2 | high, k=3 | 0.633 | **0.690** |
| GPT-5.1 | k=3 | 0.628 | 0.652 |

**Winner**: GPT-5.2 (+6.5% strict F1, +4.0% lenient F1)

**Baseline Method:**

| Model | Config | Strict F1 | Lenient F1 |
|-------|--------|-----------|------------|
| GPT-5.2 | med-baseline | 0.549 | 0.645 |
| GPT-5.1 | med-baseline | 0.485 | 0.677 |

**Winner**: Mixed (GPT-5.2 for strict, GPT-5.1 for lenient)

### Previous Wrong Conclusion

❌ **Initial Report**: "GPT-5.1 wins (0.628 vs 0.549), use GPT-5.1"
- Compared GPT-5.1 answer-first vs GPT-5.2 baseline (unfair)

✅ **Corrected**: "GPT-5.2 wins (0.669 vs 0.628), use GPT-5.2"
- Fair comparison: both use answer-first method
- GPT-5.2 + answer-first is the winning combination

---

## Recommendations

### For Competition Submission 🏆

**Primary Recommendation: `gpt-5.2-med-answer-first-k3`**

**Why:**
- ✅ **Best Strict F1**: 0.669 (competition primary metric)
- ✅ **Strong Lenient F1**: 0.678 (competition alternative metric)
- ✅ 6.5% improvement over previous best
- ✅ Balanced precision/recall (66.1% / 67.8%)
- ✅ Strong recall (67.8% essential, 83.0% relevant)
- ✅ Cost-effective (medium reasoning vs high)
- ✅ Uses v1 prompts (proven superior)

**Configuration:**
```yaml
model: gpt-5.2
reasoning_effort: medium
method: answer_first
prompt_version: v1
k_samples: 3
```

**Accept the trade-off:**
- ❌ Not highest 3-class accuracy (67.3% vs 74.3% for v2)
- ✅ **But competition measures F1, not accuracy!**

---

### Alternative #1: gpt-5.2-answer-first-high-k5

**When to use:**
- You want same strict F1 performance (0.669)
- You have budget for high reasoning effort
- You want to verify consistency with different config

**Trade-off:**
- Same strict F1 as med-k3
- Slightly lower lenient F1 (-0.006)
- Higher cost (high reasoning + k=5 vs medium + k=3)
- **Verdict**: Not worth the extra cost

---

### Alternative #2: gpt-5.2-high-answer-first-k3

**When to use:**
- Lenient evaluation matters more than strict
- You want best lenient F1 (0.690)

**Trade-off:**
- Lower strict F1 (0.633 vs 0.669, -5.4%)
- Best lenient F1 (0.690 vs 0.678, +1.8%)
- **Verdict**: Only if lenient metric is primary for you

---

### What NOT to Use ❌

**1. v2 Prompt Methods**
- gpt-5.2-answer-first-v2: 0.554 F1 (-17.2% vs v1)
- gpt-5.1-answer-first-v2: 0.604 F1 (-3.8% vs v1)
- **Reason**: Optimizes for accuracy, not F1

**2. Tight Methods (High Precision, Low Recall)**
- gpt-5.1-tight-v1: 81.1% precision, 35.5% recall → 0.494 F1
- gpt-5.1-tight-1: 89.7% precision, 28.9% recall → 0.438 F1
- **Reason**: Low recall kills F1 despite high precision

**3. Baseline Methods**
- Best baseline: gpt-5.1-baseline-1 (0.511 F1)
- **Reason**: 23.6% F1 gap vs winner

**4. GPT-5.1 Models**
- Best GPT-5.1: answer-first-3 (0.628 F1)
- **Reason**: 6.5% F1 gap vs GPT-5.2 equivalent

---

## Decision Matrix

| Your Priority | Choose This | Get This (Strict/Lenient F1) |
|---------------|-------------|------------------------------|
| **Win competition** 🏆 | **gpt-5.2-med-answer-first-k3** | **0.669 / 0.678** |
| Same F1, higher cost | gpt-5.2-answer-first-high-k5 | 0.669 / 0.672 |
| Best lenient F1 | gpt-5.2-high-answer-first-k3 | 0.633 / **0.690** |
| Budget constraint | gpt-5.1-answer-first-3 | 0.628 / 0.652 |
| Maximum recall | gpt-5.1-answer-first-3 | 71.1% / 89.1% recall |
| High accuracy ❌ | gpt-5.2-answer-first-v2 | 0.554 / 0.567 (BAD F1!) |

---

## Action Items

### Immediate: Competition Submission

1. ✅ **Use**: `gpt-5.2-med-answer-first-k3`
   - Best strict F1: 0.669
   - Directory: `/app/outputs/2026-selected/gpt-5.2-med-answer-first-k3`

2. ✅ **Report these metrics**:
   - Strict F1: 0.669 (from `metrics.csv` → "essential" row)
   - Lenient F1: 0.678 (from `binary_metrics.csv` → "relevant" row)

3. ✅ **Configuration to document**:
   ```
   Model: GPT-5.2
   Reasoning: medium
   Method: answer_first (v1 prompts)
   k: 3
   ```

### Investigation: Potential Further Improvements

1. **Check CRASHED version**:
   - `gpt-5.1-tight-v2-1-sample-CRASHED` exists
   - May contain partial results or insights
   - Worth investigating for completeness

2. **Consider ensemble**:
   - gpt-5.2-med-answer-first-k3 (0.669 strict)
   - gpt-5.2-high-answer-first-k3 (0.690 lenient)
   - Could combining them improve both metrics?

---

## Key Takeaways

### 1. Competition Metric is Everything
- **Optimize for F1, not accuracy**
- v2 prompts: 74.3% accuracy, 0.554 F1 (ranks #7) ❌
- v1 prompts: 67.3% accuracy, 0.669 F1 (ranks #1) ✅

### 2. GPT-5.2 + Answer-First is the Winning Combo
- GPT-5.2 outperforms GPT-5.1 when using same method (+6.5% F1)
- Answer-first method beats all other approaches
- Medium reasoning effort is cost-effective

### 3. Recall > Precision for This Task
- Top 3 methods all have 65-71% recall
- High precision methods (>80%) rank poorly (#12-15)
- F1 formula heavily penalizes low recall

### 4. Prompt Version Matters Enormously
- v1 prompts: 0.669 F1 ✅
- v2 prompts: 0.554 F1 ❌
- Never sacrifice recall for precision in this competition

### 5. The Accuracy Trap
- Highest accuracy: 74.3% (v2 prompts, rank #7)
- Winning config: 67.3% accuracy (rank #1 on F1)
- Don't be distracted by accuracy metrics!

---

## Final Recommendation

### 🎯 For Competition Submission:

**Use: `gpt-5.2-med-answer-first-k3`**

This configuration:
- Achieves best strict F1 (0.669) - competition primary metric
- Achieves strong lenient F1 (0.678) - competition alternative metric
- Improves 6.5% over previous best approach
- Uses cost-effective medium reasoning
- Uses proven v1 prompts optimized for recall
- Strikes optimal precision/recall balance

**File Location**: `/app/outputs/2026-selected/gpt-5.2-med-answer-first-k3/results/`

**Metrics to Report**:
- Primary (Strict): Essential F1 = **0.669**
- Alternative (Lenient): Relevant F1 = **0.678**

Don't be distracted by 3-class accuracy - the competition evaluates on Evidence F1 scores, and this configuration is specifically optimized for that metric.

---

## File Mapping Reference

Your evaluation code already computes both competition metrics:

| Competition Metric | File Path | Row to Check |
|-------------------|-----------|--------------|
| **Strict F1** (Primary) | `results/metrics.csv` | "essential" row, f1-score column |
| **Lenient F1** (Alternative) | `results/binary_metrics.csv` | "relevant" row, f1-score column |
| 3-Class Accuracy (Reference only) | `results/metrics.csv` | "accuracy" row |

Both competition metrics are already in your output files - just report the correct ones!
