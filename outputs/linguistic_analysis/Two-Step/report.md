# Linguistic Comparison Report: Model vs. Clinician

**Configuration**: Two-Step

## 1. Overview

- Cases analyzed: 20
- Features compared: 47
- Statistically significant differences (BH-adjusted p<0.05): 16 of 47

## 2. Full Feature Comparison

### Lexical Features

| Feature            |   Clinician |    Model |        Δ |      p |   p_adj | Sig   |       d |
|:-------------------|------------:|---------:|---------:|-------:|--------:|:------|--------:|
| avg_word_length    |      5.3852 |   6.0124 |  -0.6273 | 0.0000 |  0.0007 | ***   | -1.2304 |
| budget_utilization |      0.9800 |   0.9653 |   0.0147 | 0.1243 |  0.2216 | ns    |  0.3556 |
| hapax_legomena     |     44.0000 |  49.7000 |  -5.7000 | 0.0013 |  0.0053 | **    | -0.9430 |
| hapax_ratio        |      0.5995 |   0.6869 |  -0.0875 | 0.0001 |  0.0007 | ***   | -1.0709 |
| mtld               |     86.9815 | 106.6387 | -19.6573 | 0.0014 |  0.0053 | **    | -0.8896 |
| ttr                |      0.7559 |   0.8040 |  -0.0482 | 0.0010 |  0.0044 | **    | -0.9688 |
| unique_words       |     55.5000 |  58.2000 |  -2.7000 | 0.0120 |  0.0308 | *     | -0.6770 |
| word_count         |     73.5000 |  72.4000 |   1.1000 | 0.1229 |  0.2216 | ns    |  0.3556 |

### Syntactic Features

| Feature          |   Clinician |   Model |       Δ |        p |    p_adj | Sig   |       d |
|:-----------------|------------:|--------:|--------:|---------:|---------:|:------|--------:|
| adj_ratio        |      0.0820 |  0.1229 | -0.0409 |   0.0001 |   0.0007 | ***   | -1.1231 |
| adp_ratio        |      0.1094 |  0.1004 |  0.0090 |   0.3045 |   0.4994 | ns    |  0.2455 |
| adv_ratio        |      0.0235 |  0.0336 | -0.0101 |   0.0897 |   0.1901 | ns    | -0.3786 |
| avg_parse_depth  |      5.2992 |  5.1942 |  0.1050 |   0.7369 |   0.7950 | ns    |  0.0763 |
| avg_sent_length  |     17.9758 | 19.1050 | -1.1292 |   0.4665 |   0.6806 | ns    | -0.2303 |
| det_ratio        |      0.0851 |  0.0810 |  0.0041 |   0.7088 |   0.7854 | ns    |  0.1269 |
| noun_ratio       |      0.3105 |  0.3359 | -0.0254 |   0.0966 |   0.1901 | ns    | -0.3887 |
| opener_diversity |      0.9733 |  0.9600 |  0.0133 | nan      | nan      | n/a   |  0.0655 |
| pron_ratio       |      0.0632 |  0.0270 |  0.0363 |   0.0100 |   0.0273 | *     |  0.8255 |
| sent_length_std  |      6.5224 |  4.3450 |  2.1774 |   0.0037 |   0.0117 | *     |  0.7970 |
| sentence_count   |      4.7500 |  4.6000 |  0.1500 |   0.6833 |   0.7783 | ns    |  0.1269 |
| verb_ratio       |      0.1366 |  0.1302 |  0.0064 |   0.6742 |   0.7783 | ns    |  0.1642 |

### Readability

| Feature              |   Clinician |   Model |       Δ |      p |   p_adj | Sig   |       d |
|:---------------------|------------:|--------:|--------:|-------:|--------:|:------|--------:|
| coleman_liau         |     12.7828 | 16.2138 | -3.4311 | 0.0000 |  0.0007 | ***   | -1.1763 |
| flesch_kincaid_grade |     10.7161 | 13.2335 | -2.5174 | 0.0005 |  0.0025 | **    | -0.9922 |
| flesch_reading_ease  |     46.7490 | 28.8135 | 17.9356 | 0.0001 |  0.0007 | ***   |  1.1660 |

### Stylistic Features

