# Linguistic Comparison Report: Model vs. Clinician

**Configuration**: Three-Step

## 1. Overview

- Cases analyzed: 20
- Features compared: 47
- Statistically significant differences (BH-adjusted p<0.05): 6 of 47

## 2. Full Feature Comparison

### Lexical Features

| Feature            |   Clinician |   Model |       Δ |      p |   p_adj | Sig   |       d |
|:-------------------|------------:|--------:|--------:|-------:|--------:|:------|--------:|
| avg_word_length    |      5.3852 |  5.7845 | -0.3993 | 0.0017 |  0.0265 | *     | -0.8339 |
| budget_utilization |      0.9800 |  0.9787 |  0.0013 | 0.6685 |  0.8356 | ns    |  0.0476 |
| hapax_legomena     |     44.0000 | 46.5500 | -2.5500 | 0.1122 |  0.3114 | ns    | -0.3469 |
| hapax_ratio        |      0.5995 |  0.6338 | -0.0343 | 0.1650 |  0.3666 | ns    | -0.3329 |
| mtld               |     86.9815 | 90.9524 | -3.9710 | 0.3736 |  0.6227 | ns    | -0.1471 |
| ttr                |      0.7559 |  0.7701 | -0.0142 | 0.2862 |  0.5724 | ns    | -0.2217 |
| unique_words       |     55.5000 | 56.5500 | -1.0500 | 0.2541 |  0.5349 | ns    | -0.2370 |
| word_count         |     73.5000 | 73.4000 |  0.1000 | 0.6486 |  0.8356 | ns    |  0.0476 |

### Syntactic Features

| Feature          |   Clinician |   Model |       Δ |        p |    p_adj | Sig   |       d |
|:-----------------|------------:|--------:|--------:|---------:|---------:|:------|--------:|
| adj_ratio        |      0.0820 |  0.1053 | -0.0233 |   0.0522 |   0.1740 | ns    | -0.5477 |
| adp_ratio        |      0.1094 |  0.0881 |  0.0213 |   0.0304 |   0.1398 | ns    |  0.6119 |
| adv_ratio        |      0.0235 |  0.0289 | -0.0054 |   0.4723 |   0.7266 | ns    | -0.1725 |
| avg_parse_depth  |      5.2992 |  4.5757 |  0.7235 |   0.0323 |   0.1398 | ns    |  0.5575 |
| avg_sent_length  |     17.9758 | 19.1692 | -1.1933 |   0.3316 |   0.6227 | ns    | -0.2406 |
| det_ratio        |      0.0851 |  0.0781 |  0.0069 |   0.3736 |   0.6227 | ns    |  0.1585 |
| noun_ratio       |      0.3105 |  0.3113 | -0.0009 |   0.8124 |   0.9557 | ns    | -0.0143 |
| opener_diversity |      0.9733 |  1.0000 | -0.0267 | nan      | nan      | n/a   | -0.3142 |
| pron_ratio       |      0.0632 |  0.0613 |  0.0019 |   0.9563 |   1.0000 | ns    |  0.0428 |
| sent_length_std  |      6.5224 |  4.6391 |  1.8833 |   0.0005 |   0.0193 | *     |  0.9214 |
| sentence_count   |      4.7500 |  4.6500 |  0.1000 |   0.6277 |   0.8356 | ns    |  0.0798 |
| verb_ratio       |      0.1366 |  0.1409 | -0.0043 |   0.7337 |   0.8894 | ns    | -0.1290 |

### Readability

| Feature              |   Clinician |   Model |       Δ |      p |   p_adj | Sig   |       d |
|:---------------------|------------:|--------:|--------:|-------:|--------:|:------|--------:|
| coleman_liau         |     12.7828 | 14.9648 | -2.1820 | 0.0027 |  0.0271 | *     | -0.8172 |
| flesch_kincaid_grade |     10.7161 | 12.5155 | -1.7994 | 0.0049 |  0.0324 | *     | -0.7362 |
| flesch_reading_ease  |     46.7490 | 34.7742 | 11.9749 | 0.0020 |  0.0265 | *     |  0.8465 |

### Stylistic Features

