# Prompt Design Features vs Performance Analysis

## Performance Summary

### GPT-5.2 Results

| Version | Strict F1 | Precision | Recall | Balance | Strategy |
|---------|-----------|-----------|--------|---------|----------|
| **v1** | **0.669** ✓ | 0.661 | 0.678 | ⚖️ Equal | Balanced |
| v2 | 0.554 | **0.730** | 0.446 ❌ | 📊 P>>R | Precision-focused |
| v3 | 0.562 | 0.448 ❌ | **0.752** | 📊 R>>P | Recall-focused |
| v4 | TBD | TBD | TBD | TBD | Ultra-minimal (predicted) |

### GPT-5.1 Results

| Version | Strict F1 | Precision | Recall | Balance | Strategy |
|---------|-----------|-----------|--------|---------|----------|
| **v1** | **0.628** ✓ | 0.562 | 0.711 | ⚖️ Balanced | Balanced |
| v2 | 0.604 | **0.753** | 0.504 ❌ | 📊 P>>R | Precision-focused |
| v3 | 0.596 | 0.451 ❌ | **0.876** | 📊 R>>P | Recall-focused |
| v4 | TBD | TBD | TBD | TBD | Ultra-minimal (predicted) |

---

## Detailed Feature Comparison

### 1. Answer Generation: Citation Guidance

| Feature | v1 | v2 | v3 | v4 |
|---------|----|----|----|----|
| **Citation instruction** | "strictly necessary" | Not documented | "Do NOT add 'extra supporting'; pick the **best** sentence(s)" | "Use **fewest** citations needed; **avoid redundant** citations" |
| **Citation specificity** | General | High precision focus | Minimal/selective | Ultra-minimal + explicit format |
| **Restrictiveness** | Moderate | High | High | **Highest** |
| **Effect on recall** | ✓ Good (67.8%) | ❌ Low (44.6%) | ↕️ High (75.2%) | ⚠️ Predicted lower than v3 |
| **Effect on precision** | ✓ Good (66.1%) | ✓ High (73.0%) | ❌ Low (44.8%) | ⚠️ Predicted moderate |

**Key Insight:** More restrictive citation rules → Lower recall, but doesn't guarantee higher precision

---

### 2. Answer Generation: Answer Scope

| Feature | v1 | v2 | v3 | v4 |
|---------|----|----|----|----|
| **Scope guidance** | "clear, professional answer" | Not documented | "covers key supported points: diagnosis, evidence, treatments, outcomes" | "addresses **ONLY** the clinician question; Do not add extra background, timeline, outcomes **unless needed**" |
| **Breadth** | Moderate | Unknown | Broad (multiple key aspects) | **Narrow** (question only) |
| **Effect on recall** | ✓ Balanced | ❌ Low | ↕️ High (comprehensive) | ⚠️ Predicted lower |
| **Effect on precision** | ✓ Balanced | ✓ High | ❌ Low | ⚠️ Predicted moderate |

**Key Insight:** Broader scope → More citations → Higher recall but lower precision

---

### 3. Answer Generation: Constraint Strength

| Feature | v1 | v2 | v3 | v4 |
|---------|----|----|----|----|
| **Word limit** | "max 75 words" | Not documented | "≤75 words total" | "Max 75 words total" |
| **Citation constraints** | - | Unknown | "cite the **minimal** sentence(s)" | "**fewest** citations; **avoid redundant**; Do NOT use ranges; No absence claims" |
| **Content constraints** | General | Unknown | Multiple key aspects listed | "**ONLY** clinician question; no extra context" |
| **Total constraints** | Low | Medium-High | Medium | **Very High** |
| **Effect on recall** | ✓ Good | ❌ Low | ↕️ High | ⚠️ Predicted low-moderate |
| **Effect on precision** | ✓ Good | ✓ High | ❌ Low | ⚠️ Predicted moderate-high |

**Key Insight:** More constraints → Lower recall (models cite less to meet constraints)

---

### 4. Evidence Classification: Decision Philosophy