| Feature                |   Clinician |   Model |       Δ |        p |    p_adj | Sig   |       d |
|:-----------------------|------------:|--------:|--------:|---------:|---------:|:------|--------:|
| adjective_pct          |      0.0820 |  0.1229 | -0.0409 |   0.0001 |   0.0007 | ***   | -1.1231 |
| adverb_pct             |      0.0235 |  0.0336 | -0.0101 |   0.0897 |   0.1901 | ns    | -0.3786 |
| first_person_pronouns  |      0.1500 |  0.0000 |  0.1500 | nan      | nan      | n/a   |  0.4094 |
| function_word_pct      |      0.4089 |  0.3341 |  0.0748 |   0.0002 |   0.0010 | ***   |  1.2286 |
| passive_voice_ratio    |      0.3917 |  0.2542 |  0.1375 |   0.0974 |   0.1901 | ns    |  0.3913 |
| second_person_pronouns |      0.0000 |  0.0000 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| the_patient_count      |      1.5500 |  1.4500 |  0.1000 |   0.5616 |   0.7207 | ns    |  0.0537 |
| third_person_pronouns  |      3.4500 |  1.4000 |  2.0500 |   0.0037 |   0.0117 | *     |  0.7931 |

### Sentiment & Tone

| Feature           |   Clinician |   Model |       Δ |      p |   p_adj | Sig   |       d |
|:------------------|------------:|--------:|--------:|-------:|--------:|:------|--------:|
| polarity          |      0.0282 |  0.0073 |  0.0208 | 0.4980 |  0.6806 | ns    |  0.1843 |
| reassurance_count |      0.6000 |  0.7000 | -0.1000 | 0.7812 |  0.8037 | ns    | -0.1269 |
| subjectivity      |      0.3804 |  0.3690 |  0.0114 | 0.7841 |  0.8037 | ns    |  0.0644 |
| warning_count     |      0.8500 |  0.8500 |  0.0000 | 0.4844 |  0.6806 | ns    |  0.0000 |

### Clinical Communication

| Feature                 |   Clinician |   Model |       Δ |        p |    p_adj | Sig   |       d |
|:------------------------|------------:|--------:|--------:|---------:|---------:|:------|--------:|
| causal_connectives      |      0.9000 |  0.5000 |  0.4000 |   0.2012 |   0.3437 | ns    |  0.3368 |
| certainty_markers       |      0.6000 |  0.4500 |  0.1500 |   0.4531 |   0.6806 | ns    |  0.2555 |
| contrastive_connectives |      0.2000 |  0.2000 |  0.0000 |   1.0000 |   1.0000 | ns    |  0.0000 |
| hedge_certainty_ratio   |      0.4583 |  0.4000 |  0.0583 |   0.5938 |   0.7377 | ns    |  0.1478 |
| hedge_epistemic         |      0.4500 |  0.3500 |  0.1000 |   0.5625 |   0.7207 | ns    |  0.1097 |
| hedge_evidential        |      0.0500 |  0.0500 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| medical_abbreviations   |      0.9500 |  1.7500 | -0.8000 |   0.0065 |   0.0191 | *     | -0.7240 |
| meta_referential        |      0.0000 |  0.0000 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| non_ascii               |      0.0000 |  0.0000 |  0.0000 | nan      | nan      | n/a   |  0.0000 |
| temporal_connectives    |      0.3500 |  0.9000 | -0.5500 |   0.0278 |   0.0671 | ns    | -0.5823 |
| total_connectives       |      1.4500 |  1.6000 | -0.1500 |   0.6700 |   0.7783 | ns    | -0.0938 |
| total_hedging           |      0.5000 |  0.4000 |  0.1000 |   0.4062 |   0.6406 | ns    |  0.0893 |

## 3. Variability Analysis

Variance ratio = clinician variance / model variance. >1 means clinician adapts more per case.