| Feature                |   Clinician |   Model |       Δ |        p |    p_adj | Sig   |       d |
|:-----------------------|------------:|--------:|--------:|---------:|---------:|:------|--------:|
| adjective_pct          |      0.0820 |  0.1053 | -0.0233 |   0.0522 |   0.1740 | ns    | -0.5477 |
| adverb_pct             |      0.0235 |  0.0289 | -0.0054 |   0.4723 |   0.7266 | ns    | -0.1725 |
| first_person_pronouns  |      0.1500 |  0.0000 |  0.1500 | nan      | nan      | n/a   |  0.4094 |
| function_word_pct      |      0.4089 |  0.3844 |  0.0245 |   0.0637 |   0.1961 | ns    |  0.3854 |
| passive_voice_ratio    |      0.3917 |  0.2876 |  0.1040 |   0.1269 |   0.3114 | ns    |  0.3613 |
| second_person_pronouns |      0.0000 |  0.0000 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| the_patient_count      |      1.5500 |  0.9500 |  0.6000 |   0.0350 |   0.1398 | ns    |  0.5052 |
| third_person_pronouns  |      3.4500 |  3.5500 | -0.1000 |   0.8433 |   0.9637 | ns    | -0.0380 |

### Sentiment & Tone

| Feature           |   Clinician |   Model |       Δ |      p |   p_adj | Sig   |       d |
|:------------------|------------:|--------:|--------:|-------:|--------:|:------|--------:|
| polarity          |      0.0282 |  0.0139 |  0.0142 | 0.5706 |  0.8151 | ns    |  0.0796 |
| reassurance_count |      0.6000 |  0.8000 | -0.2000 | 0.3535 |  0.6227 | ns    | -0.2236 |
| subjectivity      |      0.3804 |  0.4265 | -0.0460 | 0.9273 |  1.0000 | ns    | -0.1666 |
| warning_count     |      0.8500 |  0.8000 |  0.0500 | 0.6367 |  0.8356 | ns    |  0.0405 |

### Clinical Communication

| Feature                 |   Clinician |   Model |       Δ |        p |    p_adj | Sig   |       d |
|:------------------------|------------:|--------:|--------:|---------:|---------:|:------|--------:|
| causal_connectives      |      0.9000 |  1.8000 | -0.9000 |   0.0089 |   0.0509 | ns    | -0.7440 |
| certainty_markers       |      0.6000 |  0.6000 |  0.0000 |   1.0000 |   1.0000 | ns    |  0.0000 |
| contrastive_connectives |      0.2000 |  0.1500 |  0.0500 | nan      | nan      | n/a   |  0.1269 |
| hedge_certainty_ratio   |      0.4583 |  0.4667 | -0.0083 |   0.9805 |   1.0000 | ns    | -0.0155 |
| hedge_epistemic         |      0.4500 |  0.3000 |  0.1500 |   0.5312 |   0.7870 | ns    |  0.2236 |
| hedge_evidential        |      0.0500 |  0.1500 | -0.1000 | nan      | nan      | n/a   | -0.2236 |
| medical_abbreviations   |      0.9500 |  1.4500 | -0.5000 |   0.1323 |   0.3114 | ns    | -0.3490 |
| meta_referential        |      0.0000 |  0.0000 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| non_ascii               |      0.0000 |  0.0000 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| temporal_connectives    |      0.3500 |  0.6000 | -0.2500 |   0.1250 |   0.3114 | ns    | -0.4544 |
| total_connectives       |      1.4500 |  2.5500 | -1.1000 |   0.0043 |   0.0324 | *     | -0.8247 |
| total_hedging           |      0.5000 |  0.4500 |  0.0500 |   1.0000 |   1.0000 | ns    |  0.0729 |

## 3. Variability Analysis

Variance ratio = clinician variance / model variance. >1 means clinician adapts more per case.