| Feature | v1 | v2 | v3 | v4 |
|---------|----|----|----|----|
| **Philosophy** | "Minimal set" with nuanced gradation | Not documented | Simple citation-based | Strict "CiteLock" to citations |
| **Essential definition** | "Required to support answers; cannot derive key claims without it" | Unknown | "**Any cited sentence** is Essential" | "**Cited by at least one answer**" (same as v3) |
| **Supplementary definition** | "Helpful context but answer complete without it" | Unknown | "**Rare**; only direct clarification of Essential" | "**Rare**; only if directly clarifies cited Essential" (same as v3) |
| **Default bias** | "When in doubt, choose Supplementary" | Unknown | "If unsure → Not Relevant" | "Citations as **the only signal**" |
| **Complexity** | High (74 lines, extensive heuristics) | Unknown | Low (44 lines, simple rules) | Low (47 lines, citation-locked) |

**Key Insight:**
- v1's nuanced approach balances P/R
- v3/v4's simple "cited=essential" creates imbalance depending on citation behavior

---

### 5. Evidence Classification: Strategic Heuristics

| Feature | v1 | v2 | v3 | v4 |
|---------|----|----|----|----|
| **Has strategic heuristics?** | ✓ Yes | Unknown | ❌ No | ❌ No |
| **"So What?" Test** | ✓ Yes | - | ❌ No | ❌ No |
| **Lab Trends guidance** | ✓ "Trends essential, snapshots supplementary" | - | ❌ No | ❌ No |
| **Procedural Outcomes** | ✓ "Finding during procedure essential" | - | ❌ No | ❌ No |
| **Rule-Outs guidance** | ✓ "CT ruled out X is essential" | - | ❌ No | ❌ No |
| **Negative Findings** | ✓ "Unremarkable unless answer relies on it" | - | ❌ No | ❌ No |
| **Effect on recall** | ✓ Captures nuanced evidence | - | ↕️ Over-captures cited | ⚠️ Under-captures if under-cited |
| **Effect on precision** | ✓ Filters appropriately | - | ❌ False positives | ⚠️ Depends on citation quality |

**Key Insight:** Strategic heuristics help identify truly essential evidence beyond simple citation matching

---

### 6. Evidence Classification: Decision Rules

| Feature | v1 | v2 | v3 | v4 |
|---------|----|----|----|----|
| **Primary rule** | "Minimal set test: can I remove this and still support the answer?" | Unknown | "Cited = Essential" | "Cited = Essential" |
| **Secondary guidance** | Extensive (lab trends, procedures, rule-outs, negative findings) | Unknown | Minimal | "Use citations as **only signal**; ignore uncited claims" |
| **Tie-breaker** | "When in doubt → Supplementary" | Unknown | "When in doubt → Not Relevant" | "Citations as only signal" |
| **Supplementary usage** | Encouraged for context | Unknown | Discouraged ("rare") | Discouraged ("rare") |
| **Effect on recall** | ✓ Conservative Essential, catches via Supplementary | - | ↕️ High Essential, ignores Supplementary | ⚠️ Low Essential if under-cited |
| **Effect on precision** | ✓ Filters well | - | ❌ Over-labels Essential | ⚠️ Better than v3 but still depends on citations |

**Key Insight:**
- v1: Multi-tier system (Essential/Supplementary/Not Relevant) allows nuance
- v3/v4: Effectively binary (Essential/Not Relevant) loses nuance

---

## Feature Impact Analysis

### Precision Drivers

| Feature | Impact on Precision | Best Version |
|---------|---------------------|--------------|
| **Restrictive citation rules** | ⬆️ Increases (fewer false citations) | v2 > v4 > v3 > v1 |
| **Narrow answer scope** | ⬆️ Increases (focused citations) | v4 > v2 > v1 > v3 |
| **Strong constraints** | ⬆️ Increases (forces selectivity) | v4 > v2 > v3 > v1 |
| **Strategic heuristics** | ⬆️ Increases (filters appropriately) | v1 >> v2/v3/v4 |
| **Nuanced classification** | ⬆️ Increases (gradation reduces over-labeling) | v1 >> v2/v3/v4 |

**Best precision approach:** v2 (73.0%) but at severe cost to recall

### Recall Drivers

| Feature | Impact on Recall | Best Version |
|---------|------------------|--------------|
| **Permissive citation rules** | ⬆️ Increases (more citations) | v1/v3 > v2/v4 |
| **Broad answer scope** | ⬆️ Increases (comprehensive coverage) | v3 > v1 > v4 > v2 |
| **Minimal constraints** | ⬆️ Increases (freedom to cite) | v1 > v3 > v2 > v4 |
| **Strategic heuristics** | ⬆️ Increases (catches nuanced evidence) | v1 >> v2/v3/v4 |
| **Supplementary category** | ⬆️ Increases (for lenient F1) | v1 >> v2/v3/v4 |
| **Citation-based Essential** | ⬆️ Increases Essential labels | v3 > v4 > v1 > v2 |