| Feature                      |   Clin Mean |   Clin Std |   Model Mean |   Model Std |   Var Ratio |
|:-----------------------------|------------:|-----------:|-------------:|------------:|------------:|
| sty_first_person_pronouns    |       0.150 |      0.366 |        0.000 |       0.000 |     inf     |
| sty_function_word_pct        |       0.409 |      0.065 |        0.334 |       0.036 |       3.358 |
| syn_pron_ratio               |       0.063 |      0.039 |        0.027 |       0.022 |       3.002 |
| syn_avg_parse_depth          |       5.299 |      1.181 |        5.194 |       0.693 |       2.900 |
| sty_third_person_pronouns    |       3.450 |      2.481 |        1.400 |       1.569 |       2.499 |
| read_coleman_liau            |      12.783 |      2.906 |       16.214 |       1.952 |       2.216 |
| lex_avg_word_length          |       5.385 |      0.539 |        6.012 |       0.379 |       2.025 |
| clin_causal_connectives      |       0.900 |      0.968 |        0.500 |       0.688 |       1.978 |
| sty_passive_voice_ratio      |       0.392 |      0.279 |        0.254 |       0.217 |       1.655 |
| lex_ttr                      |       0.756 |      0.046 |        0.804 |       0.036 |       1.641 |
| clin_certainty_markers       |       0.600 |      0.754 |        0.450 |       0.605 |       1.554 |
| read_flesch_kincaid_grade    |      10.716 |      2.001 |       13.233 |       1.616 |       1.533 |
| lex_hapax_ratio              |       0.599 |      0.072 |        0.687 |       0.060 |       1.463 |
| lex_hapax_legomena           |      44.000 |      4.984 |       49.700 |       4.131 |       1.456 |
| sty_the_patient_count        |       1.550 |      1.234 |        1.450 |       1.050 |       1.382 |
| read_flesch_reading_ease     |      46.749 |     13.467 |       28.813 |      11.526 |       1.365 |
| syn_det_ratio                |       0.085 |      0.032 |        0.081 |       0.028 |       1.340 |
| syn_adv_ratio                |       0.024 |      0.021 |        0.034 |       0.018 |       1.292 |
| sty_adverb_pct               |       0.024 |      0.021 |        0.034 |       0.018 |       1.292 |
| lex_word_count               |      73.500 |      2.373 |       72.400 |       2.088 |       1.292 |
| lex_budget_utilization       |       0.980 |      0.032 |        0.965 |       0.028 |       1.292 |
| sent_subjectivity            |       0.380 |      0.167 |        0.369 |       0.148 |       1.278 |
| syn_verb_ratio               |       0.137 |      0.032 |        0.130 |       0.029 |       1.216 |
| syn_sent_length_std          |       6.522 |      2.130 |        4.345 |       1.947 |       1.196 |
| clin_hedge_certainty_ratio   |       0.458 |      0.362 |        0.400 |       0.348 |       1.084 |
| syn_sentence_count           |       4.750 |      0.851 |        4.600 |       0.821 |       1.074 |
| syn_noun_ratio               |       0.310 |      0.051 |        0.336 |       0.049 |       1.055 |
| lex_unique_words             |      55.500 |      2.893 |       58.200 |       2.858 |       1.024 |
| clin_total_connectives       |       1.450 |      1.099 |        1.600 |       1.095 |       1.007 |
| clin_contrastive_connectives |       0.200 |      0.410 |        0.200 |       0.410 |       1.000 |
| clin_hedge_evidential        |       0.050 |      0.224 |        0.050 |       0.224 |       1.000 |
| sty_adjective_pct            |       0.082 |      0.042 |        0.123 |       0.045 |       0.850 |
| syn_adj_ratio                |       0.082 |      0.042 |        0.123 |       0.045 |       0.850 |
| sent_polarity                |       0.028 |      0.083 |        0.007 |       0.095 |       0.762 |
| clin_medical_abbreviations   |       0.950 |      1.191 |        1.750 |       1.372 |       0.754 |
| clin_hedge_epistemic         |       0.450 |      0.686 |        0.350 |       0.813 |       0.713 |
| syn_avg_sent_length          |      17.976 |      3.238 |       19.105 |       3.837 |       0.712 |
| syn_adp_ratio                |       0.109 |      0.022 |        0.100 |       0.026 |       0.683 |
| sent_reassurance_count       |       0.600 |      0.598 |        0.700 |       0.733 |       0.667 |
| sent_warning_count           |       0.850 |      1.268 |        0.850 |       1.631 |       0.604 |
| clin_total_hedging           |       0.500 |      0.761 |        0.400 |       0.995 |       0.585 |
| lex_mtld                     |      86.981 |     15.979 |      106.639 |      21.346 |       0.560 |
| clin_temporal_connectives    |       0.350 |      0.587 |        0.900 |       0.968 |       0.368 |
| syn_opener_diversity         |       0.973 |      0.085 |        0.960 |       0.179 |       0.225 |