| Feature                      |   Clin Mean |   Clin Std |   Model Mean |   Model Std |   Var Ratio |
|:-----------------------------|------------:|-----------:|-------------:|------------:|------------:|
| syn_opener_diversity         |       0.973 |      0.085 |        1.000 |       0.000 |     inf     |
| sty_first_person_pronouns    |       0.150 |      0.366 |        0.000 |       0.000 |     inf     |
| sty_the_patient_count        |       1.550 |      1.234 |        0.950 |       0.224 |      30.474 |
| syn_avg_parse_depth          |       5.299 |      1.181 |        4.576 |       0.456 |       6.719 |
| syn_pron_ratio               |       0.063 |      0.039 |        0.061 |       0.020 |       3.540 |
| sty_third_person_pronouns    |       3.450 |      2.481 |        3.550 |       1.468 |       2.856 |
| lex_word_count               |      73.500 |      2.373 |       73.400 |       1.536 |       2.388 |
| lex_budget_utilization       |       0.980 |      0.032 |        0.979 |       0.020 |       2.388 |
| clin_total_hedging           |       0.500 |      0.761 |        0.450 |       0.510 |       2.222 |
| clin_hedge_epistemic         |       0.450 |      0.686 |        0.300 |       0.470 |       2.131 |
| sty_function_word_pct        |       0.409 |      0.065 |        0.384 |       0.045 |       2.104 |
| sty_passive_voice_ratio      |       0.392 |      0.279 |        0.288 |       0.192 |       2.101 |
| syn_verb_ratio               |       0.137 |      0.032 |        0.141 |       0.025 |       1.677 |
| read_flesch_kincaid_grade    |      10.716 |      2.001 |       12.516 |       1.571 |       1.622 |
| read_coleman_liau            |      12.783 |      2.906 |       14.965 |       2.349 |       1.531 |
| lex_avg_word_length          |       5.385 |      0.539 |        5.784 |       0.479 |       1.268 |
| clin_contrastive_connectives |       0.200 |      0.410 |        0.150 |       0.366 |       1.255 |
| clin_certainty_markers       |       0.600 |      0.754 |        0.600 |       0.681 |       1.227 |
| read_flesch_reading_ease     |      46.749 |     13.467 |       34.774 |      12.199 |       1.219 |
| lex_ttr                      |       0.756 |      0.046 |        0.770 |       0.042 |       1.198 |
| clin_causal_connectives      |       0.900 |      0.968 |        1.800 |       0.894 |       1.171 |
| lex_hapax_ratio              |       0.599 |      0.072 |        0.634 |       0.071 |       1.047 |
| syn_sent_length_std          |       6.522 |      2.130 |        4.639 |       2.172 |       0.962 |
| syn_adp_ratio                |       0.109 |      0.022 |        0.088 |       0.022 |       0.949 |
| clin_medical_abbreviations   |       0.950 |      1.191 |        1.450 |       1.234 |       0.931 |
| syn_noun_ratio               |       0.310 |      0.051 |        0.311 |       0.053 |       0.920 |
| clin_hedge_certainty_ratio   |       0.458 |      0.362 |        0.467 |       0.381 |       0.905 |
| sty_adverb_pct               |       0.024 |      0.021 |        0.029 |       0.022 |       0.869 |
| syn_adv_ratio                |       0.024 |      0.021 |        0.029 |       0.022 |       0.869 |
| sent_warning_count           |       0.850 |      1.268 |        0.800 |       1.399 |       0.821 |
| sty_adjective_pct            |       0.082 |      0.042 |        0.105 |       0.046 |       0.819 |
| syn_adj_ratio                |       0.082 |      0.042 |        0.105 |       0.046 |       0.819 |
| lex_hapax_legomena           |      44.000 |      4.984 |       46.550 |       5.558 |       0.804 |
| syn_avg_sent_length          |      17.976 |      3.238 |       19.169 |       3.697 |       0.767 |
| clin_total_connectives       |       1.450 |      1.099 |        2.550 |       1.276 |       0.742 |
| syn_sentence_count           |       4.750 |      0.851 |        4.650 |       0.988 |       0.741 |
| lex_mtld                     |      86.981 |     15.979 |       90.952 |      20.114 |       0.631 |
| lex_unique_words             |      55.500 |      2.893 |       56.550 |       3.677 |       0.619 |
| clin_temporal_connectives    |       0.350 |      0.587 |        0.600 |       0.754 |       0.606 |
| syn_det_ratio                |       0.085 |      0.032 |        0.078 |       0.047 |       0.474 |
| sent_reassurance_count       |       0.600 |      0.598 |        0.800 |       0.894 |       0.447 |
| sent_subjectivity            |       0.380 |      0.167 |        0.426 |       0.261 |       0.409 |
| clin_hedge_evidential        |       0.050 |      0.224 |        0.150 |       0.366 |       0.373 |
| sent_polarity                |       0.028 |      0.083 |        0.014 |       0.171 |       0.237 |

