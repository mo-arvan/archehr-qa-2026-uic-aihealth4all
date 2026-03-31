# Linguistic Comparison Report: Model vs. Clinician

**Configuration**: Two-Step

## 1. Overview

- Cases analyzed: 20
- Features compared: 47
- Statistically significant differences (BH-adjusted p<0.05): 9 of 47

## 2. Full Feature Comparison

### Lexical Features

| Feature            |   Clinician |    Model |        Δ |      p |   p_adj | Sig   |       d |
|:-------------------|------------:|---------:|---------:|-------:|--------:|:------|--------:|
| avg_word_length    |      5.3852 |   6.1213 |  -0.7362 | 0.0000 |  0.0001 | ***   | -1.2113 |
| budget_utilization |      0.9800 |   0.9693 |   0.0107 | 0.0726 |  0.1418 | ns    |  0.3612 |
| hapax_legomena     |     44.0000 |  48.7000 |  -4.7000 | 0.0069 |  0.0313 | *     | -0.7233 |
| hapax_ratio        |      0.5995 |   0.6701 |  -0.0706 | 0.0042 |  0.0216 | *     | -0.7724 |
| mtld               |     86.9815 | 100.7582 | -13.7767 | 0.0328 |  0.0849 | ns    | -0.5388 |
| ttr                |      0.7559 |   0.7910 |  -0.0351 | 0.0266 |  0.0849 | ns    | -0.5980 |
| unique_words       |     55.5000 |  57.5000 |  -2.0000 | 0.0478 |  0.1031 | ns    | -0.4935 |
| word_count         |     73.5000 |  72.7000 |   0.8000 | 0.0854 |  0.1591 | ns    |  0.3612 |

### Syntactic Features

| Feature          |   Clinician |   Model |       Δ |        p |    p_adj | Sig   |       d |
|:-----------------|------------:|--------:|--------:|---------:|---------:|:------|--------:|
| adj_ratio        |      0.0820 |  0.1073 | -0.0253 |   0.0032 |   0.0185 | *     | -0.7465 |
| adp_ratio        |      0.1094 |  0.1005 |  0.0089 |   0.3955 |   0.5759 | ns    |  0.2485 |
| adv_ratio        |      0.0235 |  0.0287 | -0.0051 |   0.4074 |   0.5759 | ns    | -0.1880 |
| avg_parse_depth  |      5.2992 |  5.3208 | -0.0217 |   0.9519 |   1.0000 | ns    | -0.0133 |
| avg_sent_length  |     17.9758 | 19.8758 | -1.9000 |   0.0696 |   0.1418 | ns    | -0.3790 |
| det_ratio        |      0.0851 |  0.0767 |  0.0084 |   0.4524 |   0.6182 | ns    |  0.2269 |
| noun_ratio       |      0.3105 |  0.3458 | -0.0353 |   0.0215 |   0.0801 | ns    | -0.5643 |
| opener_diversity |      0.9733 |  1.0000 | -0.0267 | nan      | nan      | n/a   | -0.3142 |
| pron_ratio       |      0.0632 |  0.0336 |  0.0296 |   0.0215 |   0.0801 | ns    |  0.6881 |
| sent_length_std  |      6.5224 |  5.1387 |  1.3837 |   0.1429 |   0.2547 | ns    |  0.3661 |
| sentence_count   |      4.7500 |  4.4500 |  0.3000 |   0.3027 |   0.4964 | ns    |  0.2555 |
| verb_ratio       |      0.1366 |  0.1354 |  0.0012 |   0.8695 |   0.9694 | ns    |  0.0417 |

### Readability

| Feature              |   Clinician |   Model |       Δ |      p |   p_adj | Sig   |       d |
|:---------------------|------------:|--------:|--------:|-------:|--------:|:------|--------:|
| coleman_liau         |     12.7828 | 16.9081 | -4.1253 | 0.0000 |  0.0001 | ***   | -1.1174 |
| flesch_kincaid_grade |     10.7161 | 13.8724 | -3.1563 | 0.0006 |  0.0048 | **    | -0.9281 |
| flesch_reading_ease  |     46.7490 | 25.6371 | 21.1120 | 0.0001 |  0.0008 | ***   |  1.1055 |

### Stylistic Features