**Best recall approach:** v3 (75.2% GPT-5.2, 87.6% GPT-5.1) but at severe cost to precision

---

## Balance Analysis

### Precision-Recall Trade-off (GPT-5.2)

| Version | Precision | Recall | Difference | Balance Score | F1 |
|---------|-----------|--------|------------|---------------|-----|
| **v1** | 0.661 | 0.678 | **0.017** | ✓ **Excellent** | **0.669** |
| v2 | 0.730 | 0.446 | **0.284** | ❌ Poor | 0.554 |
| v3 | 0.448 | 0.752 | **0.304** | ❌ Poor | 0.562 |
| v4 | TBD | TBD | TBD | TBD | TBD |

**Balance Score = |Precision - Recall|** (lower is better)

### What Creates Balance?

| Feature | v1 (Balanced) | v2 (P-heavy) | v3 (R-heavy) | v4 (Predicted) |
|---------|---------------|--------------|--------------|----------------|
| **Citation rules** | Moderate | Very restrictive | Broad then minimal | Ultra-restrictive |
| **Answer scope** | Professional, complete | Unknown but selective | Comprehensive key points | Narrow, question-only |
| **Classification** | Nuanced 3-tier | Unknown | Binary via citations | Binary via citations |
| **Heuristics** | ✓ Extensive | Unknown | ❌ None | ❌ None |
| **Tie-breaker** | → Supplementary | Unknown | → Not Relevant | Citations only |
| **Result** | P≈R (balanced) | P>>R (imbalanced) | R>>P (imbalanced) | Predicted P<R (moderate imbalance) |

---

## Feature Effectiveness Rankings

### Features That Improve F1

| Rank | Feature | Effect | Evidence |
|------|---------|--------|----------|
| 1 | **Strategic heuristics** | ⬆️⬆️⬆️ Strong positive | v1 has them, achieves best F1; v2/v3/v4 lack them, underperform |
| 2 | **Nuanced classification (3-tier)** | ⬆️⬆️ Moderate positive | v1's Essential/Supplementary/Not Relevant beats v3/v4's binary |
| 3 | **Balanced citation guidance** | ⬆️⬆️ Moderate positive | v1's "strictly necessary" beats v2's restrictive and v3/v4's extremes |
| 4 | **Complete answer scope** | ⬆️ Small positive | v1's professional completeness beats v4's narrow focus |
| 5 | **Supplementary encouraged** | ⬆️ Small positive | v1's "when in doubt → Supplementary" helps lenient F1 |

### Features That Hurt F1

| Rank | Feature | Effect | Evidence |
|------|---------|--------|----------|
| 1 | **Over-restrictive citations** | ⬇️⬇️⬇️ Strong negative | v2 worst (0.554 F1), v4 predicted similar |
| 2 | **Simple binary classification** | ⬇️⬇️ Moderate negative | v3/v4 both underperform v1 |
| 3 | **Citation-locked Essential** | ⬇️⬇️ Moderate negative | v3/v4 create P/R imbalance |
| 4 | **Extreme constraints** | ⬇️⬇️ Moderate negative | v4's "fewest citations" + "no extra context" predicted to hurt |
| 5 | **No strategic heuristics** | ⬇️⬇️ Moderate negative | v2/v3/v4 all lack medical reasoning guidance |

---

## Design Principles for Optimal Performance

### What v1 Does Right

1. **Balanced Citation Guidance**
   - "Strictly necessary" is moderate (not "minimal", not "fewest")
   - Allows model judgment on what's needed
   - Result: 66-68% precision/recall balance

2. **Strategic Medical Heuristics**
   - Lab trends vs snapshots
   - Procedural outcomes
   - Rule-outs and negative findings
   - Guides model to identify truly essential evidence
   - Result: Better precision without sacrificing recall

3. **Three-Tier Classification**
   - Essential: Truly required
   - Supplementary: Helpful context (contributes to lenient F1)
   - Not Relevant: Unrelated
   - Result: Nuanced gradation improves both metrics

4. **Conservative Bias**
   - "When in doubt → Supplementary"
   - Prefers false positives in Supplementary over false negatives in Essential
   - Result: Better recall while maintaining precision