Median variance ratio: 1.22

## Literature Comparison

Testing established AI-text findings in the clinical QA domain:

| Finding                              | Source                 | Expected                            | Observed                       | Confirmed   |
|:-------------------------------------|:-----------------------|:------------------------------------|:-------------------------------|:------------|
| Lower lexical diversity (TTR)        | All 5 papers           | model < clinician                   | clin=0.756, model=0.804 (**)   | No          |
| Fewer unique words                   | Stelmakh+, Culda+      | model < clinician                   | clin=55.500, model=58.200 (*)  | No          |
| More uniform sentence lengths        | All 5 papers           | model < clinician                   | clin=6.522, model=4.345 (*)    | Yes         |
| More nouns, fewer adjectives/adverbs | Tercon, Contrasting    | model < clinician                   | clin=0.082, model=0.123 (***)  | No          |
| Less passive voice                   | Culda et al.           | model < clinician                   | clin=0.392, model=0.254 (ns)   | Trend       |
| More readable (lower grade level)    | Culda+, Stelmakh+      | model < clinician                   | clin=10.716, model=13.233 (**) | No          |
| More positive sentiment              | Stelmakh+, Contrasting | model > clinician                   | clin=0.028, model=0.007 (ns)   | No          |
| Lower subjectivity                   | Stelmakh et al.        | model < clinician                   | clin=0.380, model=0.369 (ns)   | Trend       |
| Higher consistency (lower variance)  | Stelmakh et al.        | model variance < clinician variance | Median var ratio: 1.22         | Partially   |

## 5. Full Case Gallery

All paired cases with key per-case metrics.

### Case 13 (divergence: 0.457)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    73   |
| Sentences |         4   |     5   |
| FK Grade  |         9.8 |    13.2 |

**Clinician**: Doctors wanted the patient to stay in the hospital to further work up her leg issue. They informed her that she needed physical therapy evaluation and that she may be at risk for paralysis if she leaves the hospital. However, the patient still chose to leave against medical advice. Based on clinical knowledge, I would recommend the patient returns to the hospital right away if she is still in pain and cannot move her legs.

**Model**: The patient was admitted to neurology for leg numbness and weakness. Back MRI showed stable degenerative disc disease without spinal cord compromise. The team wanted her to remain hospitalized for further evaluation, including neck MRI and physical therapy assessment. They warned that leaving without this evaluation could cause permanent paralysis. Given persistent leg weakness and that paralysis risk, she should now obtain the previously recommended urgent inpatient assessment with spine imaging and therapy.

---

### Case 17 (divergence: 0.410)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    69   |
| Sentences |         4   |     5   |
| FK Grade  |        13.2 |    12.5 |

**Clinician**: Palpitations may occur if sleep apnea is untreated. Patient was diagnosed with hypercarbia due to severe sleep apnea and noncompliance with wearing a CPAP at night, which is worsening this patient's hypoventilation. Hypoventilation can lead to palpitations due to lack of oxygen in the blood. It is important that he keeps his appointments and continues to take his psychosis medications as prescribed, as noncompliance can lead to an increase in anxiety and schizophrenic episodes.

**Model**: The patient should keep all follow-up appointments with PCP, endocrinology, neurology, pulmonary, and ENT. The patient should take levothyroxine 150 mcg by mouth daily as prescribed. The patient should separate levothyroxine and calcium carbonate by at least four hours. The patient should obtain ordered TSH, calcium, magnesium, phosphate, albumin, and vitamin D labs before endocrinology follow-up. The patient should use prescribed auto-CPAP whenever sleeping to treat severe obstructive sleep apnea.

---

### Case 18 (divergence: 0.367)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    74   |
| Sentences |         5   |     4   |
| FK Grade  |         8.8 |    16.5 |

**Clinician**: Patient has a history of Crohn's Disease. This could cause diarrhea and vomiting if he is having a flare up of the disease. The patient was sent home on narcotics for pain, which can cause constipation; it was recommended he take a stool softener and increase his fluid and fiber intake. Severe constipation can cause diarrhea and vomiting. The patient should be evaluated by a doctor to rule out what is causing his symptoms.