| Feature                |   Clinician |   Model |       Δ |        p |    p_adj | Sig   |       d |
|:-----------------------|------------:|--------:|--------:|---------:|---------:|:------|--------:|
| adjective_pct          |      0.0820 |  0.1073 | -0.0253 |   0.0032 |   0.0185 | *     | -0.7465 |
| adverb_pct             |      0.0235 |  0.0287 | -0.0051 |   0.4074 |   0.5759 | ns    | -0.1880 |
| first_person_pronouns  |      0.1500 |  0.0000 |  0.1500 | nan      | nan      | n/a   |  0.4094 |
| function_word_pct      |      0.4089 |  0.3420 |  0.0669 |   0.0000 |   0.0007 | ***   |  1.2621 |
| passive_voice_ratio    |      0.3917 |  0.2400 |  0.1517 |   0.0310 |   0.0849 | ns    |  0.5508 |
| second_person_pronouns |      0.0000 |  0.0000 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| the_patient_count      |      1.5500 |  1.1000 |  0.4500 |   0.2015 |   0.3442 | ns    |  0.3065 |
| third_person_pronouns  |      3.4500 |  1.8500 |  1.6000 |   0.0331 |   0.0849 | ns    |  0.5275 |

### Sentiment & Tone

| Feature           |   Clinician |   Model |       Δ |      p |   p_adj | Sig   |       d |
|:------------------|------------:|--------:|--------:|-------:|--------:|:------|--------:|
| polarity          |      0.0282 |  0.0167 |  0.0115 | 0.3884 |  0.5759 | ns    |  0.1181 |
| reassurance_count |      0.6000 |  0.6000 |  0.0000 | 1.0000 |  1.0000 | ns    |  0.0000 |
| subjectivity      |      0.3804 |  0.4258 | -0.0454 | 0.8124 |  0.9516 | ns    | -0.1663 |
| warning_count     |      0.8500 |  1.1000 | -0.2500 | 0.8945 |  0.9694 | ns    | -0.1236 |

### Clinical Communication

| Feature                 |   Clinician |   Model |       Δ |        p |    p_adj | Sig   |       d |
|:------------------------|------------:|--------:|--------:|---------:|---------:|:------|--------:|
| causal_connectives      |      0.9000 |  0.3500 |  0.5500 |   0.0437 |   0.0995 | ns    |  0.5238 |
| certainty_markers       |      0.6000 |  0.4500 |  0.1500 |   0.5488 |   0.7259 | ns    |  0.2013 |
| contrastive_connectives |      0.2000 |  0.2500 | -0.0500 |   1.0000 |   1.0000 | ns    | -0.0980 |
| hedge_certainty_ratio   |      0.4583 |  0.4583 |  0.0000 |   0.8984 |   0.9694 | ns    |  0.0000 |
| hedge_epistemic         |      0.4500 |  0.3500 |  0.1000 |   0.7812 |   0.9516 | ns    |  0.1269 |
| hedge_evidential        |      0.0500 |  0.0500 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| medical_abbreviations   |      0.9500 |  1.6500 | -0.7000 |   0.0359 |   0.0866 | ns    | -0.5071 |
| meta_referential        |      0.0000 |  0.0000 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| non_ascii               |      0.0000 |  0.0000 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| temporal_connectives    |      0.3500 |  0.8000 | -0.4500 |   0.0312 |   0.0849 | ns    | -0.5928 |
| total_connectives       |      1.4500 |  1.4000 |  0.0500 |   0.6768 |   0.8671 | ns    |  0.0349 |
| total_hedging           |      0.5000 |  0.4000 |  0.1000 |   0.7930 |   0.9516 | ns    |  0.1097 |

## 3. Variability Analysis

Variance ratio = clinician variance / model variance. >1 means clinician adapts more per case.