Median variance ratio: 0.96

## Literature Comparison

Testing established AI-text findings in the clinical QA domain:

| Finding                              | Source                 | Expected                            | Observed                       | Confirmed   |
|:-------------------------------------|:-----------------------|:------------------------------------|:-------------------------------|:------------|
| Lower lexical diversity (TTR)        | All 5 papers           | model < clinician                   | clin=0.756, model=0.770 (ns)   | No          |
| Fewer unique words                   | Stelmakh+, Culda+      | model < clinician                   | clin=55.500, model=56.550 (ns) | No          |
| More uniform sentence lengths        | All 5 papers           | model < clinician                   | clin=6.522, model=4.639 (*)    | Yes         |
| More nouns, fewer adjectives/adverbs | Tercon, Contrasting    | model < clinician                   | clin=0.082, model=0.105 (ns)   | No          |
| Less passive voice                   | Culda et al.           | model < clinician                   | clin=0.392, model=0.288 (ns)   | Trend       |
| More readable (lower grade level)    | Culda+, Stelmakh+      | model < clinician                   | clin=10.716, model=12.516 (*)  | No          |
| More positive sentiment              | Stelmakh+, Contrasting | model > clinician                   | clin=0.028, model=0.014 (ns)   | No          |
| Lower subjectivity                   | Stelmakh et al.        | model < clinician                   | clin=0.380, model=0.426 (ns)   | No          |
| Higher consistency (lower variance)  | Stelmakh et al.        | model variance < clinician variance | Median var ratio: 0.96         | No          |

## 5. Full Case Gallery

All paired cases with key per-case metrics.

### Case 2 (divergence: 0.395)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        73   |    74   |
| Sentences |         3   |     4   |
| FK Grade  |        13.6 |    12.4 |

**Clinician**: The patient was given Lasix for acute diastolic heart failure with symptoms including shortness of breath and lower extremity edema. The patient was given 8 liters of fluid to help maintain his blood pressure which contributed to his respiratory failure. After the patient's heart failure was treated with Lasix, he showed improvement in shortness of breath and his oxygen requirement, and he only needed to remain on a small amount of oxygen for comfort.

**Model**: The patient developed acute diastolic failure of the heart with volume overload, and this overload caused shortness of breath, increased oxygen requirement, and leg edema. This congestive heart failure was most likely secondary to worsening valvular disease. He received IV lasix and intermittent lasix infusion, and he then transitioned to oral torsemide so that excess fluid was removed and symptoms improved. After diuresis he required only low-flow oxygen for comfort, so it was reduced.

---

### Case 13 (divergence: 0.386)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    73   |
| Sentences |         4   |     4   |
| FK Grade  |         9.8 |    12.2 |

**Clinician**: Doctors wanted the patient to stay in the hospital to further work up her leg issue. They informed her that she needed physical therapy evaluation and that she may be at risk for paralysis if she leaves the hospital. However, the patient still chose to leave against medical advice. Based on clinical knowledge, I would recommend the patient returns to the hospital right away if she is still in pain and cannot move her legs.

**Model**: The patient had been admitted for leg numbness and weakness. MRI of the thoracic and lumbar spine showed stable degenerative disc disease without spinal cord compromise, and her neck was not imaged. The team advised her to stay for a neck MRI and a physical therapy evaluation and warned that leaving could result in permanent paralysis, but she left against medical advice. Her care therefore required in-hospital neurologic evaluation for this paralysis risk.

---

### Case 15 (divergence: 0.355)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        66   |    70   |
| Sentences |         5   |     3   |
| FK Grade  |         8.7 |    13.7 |

**Clinician**: The patient was prescribed Bactrim and Levofloxacin for treatment of his skin infection, as well as antivirals for prophylaxis for possible HIV infection. From my clinical knowledge, it is possible that these antibiotics have caused a decrease in sperm count and/or sperm movement. This should not be a long term issue. Once antibiotics are completed, this issue should resolve. He should not be concerned for infertility.

**Model**: The patient came with penis and scrotum swelling, and the evaluation showed that he likely had a superficial infection of the penile skin. The treatment plan treated this skin infection with Bactrim and levofloxacin, so he took these antibiotics until he finished the prescription and had close follow-up to confirm eradication. The note described a superficial infection of the penile skin and did not address any deeper infection or fertility.

