"""
Project  : Prevalence and Associated Factors of Depression Among Type 1 Diabetes Patients Attending Atbra Teaching Hospital, Nahr Al-Nil State, Sudan – 2025
Script   : Data Cleaning & Recoding
Author   : Abdulrahman Sirelkhatim
Date     : October 2025
Input    : 1_data/raw/raw_data.xlsx  (sheet: "Form Responses 1")
Output   : 1_data/cleaned/cleaned_data.xlsx
"""

import pandas as pd

RAW_PATH = "1_data/raw/raw_data.xlsx"
OUTPUT_PATH = "1_data/cleaned/cleaned_data.xlsx"
SHEET = "Form Responses 1"

variable_map = {
    "Age": "AGE",
    "Gender": "GENDER",
    "Marital Status:": "MARITAL",
    "Educational Level:": "EDUCATN",
    "Employment Status:": "EMPLOY",
    "Duration ince diagnoi with Diabete:": "DIAB_DUR",
    "Type of current Diabetes Treatment:": "TREATMNT",
    "How often do you follow your prescribed medication regimen?": "MED_ADHR",
    "How often do you monitor your blood sugar?": "BS_MONIT",
    "When was your last HbA1c test?": "LAST_A1C",
    "How would you describe your current glycemic control?": "GLY_CTRL",
    "How often do you visit a doctor for diabetes check-ups?": "DOC_VISIT",
    "Have you experienced any diabetes-related complications? (You can choose more than one)": "COMP_STR",
    "Depressed Mood (feelings of sadness, hopelessness, helplessness, worthlessness)": "HDRS1_STR",
    "Feelings of Guilt (self-blame, feelings of letting others down)": "HDRS2_STR",
    "Suicidal Thoughts (thoughts of death or suicide)": "HDRS3_STR",
    "Insomnia [Insomnia - Early (difficulty falling asleep)]": "HDRS4_STR",
    "Insomnia [Insomnia - Middle (waking during the night)]": "HDRS5_STR",
    "Insomnia [Insomnia - Late (early morning waking)]": "HDRS6_STR",
    "Work and Activities (loss of interest in work or hobbies)": "HDRS7_STR",
    "[Psychomotor Retardation (slowed speech or movements)]": "HDRS8_STR",
    "[Psychomotor Agitation (restlessness)]": "HDRS9_STR",
    "Anxiety - Psychic (mental worrying, tension)": "HDRS10_STR",
    "[Anxiety - Somatic (physical anxiety symptoms like palpitations)]": "HDRS11_STR",
    "[Gastrointestinal Symptoms (nausea, diarrhea, constipation)]": "HDRS12_STR",
    "[Somatic Symptoms - General (body aches, weakness)]": "HDRS13_STR",
    "[Genital Symptoms (decreased libido, menstrual changes)]": "HDRS14_STR",
    "[Hypochondriasis (worry about health)]": "HDRS15_STR",
    "Weight Loss (recent weight loss)": "HDRS16_STR",
    "Insight (understanding of illness)": "HDRS17_STR",
}

complication_map = {
    "Diabetic neuropathy (nerve damage)": "COMP_NEUR",
    "Diabetic nephropathy (kidney disease)": "COMP_NEPH",
    "Diabetic retinopathy (eye disease)": "COMP_RET",
    "Diabetic foot ulcers": "COMP_FOOT",
    "Cardiovascular disease (heart problems)": "COMP_CVD",
    "Option 6": "COMP_NONE",
}

# HDRS items encode their numeric score in the response string (e.g. "2= Moderate")
hdrs_str_cols = [f"HDRS{i}_STR" for i in range(1, 18)]


def extract_hdrs_score(cell):
    """Extract leading integer from HDRS response string."""
    try:
        return int(str(cell).strip()[0])
    except (ValueError, IndexError):
        return pd.NA


df = pd.read_excel(RAW_PATH, sheet_name=SHEET)
df.rename(columns=variable_map, inplace=True)

# Binary complication indicators
comp_col = df["COMP_STR"].astype(str)
for comp_text, col_name in complication_map.items():
    df[col_name] = comp_col.str.contains(
        comp_text, case=False, na=False, regex=False
    ).astype(int)

# Numeric HDRS item scores
for col in hdrs_str_cols:
    num_col = col.replace("_STR", "_NUM")
    df[num_col] = df[col].apply(extract_hdrs_score).astype("Int64")

# Composite HDRS total score
hdrs_num_cols = [c.replace("_STR", "_NUM") for c in hdrs_str_cols]
df["HDRS_TOTAL"] = df[hdrs_num_cols].sum(axis=1, skipna=True)

# Binary depression status (HDRS > 7 = depressed)
df["DEPRESSION_STATUS"] = (df["HDRS_TOTAL"] > 7).astype(int)


# Ordinal depression severity
def hdrs_severity(score):
    if pd.isna(score):
        return pd.NA
    if score <= 7:
        return "No Depression"
    if score <= 16:
        return "Mild"
    if score <= 24:
        return "Moderate"
    return "Severe"


df["DEPRESSION_LEVEL"] = df["HDRS_TOTAL"].apply(hdrs_severity)


# Age groups
def age_group(age):
    if pd.isna(age):
        return pd.NA
    if age < 20:
        return "Under 20"
    if age <= 39:
        return "20-39"
    return "40 and Over"


df["AGE_GROUP"] = df["AGE"].apply(age_group)


# Diabetes duration groups
def dur_group(dur):
    if pd.isna(dur):
        return pd.NA
    if dur <= 5:
        return "0-5 Years"
    if dur <= 15:
        return "6-15 Years"
    return "Over 15 Years"


df["DURATION_GROUP"] = df["DIAB_DUR"].apply(dur_group)

# Any complication flag
df["ANY_COMPLICATION"] = (
    df[["COMP_NEUR", "COMP_NEPH", "COMP_RET", "COMP_FOOT", "COMP_CVD"]].sum(axis=1) > 0
).astype(int)

df.to_excel(OUTPUT_PATH, index=False)
print(f"Saved: {OUTPUT_PATH}")
print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"Depression prevalence: {df['DEPRESSION_STATUS'].mean() * 100:.1f}%")