| Feature                      |   Clin Mean |   Clin Std |   Model Mean |   Model Std |   Var Ratio |
|:-----------------------------|------------:|-----------:|-------------:|------------:|------------:|
| syn_opener_diversity         |       0.973 |      0.085 |        1.000 |       0.000 |     inf     |
| sty_first_person_pronouns    |       0.150 |      0.366 |        0.000 |       0.000 |     inf     |
| clin_causal_connectives      |       0.900 |      0.968 |        0.350 |       0.489 |       3.912 |
| sty_the_patient_count        |       1.550 |      1.234 |        1.100 |       0.641 |       3.712 |
| syn_pron_ratio               |       0.063 |      0.039 |        0.034 |       0.026 |       2.168 |
| lex_word_count               |      73.500 |      2.373 |       72.700 |       1.720 |       1.904 |
| lex_budget_utilization       |       0.980 |      0.032 |        0.969 |       0.023 |       1.904 |
| sty_function_word_pct        |       0.409 |      0.065 |        0.342 |       0.051 |       1.636 |
| clin_certainty_markers       |       0.600 |      0.754 |        0.450 |       0.605 |       1.554 |
| sty_third_person_pronouns    |       3.450 |      2.481 |        1.850 |       2.110 |       1.383 |
| syn_avg_parse_depth          |       5.299 |      1.181 |        5.321 |       1.005 |       1.380 |
| clin_hedge_epistemic         |       0.450 |      0.686 |        0.350 |       0.587 |       1.366 |
| clin_total_hedging           |       0.500 |      0.761 |        0.400 |       0.681 |       1.250 |
| sent_polarity                |       0.028 |      0.083 |        0.017 |       0.074 |       1.248 |
| sty_passive_voice_ratio      |       0.392 |      0.279 |        0.240 |       0.252 |       1.223 |
| lex_hapax_ratio              |       0.599 |      0.072 |        0.670 |       0.068 |       1.121 |
| lex_ttr                      |       0.756 |      0.046 |        0.791 |       0.044 |       1.104 |
| syn_adv_ratio                |       0.024 |      0.021 |        0.029 |       0.020 |       1.098 |
| sty_adverb_pct               |       0.024 |      0.021 |        0.029 |       0.020 |       1.098 |
| syn_sentence_count           |       4.750 |      0.851 |        4.450 |       0.826 |       1.062 |
| lex_hapax_legomena           |      44.000 |      4.984 |       48.700 |       4.921 |       1.026 |
| clin_hedge_evidential        |       0.050 |      0.224 |        0.050 |       0.224 |       1.000 |
| lex_avg_word_length          |       5.385 |      0.539 |        6.121 |       0.542 |       0.988 |
| clin_total_connectives       |       1.450 |      1.099 |        1.400 |       1.142 |       0.925 |
| read_coleman_liau            |      12.783 |      2.906 |       16.908 |       3.062 |       0.901 |
| syn_verb_ratio               |       0.137 |      0.032 |        0.135 |       0.034 |       0.892 |
| clin_contrastive_connectives |       0.200 |      0.410 |        0.250 |       0.444 |       0.853 |
| syn_noun_ratio               |       0.310 |      0.051 |        0.346 |       0.055 |       0.852 |
| clin_hedge_certainty_ratio   |       0.458 |      0.362 |        0.458 |       0.397 |       0.833 |
| clin_medical_abbreviations   |       0.950 |      1.191 |        1.650 |       1.348 |       0.780 |
| sent_reassurance_count       |       0.600 |      0.598 |        0.600 |       0.681 |       0.773 |
| syn_adp_ratio                |       0.109 |      0.022 |        0.100 |       0.025 |       0.746 |
| syn_det_ratio                |       0.085 |      0.032 |        0.077 |       0.038 |       0.735 |
| lex_unique_words             |      55.500 |      2.893 |       57.500 |       3.380 |       0.733 |
| clin_temporal_connectives    |       0.350 |      0.587 |        0.800 |       0.696 |       0.712 |
| read_flesch_reading_ease     |      46.749 |     13.467 |       25.637 |      15.979 |       0.710 |
| syn_avg_sent_length          |      17.976 |      3.238 |       19.876 |       3.868 |       0.701 |
| read_flesch_kincaid_grade    |      10.716 |      2.001 |       13.872 |       2.494 |       0.644 |
| syn_adj_ratio                |       0.082 |      0.042 |        0.107 |       0.052 |       0.642 |
| sty_adjective_pct            |       0.082 |      0.042 |        0.107 |       0.052 |       0.642 |
| syn_sent_length_std          |       6.522 |      2.130 |        5.139 |       2.961 |       0.517 |
| lex_mtld                     |      86.981 |     15.979 |      100.758 |      22.767 |       0.493 |
| sent_warning_count           |       0.850 |      1.268 |        1.100 |       2.150 |       0.348 |
| sent_subjectivity            |       0.380 |      0.167 |        0.426 |       0.289 |       0.335 |