---

### Case 12 (divergence: 0.340)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        73   |    75   |
| Sentences |         4   |     4   |
| FK Grade  |        11.1 |    11.9 |

**Clinician**: The patient's chest pain is not a cardiac related issue based off her EKG and cardiac labs. Her stomach pain was able to be controlled with anti-nausea medication and insulin, and she received nitroglycerin for her chest pain. From my clinical knowledge, it is possible that this stomach pain is due to uncontrolled diabetes because she needed insulin in the emergency department. The patient will follow up with her PCP for abdominal pain.

**Model**: The patient went to the hospital because she had abdominal pain together with chest pain. The EKG and cardiac marker testing showed no evidence of heart problems or blockages in her heart vessels, so a cardiac cause was unlikely. Her abdominal pain improved in the hospital because doctors treated it with anti-nausea medication and insulin. The exact cause of her abdominal pain still remained unclear based on this information, so she required outpatient follow up.

---

### Case 6 (divergence: 0.339)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        73   |    71   |
| Sentences |         6   |     5   |
| FK Grade  |        11.5 |    10.8 |

**Clinician**: Preliminary tests showed Candida infection in the blood. The sputum test revealed yeast along with gram positive cocci and gram negative rods. Lung infection was treated with antibiotics (vancomcyin, linezolid, amikacin, ambisome, tobramycin). The antibiotics did not improve the patient's condition as shown by worsening chest x-ray, white blood cell count, and respiratory distress. After discussions with family and physicians, medical treatment was gradually reduced to comfort measures only. The patient died peacefully.

**Model**: The patient had pneumonia with productive cough, and CXR showed LLL consolidation. The sputum gram stain showed bacteria and yeast, and this suggested a bacterial and fungal infection. He received vancomycin and an antibiotic from 9-30 with little improvement, so he started micafungin on 10-3 with ID. Fungal infection was recognized when a blood and fungal culture grew Torulopsis glabrata. On 10-8, his WBC and respiratory distress worsened, so he was started on ambisome.

---

### Case 18 (divergence: 0.329)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    74   |
| Sentences |         5   |     4   |
| FK Grade  |         8.8 |    14.6 |

**Clinician**: Patient has a history of Crohn's Disease. This could cause diarrhea and vomiting if he is having a flare up of the disease. The patient was sent home on narcotics for pain, which can cause constipation; it was recommended he take a stool softener and increase his fluid and fiber intake. Severe constipation can cause diarrhea and vomiting. The patient should be evaluated by a doctor to rule out what is causing his symptoms.

**Model**: The patient presented to ED for a motor vehicle collision with a tree and was admitted. He had Crohns disease on prednisone and Humera, with a pulmonary contusion and neck strain, and neurologic findings were normal. His cardiovascular and pulmonary status remained stable, and he tolerated diet without abdominal pain, nausea, or vomiting. Because discharge instructions covered only breathing exercises and constipation, record cannot determine whether new diarrhea and vomiting warrant an ER visit.

---

### Case 5 (divergence: 0.327)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    75   |
| Sentences |         6   |     4   |
| FK Grade  |         8.2 |    12.6 |

**Clinician**: The chest pain was musculoskeletal, not overdose or cardiac related. On exam the patient reported more pain with movement and pain with palpation. An EKG showed no ischemia and blood tests confirmed that the patient did not have a heart attack. A transthoracic echocardiogram (TTE) of the patient's heart was performed to rule out cardiac events. TTE results were normal. The patient was monitored on telemetry which did not show any significant cardiac events.

**Model**: The patient had taken medications and street drugs, and this caused confusion, so his heart rhythm was monitored. During hospitalization he reported chest pain that appeared musculoskeletal because it was reproducible with palpation and worsened with movement. Evaluation showed no ischemia on EKG, flat troponins, an unremarkable TTE, and normal ejection fraction, so a heart attack was unlikely. Findings supported pain in the musculoskeletal chest wall rather than heart damage from overdose as the cause.

---

### Case 17 (divergence: 0.314)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    72   |
| Sentences |         4   |     4   |
| FK Grade  |        13.2 |    14.3 |