**Model**: The patient was hospitalized after a motor vehicle collision with pulmonary contusion and neck strain. During hospitalization and at discharge the patient was alert, hemodynamically stable, and tolerated a regular diet without abdominal pain, nausea, or vomiting. Discharge instructions addressed deep breathing and prevention of narcotic-related constipation with stool softeners, fluid intake, and fiber. The available discharge instructions did not specify guidance about returning to the ER for new vomiting or diarrhea after discharge.

---

### Case 8 (divergence: 0.364)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    74   |
| Sentences |         5   |     5   |
| FK Grade  |        11.1 |    15.2 |

**Clinician**: Patient has cirrhosis due to alcohol abuse. The long-term liver damage caused toxin buildup in the blood resulting in jaundice and kidney disease. Treatment of the toxin buildup with hydration and medications reduced her score for End-Stage Live Disease (MELD) and improved her creatinine and kidney function. Testing will determine if there may be longterm cognitive deficits related to alcohol abuse. She was diagnosed with a mania and suggested psychiatric treatment to control it.

**Model**: The patient had liver failure with ascites and edema and was determined to have cirrhosis, long-term liver damage from alcohol. Kidney dysfunction with elevated creatinine and toxin buildup improved with hydration, toxin-reducing medications, and diuretics. Respiratory distress with pulmonary edema resolved with IV diuresis during an ICU stay. Recovery of kidney function and breathing showed that toxic effects were reversible, not persistent poisoning. Persistent confusion would more likely reflect alcohol-related cognitive or psychiatric effects.

---

### Case 15 (divergence: 0.345)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        66   |    72   |
| Sentences |         5   |     4   |
| FK Grade  |         8.7 |    14.7 |

**Clinician**: The patient was prescribed Bactrim and Levofloxacin for treatment of his skin infection, as well as antivirals for prophylaxis for possible HIV infection. From my clinical knowledge, it is possible that these antibiotics have caused a decrease in sperm count and/or sperm movement. This should not be a long term issue. Once antibiotics are completed, this issue should resolve. He should not be concerned for infertility.

**Model**: The available documentation described a likely skin infection on the surface of the penis associated with penile and scrotal swelling. The treatment plan targeted this superficial infection with oral Bactrim and levofloxacin and advised close follow-up to confirm eradication. Additional management included a 2-week course of HIV post-exposure prophylaxis for possible HIV infection. From this record alone, only a penile skin infection is evident, so it does not establish spread or infertility.

---

### Case 2 (divergence: 0.342)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        73   |    74   |
| Sentences |         3   |     4   |
| FK Grade  |        13.6 |    12.5 |

**Clinician**: The patient was given Lasix for acute diastolic heart failure with symptoms including shortness of breath and lower extremity edema. The patient was given 8 liters of fluid to help maintain his blood pressure which contributed to his respiratory failure. After the patient's heart failure was treated with Lasix, he showed improvement in shortness of breath and his oxygen requirement, and he only needed to remain on a small amount of oxygen for comfort.

**Model**: The patient developed acute diastolic heart failure with volume overload, shortness of breath, and leg edema. He received 8 liters of fluid to support blood pressure, which worsened hypoxemic respiratory failure. He was treated with IV Lasix, intermittent Lasix infusion, and then oral torsemide to remove excess fluid and treat the volume overload. After diuresis, his symptoms and oxygenation improved, so he needed a small amount of supplemental oxygen for comfort instead of higher flows.

---

### Case 11 (divergence: 0.336)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    73   |
| Sentences |         5   |     5   |
| FK Grade  |         9.8 |    13.5 |

**Clinician**: The patient was diagnosed with aseptic viral meningitis and completed treatment prior to discharge. It is expected that she may still have some symptoms when she is home resting based off the medications prescribed on discharge. She was prescribed PO dilaudid, tylenol, and advil as needed for pain. She was prescribed PO zofran for nausea management prn. With these medications prescribed, it appears that she will still experience pain and nausea during her recovery process.

**Model**: The patient had meningitis that was most consistent with a viral cause. CSF and blood testing ruled out bacterial, HSV, and Lyme meningitis. Encephalitis was considered unlikely because the patient maintained a normal mental status. The patient initially received IV vancomycin, ceftriaxone, and acyclovir, which were discontinued once aseptic meningitis was confirmed. Her recovery plan consisted of pain control in the hospital and discharge on oral hydromorphone, acetaminophen, ibuprofen, and ondansetron as needed.

---

### Case 20 (divergence: 0.319)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    72   |
| Sentences |         6   |     6   |
| FK Grade  |         9.9 |    13.5 |