Median variance ratio: 0.96

## Literature Comparison

Testing established AI-text findings in the clinical QA domain:

| Finding                              | Source                 | Expected                            | Observed                       | Confirmed   |
|:-------------------------------------|:-----------------------|:------------------------------------|:-------------------------------|:------------|
| Lower lexical diversity (TTR)        | All 5 papers           | model < clinician                   | clin=0.756, model=0.791 (ns)   | No          |
| Fewer unique words                   | Stelmakh+, Culda+      | model < clinician                   | clin=55.500, model=57.500 (ns) | No          |
| More uniform sentence lengths        | All 5 papers           | model < clinician                   | clin=6.522, model=5.139 (ns)   | Trend       |
| More nouns, fewer adjectives/adverbs | Tercon, Contrasting    | model < clinician                   | clin=0.082, model=0.107 (*)    | No          |
| Less passive voice                   | Culda et al.           | model < clinician                   | clin=0.392, model=0.240 (ns)   | Trend       |
| More readable (lower grade level)    | Culda+, Stelmakh+      | model < clinician                   | clin=10.716, model=13.872 (**) | No          |
| More positive sentiment              | Stelmakh+, Contrasting | model > clinician                   | clin=0.028, model=0.017 (ns)   | No          |
| Lower subjectivity                   | Stelmakh et al.        | model < clinician                   | clin=0.380, model=0.426 (ns)   | No          |
| Higher consistency (lower variance)  | Stelmakh et al.        | model variance < clinician variance | Median var ratio: 0.96         | No          |

## 5. Full Case Gallery

All paired cases with key per-case metrics.

### Case 5 (divergence: 0.434)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    75   |
| Sentences |         6   |     3   |
| FK Grade  |         8.2 |    17.1 |

**Clinician**: The chest pain was musculoskeletal, not overdose or cardiac related. On exam the patient reported more pain with movement and pain with palpation. An EKG showed no ischemia and blood tests confirmed that the patient did not have a heart attack. A transthoracic echocardiogram (TTE) of the patient's heart was performed to rule out cardiac events. TTE results were normal. The patient was monitored on telemetry which did not show any significant cardiac events.

**Model**: Cardiac monitoring, EKGs, enzymes, and echocardiogram during hospitalization for confusion showed no heart attack, no structural heart damage, and no arrhythmias. During hospitalization the chest pain behaved like musculoskeletal pain because palpation and movement reproducibly worsened it. The musculoskeletal pattern of pain and normal cardiac testing indicated the pain was more likely from a musculoskeletal source than from a cardiac complication of the medications and street drugs used, although symptoms still warranted primary care follow-up.

---

### Case 13 (divergence: 0.429)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |      75 |
| Sentences |         4   |       5 |
| FK Grade  |         9.8 |      15 |

**Clinician**: Doctors wanted the patient to stay in the hospital to further work up her leg issue. They informed her that she needed physical therapy evaluation and that she may be at risk for paralysis if she leaves the hospital. However, the patient still chose to leave against medical advice. Based on clinical knowledge, I would recommend the patient returns to the hospital right away if she is still in pain and cannot move her legs.

**Model**: The patient had been admitted for leg numbness and weakness. MRI of the thoracic and lumbar spine showed degenerative disc disease without spinal cord compromise. Neurology recommended continued hospitalization for neck MRI and physical therapy evaluation before discharge. The team warned that leaving without this evaluation could result in permanent paralysis. Given this documented paralysis risk with unresolved leg symptoms, the patient should return immediately for emergency in-hospital reassessment rather than wait for outpatient follow-up.

---

### Case 17 (divergence: 0.410)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    72   |
| Sentences |         4   |     6   |
| FK Grade  |        13.2 |    10.9 |

**Clinician**: Palpitations may occur if sleep apnea is untreated. Patient was diagnosed with hypercarbia due to severe sleep apnea and noncompliance with wearing a CPAP at night, which is worsening this patient's hypoventilation. Hypoventilation can lead to palpitations due to lack of oxygen in the blood. It is important that he keeps his appointments and continues to take his psychosis medications as prescribed, as noncompliance can lead to an increase in anxiety and schizophrenic episodes.

