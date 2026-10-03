"""
Mini Project 2 - Standpunkt vs written exam grades in Norwegian high schools.
Author: Talha Aker

This project analyzes the difference between standpunkt grades (teacher-assessed)
and written exam grades for Norwegian upper secondary schools (VGS), using the
public grade statistics from UDIR. It cleans and merges the data, computes the
difference per subject, and visualizes the result.

Data: https://www.udir.no/tall-og-forskning/statistikk/statistikk-videregaende-skole/karakterer-vgs/
Run:  python miniproject2.py
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # save figures without needing a display
import matplotlib.pyplot as plt

# Save figures into a "graphs" folder to keep the project organized.
os.makedirs("graphs", exist_ok=True)

# Load data. The CSV files from UDIR use semicolon as the separator.
df_stand = pd.read_csv("standpunkt_grades_vgs.csv", sep=";", encoding="latin1")
df_exam = pd.read_csv("skriftlig_grades_vgs.csv", sep=";", encoding="latin1")

# Clean column names (remove stray whitespace).
df_stand.columns = df_stand.columns.str.strip()
df_exam.columns = df_exam.columns.str.strip()

# Rename the long statistic columns to something short.
df_stand = df_stand.rename(columns={
    "2024-25.Standpunkt.Alle eierformer.Alle kjønn.Snittkarakter": "standpunkt"
})
df_exam = df_exam.rename(columns={
    "2024-25.Skriftlig eksamen.Alle eierformer.Alle kjønn.Snittkarakter": "exam"
})

# Keep only the columns needed for the analysis.
df_stand = df_stand[["Fylke", "Vurderingsfagnavn", "standpunkt"]]
df_exam = df_exam[["Fylke", "Vurderingsfagnavn", "exam"]]

# Convert grades to numeric ("4,5" -> 4.5) and turn invalid values like "*" into NaN.
df_stand["standpunkt"] = pd.to_numeric(
    df_stand["standpunkt"].astype(str).str.replace(",", "."), errors="coerce")
df_exam["exam"] = pd.to_numeric(
    df_exam["exam"].astype(str).str.replace(",", "."), errors="coerce")

# Drop rows with missing grades.
df_stand = df_stand.dropna()
df_exam = df_exam.dropna()

# Merge the two tables on county and subject.
df = pd.merge(df_stand, df_exam, on=["Fylke", "Vurderingsfagnavn"])

# Difference between the teacher-assessed grade and the written exam grade.
df["difference"] = df["standpunkt"] - df["exam"]

# Overall trend.
avg_diff = df["difference"].mean()
print("Average difference:", round(avg_diff, 3))

# Average difference per subject.
subject_diff = df.groupby("Vurderingsfagnavn")["difference"].mean()
print("\nAverage difference by subject:")
print(subject_diff)


# Bar chart: average difference per subject (long names are shortened).
def shorten_label(label):
    label = str(label)
    return label[:20] + "..." if len(label) > 20 else label


plot_data = subject_diff.copy()
plot_data.index = [shorten_label(label) for label in plot_data.index]

plt.figure(figsize=(10, 12))
plot_data.sort_values().plot(kind="barh")
plt.title("Difference between standpunkt and exam grades")
plt.xlabel("Average difference")
plt.ylabel("Subjects")
plt.tight_layout()
plt.savefig("graphs/difference_between_standpunkt_and_exam.png")

# Histogram: how the differences are distributed.
plt.figure()
df["difference"].plot(kind="hist", bins=20)
plt.title("Distribution of grade differences")
plt.xlabel("Difference (standpunkt - exam)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("graphs/distribution_of_grade_differences.png")

# Conclusion.
if avg_diff > 0:
    print("\nConclusion: standpunkt grades are generally higher than exam grades.")
else:
    print("\nConclusion: exam grades are higher than standpunkt grades.")

print("\nProject completed successfully.")


# ----------------------------------------------------------------------
# Findings
#
# The average difference is about 0.47, so standpunkt grades are generally
# higher than written exam grades.
#
# In "difference_between_standpunkt_and_exam.png" most subjects show a
# positive difference, meaning teacher-based assessment tends to give higher
# grades. A few subjects show a small or negative difference, where exam
# grades are similar or higher. The variation suggests the gap depends on the
# subject and the assessment method.
#
# In "distribution_of_grade_differences.png" the histogram is roughly normal
# and centered above zero, which confirms that most differences are positive
# and supports the conclusion above.
# ----------------------------------------------------------------------
