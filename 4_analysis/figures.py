""" "
Project  : Prevalence and Associated Factors of Depression Among Type 1 Diabetes Patients Attending Atbra Teaching Hospital, Nahr Al-Nil State, Sudan – 2025
Script   : Figure Generation (all figures)
Author   : Abdulrahman Sirelkhatim
Date     : October 2025
Input    : 1_data/cleaned/cleaned_data.xlsx
Output   : 5_figures/ directory (PNG, 300 DPI)

Figures produced:
fig01_gender_distribution.png
fig02_marital_status_distribution.png
fig03_education_distribution.png
fig04_employment_distribution.png
fig05_treatment_type.png
fig06_medication_adherence.png
fig07_blood_sugar_monitoring.png
fig08_complications_prevalence.png
fig09_depression_severity_distribution.png
fig10_glycemic_control_distribution.png
fig11_depression_by_glycemic_control.png
fig12_hdrs_by_age_group.png
fig13_hdrs_by_diabetes_duration.png
fig14_depression_predictors_forest_plot.png
fig15_correlation_heatmap.png
"""

import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

DATA_PATH = "1_data/cleaned/cleaned_data.xlsx"
FIGURES_DIR = "5_figures/"

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 11
plt.rcParams["figure.dpi"] = 200

PALETTE = sns.color_palette("Set2")
BLUE = sns.color_palette("Blues_r", 5)
SEVERITY = sns.color_palette("YlOrRd_r", 4)
CONTRAST = [sns.color_palette("Blues")[4], sns.color_palette("YlOrRd")[3]]

HDRS_NUM_COLS = [f"HDRS{i}_NUM" for i in range(1, 18)]


def save_fig(fig, filename):
    fig.savefig(FIGURES_DIR + filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {filename}")


# --- Load and prepare data ---
df = pd.read_excel(DATA_PATH)
n = len(df)

for col in HDRS_NUM_COLS:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

if "HDRS_TOTAL" not in df.columns:
    df["HDRS_TOTAL"] = df[[c for c in HDRS_NUM_COLS if c in df.columns]].sum(
        axis=1, skipna=True
    )

if "DEPRESSION_STATUS" not in df.columns:
    df["DEPRESSION_STATUS"] = (df["HDRS_TOTAL"] > 7).astype(int)

if "DEPRESSION_LEVEL" not in df.columns:

    def hdrs_severity(s):
        if pd.isna(s):
            return pd.NA
        if s <= 7:
            return "No Depression"
        if s <= 16:
            return "Mild"
        if s <= 24:
            return "Moderate"
        return "Severe"

    df["DEPRESSION_LEVEL"] = df["HDRS_TOTAL"].apply(hdrs_severity)

if "AGE_GROUP" not in df.columns:
    df["AGE_GROUP"] = pd.cut(
        df["AGE"], bins=[0, 19, 39, 100], labels=["Under 20", "20-39", "40 and Over"]
    )

if "DURATION_GROUP" not in df.columns:
    df["DURATION_GROUP"] = pd.cut(
        df["DIAB_DUR"],
        bins=[0, 5, 15, 100],
        labels=["0-5 Years", "6-15 Years", "Over 15 Years"],
    )


# --- Helper: donut pie chart ---
def donut_pie(ax, counts, title):
    ax.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=PALETTE,
        wedgeprops={"width": 0.6, "edgecolor": "white"},
        pctdistance=0.7,
        labeldistance=1.05,
    )
    ax.set_title(title, pad=12)


# --- Figures 1–4: Demographic distributions ---
demo_configs = [
    ("GENDER", "fig01_gender_distribution.png", "Gender Distribution"),
    ("MARITAL", "fig02_marital_status_distribution.png", "Marital Status Distribution"),
    ("EDUCATN", "fig03_education_distribution.png", "Educational Level Distribution"),
    ("EMPLOY", "fig04_employment_distribution.png", "Employment Status Distribution"),
]
for col, filename, title in demo_configs:
    fig, ax = plt.subplots(figsize=(5, 5))
    counts = df[col].value_counts()
    donut_pie(ax, counts, f"{title} (N={n})")
    save_fig(fig, filename)


# --- Figure 5: Treatment type ---
fig, ax = plt.subplots(figsize=(6, 4))
counts = df["TREATMNT"].value_counts()
sns.barplot(
    x=counts.index, y=counts.values / n * 100, palette=BLUE[: len(counts)], ax=ax
)
for i, v in enumerate(counts.values / n * 100):
    ax.text(i, v + 0.5, f"{v:.1f}%", ha="center", fontsize=9)