**Clinician**: Neurology doctors completed a series of tests and procedures to determine the cause of headaches. They ruled out elevated intracranial pressure and blood clots. Verapamil was started once daily to prevent headaches. Based on clinical knowledge, spinning sensation with a migraine is vertigo caused by the migraine. A migraine with aura can also cause dizziness. To achieve optimal control of migraines, patient was recommended to avoid caffeine and keep a regular sleep wake cycle.

**Model**: The neurology ward evaluated the patient for headaches of unusual quality. The evaluation included CT, MRI, laboratory tests, lumbar puncture, and MR venogram. These studies ruled out serious intracranial causes, including pseudotumor cerebri and cerebral venous thrombosis. After excluding these conditions, the team managed the headaches as migraine. The patient was started on verapamil daily as preventive headache therapy. Discharge instructions addressed optimal control of migraines with caffeine avoidance and regular sleep.

---

### Case 16 (divergence: 0.318)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    74   |
| Sentences |         4   |     5   |
| FK Grade  |        11.6 |    10.6 |

**Clinician**: Patient's back pain is consistent with musculoskeletal pain related to muscle spasms. The doctors recommended weight loss as well as follow up with a physical therapist and pain clinic. The only other concern, is her abdominal pain, which the gastrointestinal team believe to be referred or radiating from the back pain she is having. While outpatient pain consult and integrative medicine consult were discussed with patient at discharge, no concerns for stroke were discussed.

**Model**: The patient had two distinct types of back pain, including upper back pain possibly related to abdominal pain. The care team considered her abdominal pain possibly referred or radiating from the spine. She also had crampy bilateral mid-back pain that seemed more consistent with muscle spasm and possible musculoskeletal pain. Her management included massaging her back at home, flexeril, a lidocaine patch, and recommendations for weight loss. Overall, findings did not suggest a stroke.

---

### Case 1 (divergence: 0.297)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        78   |    72   |
| Sentences |         5   |     5   |
| FK Grade  |         9.3 |    10.8 |

**Clinician**: An endoscopic retrograde cholangiopancreatography, ERCP, was recommended to place a common bile duct stent. This stent was placed to allow drainage of the biliary obstruction which was caused by stones and sludge. Due to no improvement in liver function, the patient needed a repeat ERCP. The repeat ERCP showed that the biliary stent placed in the first ERCP was obstructed by stones and sludge. The stones and stent were successfully removed during this procedure by performing a sphincterotomy.

**Model**: The patient had biliary obstruction from duct stones and sludge, which ERCP treated by placing a stent to allow drainage. Frank pus drained from the bile duct, so the obstruction was associated with active infection requiring IV antibiotics. Worsening LFTs and bilirubin despite treatment prompted ERCP. The biliary stent was acutely re-obstructed by sludge and stones. With normalized INR, ERCP allowed sphincterotomy and stone extraction, directly relieving the obstructing source of infection.

---

### Case 3 (divergence: 0.289)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        72   |    74   |
| Sentences |         5   |     5   |
| FK Grade  |         9.2 |    13.6 |

**Clinician**: This patient should expect to have drowsiness, headaches, dizziness, irritability, and short-term memory loss with a head injury. These symptoms will decrease over the next few weeks. It is important to follow up with a specialist in traumatic brain injuries. The patient needs time to recover and needs to be aware of any new symptoms he has. He should report visual changes, weakness on one side of his body, and/or speech difficulty.

**Model**: The patient sustained a traumatic brain injury from a fall that did not require surgery. After discharge, the expected course includes drowsiness, headaches, dizziness, irritability, and short-term memory loss. These post-concussive symptoms are considered normal for this injury and should gradually decrease over several weeks. The patient should follow up with the traumatic brain injury specialist for ongoing care. Recovery is expected to be favorable but requires monitoring for new neurologic or respiratory symptoms.

---

### Case 12 (divergence: 0.285)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        73   |    71   |
| Sentences |         4   |     3   |
| FK Grade  |        11.1 |    13.3 |

**Clinician**: The patient's chest pain is not a cardiac related issue based off her EKG and cardiac labs. Her stomach pain was able to be controlled with anti-nausea medication and insulin, and she received nitroglycerin for her chest pain. From my clinical knowledge, it is possible that this stomach pain is due to uncontrolled diabetes because she needed insulin in the emergency department. The patient will follow up with her PCP for abdominal pain.