**Clinician**: Palpitations may occur if sleep apnea is untreated. Patient was diagnosed with hypercarbia due to severe sleep apnea and noncompliance with wearing a CPAP at night, which is worsening this patient's hypoventilation. Hypoventilation can lead to palpitations due to lack of oxygen in the blood. It is important that he keeps his appointments and continues to take his psychosis medications as prescribed, as noncompliance can lead to an increase in anxiety and schizophrenic episodes.

**Model**: The patient should continue levothyroxine after thyroidectomy and attend endocrinology follow up to manage hypothyroidism, because this may help reduce palpitations and anxiety. He should separate levothyroxine and calcium carbonate doses by at least 4 hours, so thyroid hormone replacement can work properly. He should complete thyroid and metabolic labs before endocrinology visits, so treatment is guided by recent results. He should use auto-CPAP whenever he sleeps to treat severe obstructive sleep apnea.

---

### Case 20 (divergence: 0.290)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    73   |
| Sentences |         6   |     6   |
| FK Grade  |         9.9 |    11.9 |

**Clinician**: Neurology doctors completed a series of tests and procedures to determine the cause of headaches. They ruled out elevated intracranial pressure and blood clots. Verapamil was started once daily to prevent headaches. Based on clinical knowledge, spinning sensation with a migraine is vertigo caused by the migraine. A migraine with aura can also cause dizziness. To achieve optimal control of migraines, patient was recommended to avoid caffeine and keep a regular sleep wake cycle.

**Model**: The patient was evaluated on the neurology ward for unusual headaches. The team obtained CT, MRI, laboratory tests, and lumbar puncture to investigate the headaches. These tests ruled out serious intracranial causes of headache, including pseudotumor cerebri. The MRV then ruled out cerebral venous thrombosis. The team excluded these conditions, so they started verapamil as a new daily medication. Discharge instructions focused on optimal migraine control, which confirmed a migraine diagnosis by exclusion.

---

### Case 4 (divergence: 0.283)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        70   |    74   |
| Sentences |         4   |     7   |
| FK Grade  |        15.1 |    11.7 |

**Clinician**: The patient was recommended a cardiac catheterization for worsening heart failure confirmed by left ventricle ejection fraction of 25% on his echocardiogram. He had low output heart failure which caused increasing intra-abdominal pressure resulting in congestive hepatopathy, abdominal pain, and right upper quadrant abdominal tenderness. The cardiac catheterization showed the patient needed milrinone for treatment. Milrinone infusion improved the patient's heart pump function by significantly improving cardiac output and wedge pressure.

**Model**: The patient had idiopathic dilated cardiomyopathy and acute-on-chronic systolic heart failure, LVEF 25%. He presented with syncope, abdominal pain, and dyspnea from low-output heart failure and congestive hepatopathy. He underwent right-heart catheterization for milrinone trial. Catheterization showed he would benefit from milrinone. Milrinone improved output, wedge pressure, and pump function. He was maintained on milrinone infusion at discharge. Cardiac catheterization was recommended to assess response to milrinone and guide management of his low-output heart failure.

---

### Case 19 (divergence: 0.280)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    71   |
| Sentences |         4   |     5   |
| FK Grade  |        10.3 |    10.1 |

**Clinician**: At the hospital, a work up for chest pain showed her pain was unrelated to cardiovascular issues. The tests and procedures were normal, including an EKG, labs, CAT scan, stress test, and a more specific heart study. The doctors believe that anxiety is the cause of her symptoms, so she was started on anti-anxiety medications. She received Ativan in the hospital which improved her pain leading the doctors to believe anxiety was the cause.

**Model**: The patient was admitted for chest pain and underwent evaluation for a cardiac cause. Her workup included EKGs, cardiac blood tests, CT imaging, stress testing, and a MIBI study. All tests were normal and did not show heart problems, so cardiovascular disease was unlikely. Her chest pain improved with Ativan and Tylenol, so sertraline was started for anxiety. Overall, her current symptoms most likely relate to anxiety, not a heart condition.

---

### Case 16 (divergence: 0.276)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    72   |
| Sentences |         4   |     5   |
| FK Grade  |        11.6 |    12.8 |

**Clinician**: Patient's back pain is consistent with musculoskeletal pain related to muscle spasms. The doctors recommended weight loss as well as follow up with a physical therapist and pain clinic. The only other concern, is her abdominal pain, which the gastrointestinal team believe to be referred or radiating from the back pain she is having. While outpatient pain consult and integrative medicine consult were discussed with patient at discharge, no concerns for stroke were discussed.