ax.set_ylabel("Percentage (%)")
ax.set_xlabel("Treatment Type")
ax.set_title(f"Type of Diabetes Treatment (N={n})")
ax.set_ylim(0, 100)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
save_fig(fig, "fig05_treatment_type.png")


# --- Figure 6: Medication adherence ---
adhr_order = ["Always", "Most of the time", "Sometimes", "Rarely", "Never"]
fig, ax = plt.subplots(figsize=(7, 4))
counts = df["MED_ADHR"].value_counts().reindex(adhr_order).dropna()
sns.barplot(
    x=counts.index, y=counts.values / n * 100, palette=BLUE[: len(counts)], ax=ax
)
for i, v in enumerate(counts.values / n * 100):
    ax.text(i, v + 0.5, f"{v:.1f}%", ha="center", fontsize=9)
ax.set_ylabel("Percentage (%)")
ax.set_xlabel("Adherence Level")
ax.set_title(f"Medication Adherence (N={n})")
ax.set_ylim(0, 75)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
save_fig(fig, "fig06_medication_adherence.png")


# --- Figure 7: Blood sugar monitoring frequency ---
monit_order = ["Daily", "Several times a week", "Once a week", "Rarely", "Never"]
fig, ax = plt.subplots(figsize=(7, 4))
counts = df["BS_MONIT"].value_counts().reindex(monit_order).dropna()
pcts = counts.values / n * 100
bars = ax.barh(counts.index[::-1], pcts[::-1], color=BLUE[0])
for bar in bars:
    w = bar.get_width()
    ax.text(
        w + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{w:.1f}%",
        va="center",
        fontsize=9,
    )
ax.set_xlabel("Percentage (%)")
ax.set_title(f"Blood Sugar Monitoring Frequency (N={n})")
ax.set_xlim(0, 55)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
save_fig(fig, "fig07_blood_sugar_monitoring.png")


# --- Figure 8: Complications prevalence ---
comp_map = {
    "COMP_FOOT": "Foot Ulcers",
    "COMP_RET": "Retinopathy",
    "COMP_NEUR": "Neuropathy",
    "COMP_NEPH": "Nephropathy",
    "COMP_CVD": "CVD",
}
comp_pcts = {label: df[col].mean() * 100 for col, label in comp_map.items()}
comp_pcts = dict(sorted(comp_pcts.items(), key=lambda x: x[1]))

fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.barh(list(comp_pcts.keys()), list(comp_pcts.values()), color=BLUE[0])
for bar in bars:
    w = bar.get_width()
    ax.text(
        w + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{w:.1f}%",
        va="center",
        fontsize=9,
    )
ax.set_xlabel("Prevalence (%)")
ax.set_title(f"Prevalence of Diabetes-Related Complications (N={n})")
ax.set_xlim(0, 50)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
save_fig(fig, "fig08_complications_prevalence.png")


# --- Figure 9: Depression severity distribution (donut) ---
sev_order = ["No Depression", "Mild", "Moderate", "Severe"]
fig, ax = plt.subplots(figsize=(5, 5))
counts = df["DEPRESSION_LEVEL"].value_counts().reindex(sev_order).dropna()
ax.pie(
    counts,
    labels=counts.index,
    autopct="%1.1f%%",
    colors=SEVERITY,
    wedgeprops={"width": 0.6, "edgecolor": "white"},
    pctdistance=0.7,
    labeldistance=1.05,
)
ax.set_title(f"Depression Severity Distribution (N={n})\nCronbach's α = 0.913")
save_fig(fig, "fig09_depression_severity_distribution.png")


# --- Figure 10: Glycemic control distribution ---
fig, ax = plt.subplots(figsize=(5, 5))
counts = df["GLY_CTRL"].value_counts()
donut_pie(ax, counts, f"Glycemic Control Distribution (N={n})")
save_fig(fig, "fig10_glycemic_control_distribution.png")


# --- Figure 11: Depression prevalence by glycemic control ---
fig, ax = plt.subplots(figsize=(6, 4))
dep_by_ctrl = (
    (df.groupby("GLY_CTRL")["DEPRESSION_STATUS"].mean() * 100)
    .reindex(["Good", "Not sure", "Poor"])
    .dropna()
)
bars = ax.bar(dep_by_ctrl.index, dep_by_ctrl.values, color=CONTRAST)
for bar in bars:
    h = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2, h + 1, f"{h:.1f}%", ha="center", fontsize=9
    )
ax.set_ylabel("Depression Prevalence (%)")
ax.set_xlabel("Glycemic Control")
ax.set_title("Depression Prevalence by Glycemic Control (p<0.001)")
ax.set_ylim(0, 110)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
save_fig(fig, "fig11_depression_by_glycemic_control.png")