**Model**: The patient had abdominal and chest pain, but EKG and cardiac markers did not show heart problems or blockages, making a cardiac cause of her pain unlikely. Hospital tests were reassuring that her chest pain was not caused by heart vessel disease, so the pain most likely arose from a non-cardiac source. Her abdominal pain improved with anti-nausea medicine and insulin, and outpatient follow-up was advised to address ongoing abdominal pain.

---

### Case 5 (divergence: 0.280)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    75   |
| Sentences |         6   |     4   |
| FK Grade  |         8.2 |    13.6 |

**Clinician**: The chest pain was musculoskeletal, not overdose or cardiac related. On exam the patient reported more pain with movement and pain with palpation. An EKG showed no ischemia and blood tests confirmed that the patient did not have a heart attack. A transthoracic echocardiogram (TTE) of the patient's heart was performed to rule out cardiac events. TTE results were normal. The patient was monitored on telemetry which did not show any significant cardiac events.

**Model**: During hospitalization the patient reported chest pain that appeared musculoskeletal in origin because it was reproducible with palpation and worsened with movement. EKGs, serial troponins, and a TTE showed no ischemia, no heart attack, and normal heart function. Telemetry showed no significant arrhythmias, and CK levels fell without treatment, limiting concern for heart damage. The ongoing similar chest pain is therefore most consistent with musculoskeletal chest wall pain, not lasting cardiac injury from the overdose.

---

### Case 10 (divergence: 0.274)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    70   |
| Sentences |         5   |     5   |
| FK Grade  |        12.1 |    13.8 |

**Clinician**: The patient had a pulseless electrical activity arrest with subsequent anoxic brain injury. His mental status improved, though he had seizures and became impulsive with poor motor planning leading to falls. The patient may improve neurologically but he will likely have recurrent seizures. Additionally, the patient remains confused at times and requires assistance with ambulation. The brain damages this patient sustained after the heart attack will require intensive treatment in an anoxic brain injury unit.

**Model**: The patient sustained an anoxic brain injury after PEA cardiac arrests associated with asthma. Initial EEG showed no evident brain activity and he remained comatose with a guarded prognosis. Over days he improved to alert, oriented, and moving all extremities. He developed seizures from hypoxic brain injury requiring ongoing antiepileptic therapy. At discharge he was alert but intermittently confused with poor motor planning, needing rehabilitation and assistance for safe ambulation.

---

### Case 14 (divergence: 0.251)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        72   |    71   |
| Sentences |         5   |     4   |
| FK Grade  |         9.5 |    14.4 |

**Clinician**: The patient does not have any evidence of stomach cancer. She does see an oncologist for bladder cancer, though. The patient's lower left side pain was due to a partial bowel obstruction, blockage in her intestine. Her symptoms improved over time, but she needs to be very careful with becoming constipated as that can worsen her symptoms of an intestinal blockage. The doctors recommended that she take fiber supplements to prevent constipation.

**Model**: The patient was admitted with a partial small bowel obstruction. The small bowel obstruction improved over time, and he tolerated regular food before discharge. Constipation management focused on fiber supplements such as Metamucil, given his difficulty tolerating stool softeners and tendency toward diarrhea. Oncology follow-up was arranged solely for further treatment of bladder cancer, and the care plan did not identify or treat any malignancy of the stomach during this admission.

---

### Case 6 (divergence: 0.237)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        73   |    67   |
| Sentences |         6   |     5   |
| FK Grade  |        11.5 |    14.1 |

**Clinician**: Preliminary tests showed Candida infection in the blood. The sputum test revealed yeast along with gram positive cocci and gram negative rods. Lung infection was treated with antibiotics (vancomcyin, linezolid, amikacin, ambisome, tobramycin). The antibiotics did not improve the patient's condition as shown by worsening chest x-ray, white blood cell count, and respiratory distress. After discussions with family and physicians, medical treatment was gradually reduced to comfort measures only. The patient died peacefully.

**Model**: The patient developed pneumonia with productive cough, somnolence, and left lower lobe consolidation. Based on this presentation, he was initially started on vancomycin and another antibiotic on 9-30. The initial sputum gram stain demonstrated gram positive cocci, gram negative rods, and yeast. A blood fungal culture subsequently grew Torulopsis glabrata, indicating a systemic fungal infection. After these microbiologic findings, antifungal agents micafungin on 10-3 and ambisome on 10-8 were added.