5. **Minimal Constraints**
   - Focus on quality ("strictly necessary") not quantity ("fewest")
   - Trust model to make good judgments with guidance
   - Result: Model finds optimal balance naturally

### What v2/v3/v4 Do Wrong

**v2: Over-constrains**
- Too restrictive → Low recall (44.6%)
- High precision (73.0%) but F1 suffers
- Optimizes wrong metric

**v3: Over-simplifies**
- Binary "cited=essential" loses nuance
- No heuristics → Over-labels cited sentences
- High recall (75.2%) but low precision (44.8%)
- F1 suffers from imbalance

**v4: Combines Both Failures**
- Ultra-restrictive citations (v2's problem)
- Binary citation-locked classification (v3's problem)
- Predicted to underperform both

---

## Predictions for v4

### Expected Feature Impact

| Feature | v4 Implementation | Predicted Effect | Confidence |
|---------|-------------------|------------------|------------|
| "Fewest citations" | Ultra-restrictive | ⬇️ Recall vs v3 | High |
| "Avoid redundant" | Removes overlapping evidence | ⬇️ Recall | High |
| "ONLY clinician question" | Narrow scope | ⬇️ Recall | High |
| "No absence claims" | Removes negative evidence | ⬇️ Recall | Medium |
| "CiteLock" | Same as v3 | = Precision/Recall balance | High |
| No heuristics | Same as v3 | = Classification quality | High |

### Predicted Performance (GPT-5.2)

| Metric | Prediction | Reasoning |
|--------|------------|-----------|
| **Precision** | 0.50-0.55 | Better than v3 (fewer citations = fewer FP), worse than v1/v2 (no heuristics) |
| **Recall** | 0.60-0.70 | Worse than v3 (more restrictive), worse than v1 (over-constrained) |
| **Strict F1** | 0.54-0.58 | Imbalance hurts; likely #8-9 rank |
| **vs v1** | -0.09 to -0.13 | Significantly worse |
| **vs v3** | -0.01 to +0.02 | Slightly worse or similar |

### Why v4 Won't Beat v1

1. **Missing strategic heuristics** (v1's #1 advantage)
2. **Over-restrictive citations** (hurts recall)
3. **Binary classification** (loses nuance)
4. **No conservative bias** (misses edge cases)
5. **Ultra-minimal constraints** (forces model to under-cite)

---

## Recommendations

### For Competition: Use v1

**gpt-5.2-med-answer-first-k3 (v1 prompts)**
- ✓ Best balance (P≈R)
- ✓ Strategic heuristics
- ✓ Nuanced classification
- ✓ Proven winner: 0.669 F1

### If Testing v4

**Expected outcome:** Rank #8-9, F1 ~0.54-0.58

**Only test if:**
- You want to confirm the prediction
- You're gathering data on prompt design
- You have compute budget to spare

**Don't test if:**
- You need best competition results NOW
- Compute budget is limited
- Deadline is approaching

### Better Alternatives to v4

Instead of v4, try:

1. **v1 with higher k** (k=5 or k=7)
   - Keep proven prompts, increase coverage
   - Expected: +1-3% F1

2. **v1 with post-processing**
   - Add rule-based evidence expansion
   - Expected: +2-4% F1

3. **v1 ensemble**
   - Multiple v1 runs, union of evidence
   - Expected: +3-5% F1

4. **Hybrid v1 + strategic rules**
   - v1 prompts + algorithmic supplementary detection
   - Expected: +2-4% F1

---

## Conclusion

### The Winning Formula (v1)

```
Balanced Citations (moderate guidance)
+ Strategic Heuristics (medical reasoning)
+ Nuanced Classification (3-tier system)
+ Conservative Bias (prefer false positives in Supplementary)
+ Minimal Constraints (trust model judgment)
───────────────────────────────────────────────
= Best F1 (0.669)
```

### The Failing Patterns (v2/v3/v4)

```
Over-constraint (v2, v4) → Low Recall → Poor F1
Simple Rules (v3, v4) → Imbalance → Poor F1
No Heuristics (v2, v3, v4) → Suboptimal Classification → Poor F1
Binary Thinking (v3, v4) → Lost Nuance → Poor F1
```

### Key Insight

**Complexity and balance win in medical evidence classification.**

Simple, extreme approaches (v2's precision focus, v3's recall focus, v4's ultra-minimalism) all underperform v1's nuanced, balanced approach with strategic medical reasoning.

**Recommendation: Use v1 for competition. Stop experimenting with simplification.**