**Model**: Because she had chronic abdominal pain with nausea and vomiting, gastrointestinal evaluation did not find a structural cause. She reported crampy bilateral mid-back pain that flared with and without abdominal pain. Because the mid-back pain resembled muscle spasm, it seemed consistent with musculoskeletal pain and was not necessarily related to her abdominal symptoms. She had back imaging, and physical therapy and pain clinic follow-up were recommended. No concern for stroke was documented.

---

### Case 1 (divergence: 0.269)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        78   |      75 |
| Sentences |         5   |       3 |
| FK Grade  |         9.3 |      11 |

**Clinician**: An endoscopic retrograde cholangiopancreatography, ERCP, was recommended to place a common bile duct stent. This stent was placed to allow drainage of the biliary obstruction which was caused by stones and sludge. Due to no improvement in liver function, the patient needed a repeat ERCP. The repeat ERCP showed that the biliary stent placed in the first ERCP was obstructed by stones and sludge. The stones and stent were successfully removed during this procedure by performing a sphincterotomy.

**Model**: The patient had biliary obstruction from stones and sludge, so ERCP treated this and placed a stent for drainage; frank pus drained from the duct. Despite this stent, liver tests and bilirubin rose, so he underwent repeat ERCP, and it showed the stent was acutely obstructed by sludge and stones. After his INR normalized, ERCP with sphincterotomy and removal of stones and the stent cleared the duct, and the retrograde cholangiogram showed no filling defects.

---

### Case 7 (divergence: 0.265)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    75   |
| Sentences |         4   |     5   |
| FK Grade  |         7.9 |     9.8 |

**Clinician**: The patient no longer needs to take her Coumadin for her deep vein thrombosis history. She had a filter placed to prevent clots from returning to her heart. This filter is called an IVC filter, and she received it due to her prolonged bed rest and risk of developing a clot. The patient will need to follow up with her doctor and get a repeat CT scan of her brain to evaluate the subarachnoid hemorrhage.

**Model**: The patient had a subarachnoid hemorrhage, so neurosurgery followed her throughout the hospitalization. She had a history of DVT and had taken chronic Coumadin before this injury. She received an IVC filter so the device served to prevent venous clots from reaching the heart. After the filter placement, the team discontinued Coumadin and instructed her not to continue it at this point. These instructions held systemic blood thinners in the setting of her subarachnoid hemorrhage.

---

### Case 11 (divergence: 0.254)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    73   |
| Sentences |         5   |     5   |
| FK Grade  |         9.8 |    13.7 |

**Clinician**: The patient was diagnosed with aseptic viral meningitis and completed treatment prior to discharge. It is expected that she may still have some symptoms when she is home resting based off the medications prescribed on discharge. She was prescribed PO dilaudid, tylenol, and advil as needed for pain. She was prescribed PO zofran for nausea management prn. With these medications prescribed, it appears that she will still experience pain and nausea during her recovery process.

**Model**: The patient had meningitis that was likely viral because bacterial, HSV, and Lyme causes were ruled out. It was concluded that she had aseptic meningitis. She initially received acyclovir, vancomycin, and ceftriaxone, and these were discontinued by discharge because aseptic meningitis was confirmed. She was discharged home with hydromorphone, acetaminophen, ibuprofen, and ondansetron prescribed as needed for pain and nausea during recovery. The plan described outpatient recovery with these symptomatic medications and follow-up.

---

### Case 8 (divergence: 0.246)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    75   |
| Sentences |         5   |     5   |
| FK Grade  |        11.1 |    16.1 |

**Clinician**: Patient has cirrhosis due to alcohol abuse. The long-term liver damage caused toxin buildup in the blood resulting in jaundice and kidney disease. Treatment of the toxin buildup with hydration and medications reduced her score for End-Stage Live Disease (MELD) and improved her creatinine and kidney function. Testing will determine if there may be longterm cognitive deficits related to alcohol abuse. She was diagnosed with a mania and suggested psychiatric treatment to control it.