---

### Case 19 (divergence: 0.229)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        74   |    74   |
| Sentences |         4   |     4   |
| FK Grade  |        10.3 |    11.2 |

**Clinician**: At the hospital, a work up for chest pain showed her pain was unrelated to cardiovascular issues. The tests and procedures were normal, including an EKG, labs, CAT scan, stress test, and a more specific heart study. The doctors believe that anxiety is the cause of her symptoms, so she was started on anti-anxiety medications. She received Ativan in the hospital which improved her pain leading the doctors to believe anxiety was the cause.

**Model**: The patient was admitted for chest pain to rule out a heart-related cause. A thorough cardiac workup including EKGs, cardiac blood tests, and CT imaging was normal, making acute heart disease very unlikely. A stress test and MIBI heart study also showed no heart problems, further decreasing the likelihood that the chest pain was cardiac. Improvement with Ativan and starting sertraline specifically to treat anxiety supported anxiety as the main cause of her symptoms.

---

### Case 7 (divergence: 0.219)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    75   |
| Sentences |         4   |     6   |
| FK Grade  |         7.9 |     9.9 |

**Clinician**: The patient no longer needs to take her Coumadin for her deep vein thrombosis history. She had a filter placed to prevent clots from returning to her heart. This filter is called an IVC filter, and she received it due to her prolonged bed rest and risk of developing a clot. The patient will need to follow up with her doctor and get a repeat CT scan of her brain to evaluate the subarachnoid hemorrhage.

**Model**: The patient had a subarachnoid hemorrhage that neurosurgery followed throughout the hospitalization. The patient previously received Coumadin for a history of DVT. An IVC filter was placed because prolonged bedrest increased the risk of blood clots returning to the heart. After filter placement, Coumadin was discontinued and not resumed at discharge. The discharge instruction about blood thinners was that the IVC filter would now provide clot protection instead of Coumadin. Neurosurgery arranged follow-up for hemorrhage.

---

### Case 9 (divergence: 0.187)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        75   |    71   |
| Sentences |         6   |     3   |
| FK Grade  |        13.7 |    13.5 |

**Clinician**: Due to significant blood loss, elevated LFTs and creatinine, the patient received multiple blood transfusions and fluids requiring intubation and ICU management. She had end-stage organ dysfunction, abdominal compartment syndrome requiring surgery, and continuous dialysis for acute kidney injury. The cerebral edema was managed by neurosurgery. Low cortisol levels were treated with hydrocortisone. The abdomen was left open due to bleeding and then closed successfully. Due to liver failure, she was listed for liver transplantation.

**Model**: The patient underwent an emergent C-section for fetal distress that was complicated by 1.7 liters of blood loss. She was resuscitated with red blood cells, plasma, and 4 liters of saline, was intubated, and was admitted to the ICU. She developed abdominal compartment syndrome with ongoing bleeding and fulminant hepatic failure, requiring emergent decompressive laparotomy with temporary open abdomen and later closure, and the note did not describe later problems from these treatments.

---

### Case 4 (divergence: 0.186)

| Metric    |   Clinician |   Model |
|:----------|------------:|--------:|
| Words     |        70   |    73   |
| Sentences |         4   |     5   |
| FK Grade  |        15.1 |    14.1 |

**Clinician**: The patient was recommended a cardiac catheterization for worsening heart failure confirmed by left ventricle ejection fraction of 25% on his echocardiogram. He had low output heart failure which caused increasing intra-abdominal pressure resulting in congestive hepatopathy, abdominal pain, and right upper quadrant abdominal tenderness. The cardiac catheterization showed the patient needed milrinone for treatment. Milrinone infusion improved the patient's heart pump function by significantly improving cardiac output and wedge pressure.

**Model**: The patient had idiopathic dilated cardiomyopathy with LVEF 25 percent and acute-on-chronic low-output heart failure causing syncope. He was admitted with worsening low-output heart failure. He therefore underwent right heart catheterization specifically for a milrinone trial in this low-output state. Catheterization showed high wedge pressure and low cardiac index that improved markedly with milrinone, indicating therapeutic benefit. Cardiac catheterization was recommended to demonstrate milrinone effectiveness and guide management of his severe systolic heart failure.

---