**Model**: The patient should take levothyroxine 150 mcg daily to treat hypothyroidism after thyroidectomy. He should take calcium carbonate 1250 mg three times daily as prescribed. He should separate levothyroxine and calcium doses by at least four hours. He should use auto-CPAP whenever he sleeps to treat severe obstructive sleep apnea. He should attend scheduled follow-up visits with PCP, neurology, pulmonary, ENT, and endocrinology. He should obtain TSH and related outpatient labs before endocrinology follow-up.

---

### Case 18 (divergence: 0.399)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    75   |
| Sentences |         5   |     4   |
| FK Grade  |         8.8 |    18.6 |

**Clinician**: Patient has a history of Crohn's Disease. This could cause diarrhea and vomiting if he is having a flare up of the disease. The patient was sent home on narcotics for pain, which can cause constipation; it was recommended he take a stool softener and increase his fluid and fiber intake. Severe constipation can cause diarrhea and vomiting. The patient should be evaluated by a doctor to rule out what is causing his symptoms.

**Model**: The patient tolerated diet without abdominal pain, nausea, or vomiting and remained hemodynamically stable during hospitalization. At discharge, he was afebrile, ambulating, tolerating diet, voiding independently, and had well-controlled pain. The discharge documentation did not mention diarrhea or vomiting or provide return-precautions for new gastrointestinal symptoms, so whether his current diarrhea and vomiting warrant ER evaluation cannot be determined from this note. Discharge instructions focused on deep-breathing exercises and preventing constipation from narcotic pain medications.

---

### Case 12 (divergence: 0.379)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        73   |    72   |
| Sentences |         4   |     4   |
| FK Grade  |        11.1 |    12.7 |

**Clinician**: The patient's chest pain is not a cardiac related issue based off her EKG and cardiac labs. Her stomach pain was able to be controlled with anti-nausea medication and insulin, and she received nitroglycerin for her chest pain. From my clinical knowledge, it is possible that this stomach pain is due to uncontrolled diabetes because she needed insulin in the emergency department. The patient will follow up with her PCP for abdominal pain.

**Model**: The patient had abdominal pain along with chest pain that prompted hospital evaluation. EKG and cardiac marker testing showed no changes and no signs of heart problems or blockages, so the pain did not come from coronary artery disease. Abdominal pain improved with anti-nausea medicine and insulin, findings consistent with a non-cardiac source for her symptoms. If the pain continues, the next step is further evaluation for abdominal pain as previously recommended.

---

### Case 8 (divergence: 0.355)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    71   |
| Sentences |         5   |     4   |
| FK Grade  |        11.1 |    17.9 |

**Clinician**: Patient has cirrhosis due to alcohol abuse. The long-term liver damage caused toxin buildup in the blood resulting in jaundice and kidney disease. Treatment of the toxin buildup with hydration and medications reduced her score for End-Stage Live Disease (MELD) and improved her creatinine and kidney function. Testing will determine if there may be longterm cognitive deficits related to alcohol abuse. She was diagnosed with a mania and suggested psychiatric treatment to control it.

**Model**: The patient had jaundice from cirrhosis and kidney disease, with toxin buildup from these conditions treated using hydration and medications. Hydration, medications to reduce toxins, and diuretics improved organ function, including creatinine and MELD score, before discharge. Psychiatry diagnosed a manic episode with hallucinations, pressured speech, and disorganized thoughts, which normalized after treatment with Haldol. Psychiatry recommended neuropsychological testing for possible longterm cognitive deficits associated with alcohol use and alcohol-related disease.

---

### Case 19 (divergence: 0.322)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    72   |
| Sentences |         4   |     6   |
| FK Grade  |        10.3 |     8.1 |

**Clinician**: At the hospital, a work up for chest pain showed her pain was unrelated to cardiovascular issues. The tests and procedures were normal, including an EKG, labs, CAT scan, stress test, and a more specific heart study. The doctors believe that anxiety is the cause of her symptoms, so she was started on anti-anxiety medications. She received Ativan in the hospital which improved her pain leading the doctors to believe anxiety was the cause.

**Model**: The patient was admitted for evaluation of chest pain. The hospital evaluation included EKGs, cardiac blood tests, and a chest CT to assess for vascular or lung causes. These tests were all normal. A stress test and MIBI study also did not show heart problems. Ativan and Tylenol improved the patients chest pain. Sertraline was started to help with anxiety, which might be causing the chest pain rather than a cardiovascular process.

---