**Model**: The patient had liver and kidney disease, which caused jaundice and fluid overload. She had cirrhosis, which meant long-term liver damage from alcohol. She received hydration, albumin, diuretics, and medications to reduce toxin buildup, which improved liver function, kidney injury, and respiratory distress. She experienced visual hallucinations, mania, and disorganized thoughts, and symptoms responded to Haldol so mental status normalized. Neuropsychological testing was recommended to evaluate possible long-term cognitive deficits from alcohol, including persistent confusion.

---

### Case 10 (divergence: 0.244)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    74   |
| Sentences |         5   |     6   |
| FK Grade  |        12.1 |    11.4 |

**Clinician**: The patient had a pulseless electrical activity arrest with subsequent anoxic brain injury. His mental status improved, though he had seizures and became impulsive with poor motor planning leading to falls. The patient may improve neurologically but he will likely have recurrent seizures. Additionally, the patient remains confused at times and requires assistance with ambulation. The brain damages this patient sustained after the heart attack will require intensive treatment in an anoxic brain injury unit.

**Model**: The patient sustained an anoxic brain injury after two PEA cardiac arrests. The initial EEG showed no brain activity and indicated severe injury. Over several days he was weaned from the ventilator and breathed independently as his mental status improved. At discharge he was alert and interactive, but he was sometimes confused. He had impaired motor planning, so he required assistance to walk. Neurology expected he had potential for neurologic improvement with intensive rehabilitation.

---

### Case 14 (divergence: 0.239)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        72   |    74   |
| Sentences |         5   |     5   |
| FK Grade  |         9.5 |    13.5 |

**Clinician**: The patient does not have any evidence of stomach cancer. She does see an oncologist for bladder cancer, though. The patient's lower left side pain was due to a partial bowel obstruction, blockage in her intestine. Her symptoms improved over time, but she needs to be very careful with becoming constipated as that can worsen her symptoms of an intestinal blockage. The doctors recommended that she take fiber supplements to prevent constipation.

**Model**: The patient was admitted with a partial small bowel obstruction, improved, and tolerated regular food at discharge. Discharge instructions focused on constipation management with fiber supplements and cautious use of an additional agent. He had bladder cancer as the only documented malignancy, so oncology follow up was arranged. The plan included gastroenterology follow up for intestinal evaluation, and this plan did not include a stomach cancer diagnosis. The documentation did not support stomach cancer.

---

### Case 3 (divergence: 0.234)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        72   |    73   |
| Sentences |         5   |     4   |
| FK Grade  |         9.2 |    12.4 |

**Clinician**: This patient should expect to have drowsiness, headaches, dizziness, irritability, and short-term memory loss with a head injury. These symptoms will decrease over the next few weeks. It is important to follow up with a specialist in traumatic brain injuries. The patient needs time to recover and needs to be aware of any new symptoms he has. He should report visual changes, weakness on one side of his body, and/or speech difficulty.

**Model**: The patient sustained a traumatic brain injury from a fall, and he did not require surgery. Because of this injury, his expected recovery includes drowsiness, headaches, dizziness, irritability, and short-term memory loss. These symptoms are normal effects of his head injury and typically decrease over the next several weeks, so he should be expected to improve. He should follow up with a specialist in traumatic brain injuries to guide recovery and monitor symptoms.

---

### Case 9 (divergence: 0.144)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    75   |
| Sentences |         6   |     5   |
| FK Grade  |        13.7 |    13.5 |

**Clinician**: Due to significant blood loss, elevated LFTs and creatinine, the patient received multiple blood transfusions and fluids requiring intubation and ICU management. She had end-stage organ dysfunction, abdominal compartment syndrome requiring surgery, and continuous dialysis for acute kidney injury. The cerebral edema was managed by neurosurgery. Low cortisol levels were treated with hydrocortisone. The abdomen was left open due to bleeding and then closed successfully. Due to liver failure, she was listed for liver transplantation.

**Model**: The patient underwent emergent C-section for fetal distress, which caused intraoperative blood loss. She was intubated, admitted to the ICU, and resuscitated with packed red cells, plasma, and saline. She developed abdominal compartment syndrome and coagulopathy, so she needed decompressive laparotomy, an open abdomen, and later abdominal closure. She had fulminant hepatic failure and acute kidney injury, and these were managed with liver-failure guidelines, transplant listing, and hemofiltration. Later problems from these treatments are unknown.

---