# --- Figure 12: Mean HDRS by age group ---
age_order = ["Under 20", "20-39", "40 and Over"]
fig, ax = plt.subplots(figsize=(6, 4))
means = df.groupby("AGE_GROUP")["HDRS_TOTAL"].mean().reindex(age_order).dropna()
sds = df.groupby("AGE_GROUP")["HDRS_TOTAL"].std().reindex(age_order).dropna()
bars = ax.bar(
    means.index,
    means.values,
    yerr=sds.values,
    capsize=5,
    color=sns.color_palette("Purples_r", 3),
)
for bar, v in zip(bars, means.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        v + 1,
        f"{v:.2f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )
ax.set_ylabel("Mean HDRS Total Score")
ax.set_xlabel("Age Group")
ax.set_title("Mean HDRS Score by Age Group (F(2,245)=10.19, p<0.001)")
ax.set_ylim(0, 28)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
save_fig(fig, "fig12_hdrs_by_age_group.png")


# --- Figure 13: Mean HDRS by diabetes duration group ---
dur_order = ["0-5 Years", "6-15 Years", "Over 15 Years"]
fig, ax = plt.subplots(figsize=(6, 4))
means = df.groupby("DURATION_GROUP")["HDRS_TOTAL"].mean().reindex(dur_order).dropna()
sds = df.groupby("DURATION_GROUP")["HDRS_TOTAL"].std().reindex(dur_order).dropna()
bars = ax.bar(
    means.index,
    means.values,
    yerr=sds.values,
    capsize=5,
    color=sns.color_palette("Purples_r", 3),
)
for bar, v in zip(bars, means.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        v + 1,
        f"{v:.2f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )
ax.set_ylabel("Mean HDRS Total Score")
ax.set_xlabel("Diabetes Duration Group")
ax.set_title("Mean HDRS Score by Diabetes Duration (F(2,245)=11.67, p<0.001)")
ax.set_ylim(0, 28)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
save_fig(fig, "fig13_hdrs_by_diabetes_duration.png")


# --- Figure 14: Forest plot — independent predictors of depression diagnosis ---
# OR and 95% CI from binary logistic regression (Table 13 in results)
predictors = ["Diabetic Foot Ulcers", "Blood Sugar Monitor Frequency"]
ors = [3.355, 0.518]
ci_lower = [1.41, 0.35]
ci_upper = [7.97, 0.77]
p_vals = [0.007, 0.001]

fig, ax = plt.subplots(figsize=(7, 3.5))
y_pos = np.arange(len(predictors))
ax.errorbar(
    ors,
    y_pos,
    xerr=[np.array(ors) - np.array(ci_lower), np.array(ci_upper) - np.array(ors)],
    fmt="o",
    color=BLUE[0],
    capsize=5,
    markersize=8,
)
for i, (or_val, p) in enumerate(zip(ors, p_vals)):
    ax.text(
        ci_upper[i] + 0.1, i, f"OR={or_val:.3f}, p={p:.3f}", va="center", fontsize=9
    )
ax.axvline(1, color="red", linestyle="--", linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(predictors)
ax.set_xlabel("Odds Ratio (95% CI)")
ax.set_title(
    "Independent Predictors of Depression Diagnosis\nBinary Logistic Regression (N=248)"
)
ax.set_xlim(0, 10)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
save_fig(fig, "fig14_depression_predictors_forest_plot.png")


# --- Figure 15: Pearson correlation heatmap (age, diabetes duration, HDRS total) ---
corr_vars = {
    "Age (years)": "AGE",
    "Diabetes Duration (years)": "DIAB_DUR",
    "HDRS Total Score": "HDRS_TOTAL",
}
corr_df = df[[v for v in corr_vars.values() if v in df.columns]].copy()
corr_df.columns = list(corr_vars.keys())[: len(corr_df.columns)]

rho = corr_df.corr(method="pearson")
annot = pd.DataFrame("", index=rho.index, columns=rho.columns)
for r in rho.index:
    for c in rho.columns:
        if r == c:
            annot.loc[r, c] = ""
        else:
            r_val, p_val = stats.pearsonr(corr_df[r].dropna(), corr_df[c].dropna())
            annot.loc[r, c] = f"r={r_val:.3f}\np={p_val:.3f}"

fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(
    rho,
    annot=annot.values,
    fmt="s",
    cmap="coolwarm",
    linewidths=0.5,
    vmin=-1,
    vmax=1,
    cbar_kws={"label": "Pearson r"},
    ax=ax,
)
ax.set_title(
    f"Pearson Correlations: Age, Diabetes Duration, and Depression (N={n})", fontsize=10
)
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
save_fig(fig, "fig15_correlation_heatmap.png")

print(f"\nAll figures saved to: {FIGURES_DIR}")