### Case 15 (divergence: 0.312)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        66   |    71   |
| Sentences |         5   |     4   |
| FK Grade  |         8.7 |    16.6 |

**Clinician**: The patient was prescribed Bactrim and Levofloxacin for treatment of his skin infection, as well as antivirals for prophylaxis for possible HIV infection. From my clinical knowledge, it is possible that these antibiotics have caused a decrease in sperm count and/or sperm movement. This should not be a long term issue. Once antibiotics are completed, this issue should resolve. He should not be concerned for infertility.

**Model**: The patient presented with penis and scrotum swelling, which evaluation attributed to a likely penile surface skin infection. The treatment targeted this superficial infection with oral antibiotics Bactrim and levofloxacin and advised close follow-up for eradication of infection. The instructions did not describe involvement of the testicles, prostate, or seminal vesicles or any infection-related fertility impairment. The patient also received emtricitabine-tenofovir and lopinavir-ritonavir as short-term two-week prophylaxis for possible HIV infection.

---

### Case 2 (divergence: 0.294)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        73   |    72   |
| Sentences |         3   |     3   |
| FK Grade  |        13.6 |    14.6 |

**Clinician**: The patient was given Lasix for acute diastolic heart failure with symptoms including shortness of breath and lower extremity edema. The patient was given 8 liters of fluid to help maintain his blood pressure which contributed to his respiratory failure. After the patient's heart failure was treated with Lasix, he showed improvement in shortness of breath and his oxygen requirement, and he only needed to remain on a small amount of oxygen for comfort.

**Model**: The patient had acute diastolic heart failure with volume overload, causing shortness of breath, increased oxygen requirement, and lower extremity leg edema. In this setting he was diuresed with IV and infusion lasix then oral torsemide, which improved his symptoms. As his ventilation and oxygenation stabilized and he was successfully extubated, he required only a small amount of supplemental oxygen for comfort, so the oxygen flow rate was reduced at that time.

---

### Case 11 (divergence: 0.285)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    75   |
| Sentences |         5   |     4   |
| FK Grade  |         9.8 |    13.6 |

**Clinician**: The patient was diagnosed with aseptic viral meningitis and completed treatment prior to discharge. It is expected that she may still have some symptoms when she is home resting based off the medications prescribed on discharge. She was prescribed PO dilaudid, tylenol, and advil as needed for pain. She was prescribed PO zofran for nausea management prn. With these medications prescribed, it appears that she will still experience pain and nausea during her recovery process.

**Model**: The patient had meningitis with headaches, neck stiffness, and fevers and was found to have viral, non-bacterial meningitis. CSF studies and blood tests ruled out bacterial, HSV, and Lyme meningitis and supported the diagnosis of aseptic meningitis. She initially received IV vancomycin, ceftriaxone, and acyclovir, but these therapies were stopped by discharge when her illness was concluded to be aseptic meningitis. She was discharged to recover with pain medications and ondansetron for nausea as needed.

---

### Case 16 (divergence: 0.270)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    74   |
| Sentences |         4   |     4   |
| FK Grade  |        11.6 |    13.2 |

**Clinician**: Patient's back pain is consistent with musculoskeletal pain related to muscle spasms. The doctors recommended weight loss as well as follow up with a physical therapist and pain clinic. The only other concern, is her abdominal pain, which the gastrointestinal team believe to be referred or radiating from the back pain she is having. While outpatient pain consult and integrative medicine consult were discussed with patient at discharge, no concerns for stroke were discussed.

**Model**: The patient had a several-year history of severe epigastric abdominal pain and chronic crampy bilateral mid-back pain. She also reported upper back pain that was considered possibly related to the abdominal pain. Teams felt the mid-back pain was more consistent with musculoskeletal muscle spasm and discussed weight loss. Back imaging was obtained, and the plan emphasized physical therapy, oxycodone, and pain clinic followup, treating the pain as musculoskeletal rather than as a stroke manifestation.

---

### Case 10 (divergence: 0.268)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    73   |
| Sentences |         5   |     5   |
| FK Grade  |        12.1 |    13.9 |

**Clinician**: The patient had a pulseless electrical activity arrest with subsequent anoxic brain injury. His mental status improved, though he had seizures and became impulsive with poor motor planning leading to falls. The patient may improve neurologically but he will likely have recurrent seizures. Additionally, the patient remains confused at times and requires assistance with ambulation. The brain damages this patient sustained after the heart attack will require intensive treatment in an anoxic brain injury unit.

**Model**: The patient sustained an anoxic brain injury after PEA cardiac arrests associated with severe asthma, hypoxemia, and acidosis. Early EEG showed no evident brain activity and he remained comatose with a guarded prognosis on hospital day 3. Over subsequent days he was weaned off the ventilator, breathed independently, and his mental status progressively improved. He developed seizures attributed to hypoxic brain injury and required antiepileptic therapy. At discharge he remained confused but neurologically improving.

---

### Case 20 (divergence: 0.261)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    74   |
| Sentences |         6   |     5   |
| FK Grade  |         9.9 |    13.5 |

**Clinician**: Neurology doctors completed a series of tests and procedures to determine the cause of headaches. They ruled out elevated intracranial pressure and blood clots. Verapamil was started once daily to prevent headaches. Based on clinical knowledge, spinning sensation with a migraine is vertigo caused by the migraine. A migraine with aura can also cause dizziness. To achieve optimal control of migraines, patient was recommended to avoid caffeine and keep a regular sleep wake cycle.

**Model**: The patient was evaluated on the neurology ward for headaches of unusual quality. The evaluation used CT and MRI imaging, laboratory studies, and lumbar puncture to search for a cause. These tests ruled out serious intracranial headache causes, including pseudotumor cerebri from elevated intracranial pressure. MR venography also ruled out cerebral venous thrombosis as a cause of her headaches. With these causes excluded, the team treated the headaches as migraine, giving migraine-specific discharge instructions.

---

### Case 3 (divergence: 0.257)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        72   |    74   |
| Sentences |         5   |     4   |
| FK Grade  |         9.2 |    12.5 |

**Clinician**: This patient should expect to have drowsiness, headaches, dizziness, irritability, and short-term memory loss with a head injury. These symptoms will decrease over the next few weeks. It is important to follow up with a specialist in traumatic brain injuries. The patient needs time to recover and needs to be aware of any new symptoms he has. He should report visual changes, weakness on one side of his body, and/or speech difficulty.

**Model**: The patient sustained a traumatic brain injury from a fall that did not require surgery. The patient may have drowsiness, headaches, dizziness, irritability, and short term memory loss, which are normal after this head injury and should decrease over the next several weeks. The overall expected course is gradual recovery over several weeks with progressive improvement in these symptoms. The patient should follow up with the traumatic brain injury specialist and report concerning symptoms.

---

### Case 4 (divergence: 0.246)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        70   |      70 |
| Sentences |         4   |       5 |
| FK Grade  |        15.1 |      14 |

**Clinician**: The patient was recommended a cardiac catheterization for worsening heart failure confirmed by left ventricle ejection fraction of 25% on his echocardiogram. He had low output heart failure which caused increasing intra-abdominal pressure resulting in congestive hepatopathy, abdominal pain, and right upper quadrant abdominal tenderness. The cardiac catheterization showed the patient needed milrinone for treatment. Milrinone infusion improved the patient's heart pump function by significantly improving cardiac output and wedge pressure.

**Model**: The patient had idiopathic dilated cardiomyopathy with LVEF 25% and acute-on-chronic systolic heart failure. He was admitted in low-output heart failure with increased intra-abdominal pressures and syncope. He underwent right heart catheterization specifically for a milrinone trial. During catheterization, milrinone reduced his wedge pressure and increased his cardiac index, improving cardiac output. The cardiac catheterization therefore showed he would benefit from ongoing milrinone therapy for advanced heart failure and transplant evaluation.

---

### Case 1 (divergence: 0.232)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        78   |    73   |
| Sentences |         5   |     4   |
| FK Grade  |         9.3 |    12.4 |

**Clinician**: An endoscopic retrograde cholangiopancreatography, ERCP, was recommended to place a common bile duct stent. This stent was placed to allow drainage of the biliary obstruction which was caused by stones and sludge. Due to no improvement in liver function, the patient needed a repeat ERCP. The repeat ERCP showed that the biliary stent placed in the first ERCP was obstructed by stones and sludge. The stones and stent were successfully removed during this procedure by performing a sphincterotomy.

**Model**: ERCP was recommended to treat common bile duct obstruction from stones and sludge, requiring stent placement to restore biliary drainage. Frank pus from the duct showed infected obstruction, so endoscopic drainage and IV antibiotics were required. Despite stenting, LFTs and bilirubin rose, and repeat ERCP showed the stent obstructed by sludge and stones. After INR normalized, sphincterotomy with stone and stent removal cleared the obstruction, confirming that endoscopic therapy, not medication, resolved it.

---

### Case 9 (divergence: 0.222)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    74   |
| Sentences |         6   |     5   |
| FK Grade  |        13.7 |    13.2 |

**Clinician**: Due to significant blood loss, elevated LFTs and creatinine, the patient received multiple blood transfusions and fluids requiring intubation and ICU management. She had end-stage organ dysfunction, abdominal compartment syndrome requiring surgery, and continuous dialysis for acute kidney injury. The cerebral edema was managed by neurosurgery. Low cortisol levels were treated with hydrocortisone. The abdomen was left open due to bleeding and then closed successfully. Due to liver failure, she was listed for liver transplantation.

**Model**: The patient underwent emergent C-section for fetal distress complicated by 1.7 liters blood loss and liver dysfunction. She received blood products, large-volume saline, intubation, and ICU care for presumed fatty liver of pregnancy. Abdominal compartment syndrome with ongoing bleeding led to decompressive laparotomy, temporary open abdomen, and later washouts. She developed fulminant hepatic failure and acute kidney injury and received management including CVVH. She had uneventful abdominal closure on POD5; later treatment effects are unknown.

---

### Case 7 (divergence: 0.211)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    71   |
| Sentences |         4   |     4   |
| FK Grade  |         7.9 |    10.8 |

**Clinician**: The patient no longer needs to take her Coumadin for her deep vein thrombosis history. She had a filter placed to prevent clots from returning to her heart. This filter is called an IVC filter, and she received it due to her prolonged bed rest and risk of developing a clot. The patient will need to follow up with her doctor and get a repeat CT scan of her brain to evaluate the subarachnoid hemorrhage.

**Model**: The patient had a history of DVT treated with coumadin, which she took before the injury. During hospitalization she received an IVC filter, and the team discontinued coumadin after the filter placement. Discharge instructions specified that she would not have to continue coumadin because the IVC filter would prevent clots returning to her heart. Thus, current management used the IVC filter instead of continuing coumadin to provide protection against venous clots.

---

### Case 6 (divergence: 0.205)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        73   |    70   |
| Sentences |         6   |     5   |
| FK Grade  |        11.5 |    14.9 |

**Clinician**: Preliminary tests showed Candida infection in the blood. The sputum test revealed yeast along with gram positive cocci and gram negative rods. Lung infection was treated with antibiotics (vancomcyin, linezolid, amikacin, ambisome, tobramycin). The antibiotics did not improve the patient's condition as shown by worsening chest x-ray, white blood cell count, and respiratory distress. After discussions with family and physicians, medical treatment was gradually reduced to comfort measures only. The patient died peacefully.

**Model**: The patient developed pneumonia with productive cough and left lower lobe consolidation. Initial sputum gram stain showed gram positive cocci, gram negative rods, and yeast. He was started on vancomycin and another antibacterial on September 30 for presumed bacterial pneumonia. Micafungin, an antifungal, was only added on October 3 after ID consultation. A subsequent blood and fungal culture preliminarily grew Torulopsis glabrata, confirming significant fungal infection in addition to the bacterial pneumonia.

---

### Case 14 (divergence: 0.197)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        72   |    71   |
| Sentences |         5   |     5   |
| FK Grade  |         9.5 |    13.9 |

**Clinician**: The patient does not have any evidence of stomach cancer. She does see an oncologist for bladder cancer, though. The patient's lower left side pain was due to a partial bowel obstruction, blockage in her intestine. Her symptoms improved over time, but she needs to be very careful with becoming constipated as that can worsen her symptoms of an intestinal blockage. The doctors recommended that she take fiber supplements to prevent constipation.

**Model**: The patient was hospitalized for a partial small bowel obstruction that improved with time. The discharge instructions focused on managing constipation and recommending fiber supplementation for ongoing symptoms. The only malignancy specifically identified was bladder cancer, for which oncology follow-up was arranged. The plan also included gastroenterology follow-up, but no stomach mass, lesion, or cancer was described. Based on this documentation, there was no recorded evidence or diagnosis of stomach cancer.

---
