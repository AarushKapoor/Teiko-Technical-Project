import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
import pandas as pd

st.title("Loblaw Bio - Clinical Trial Dashboard")

# Open connection to cell counts db
conn = sqlite3.connect("cell-counts.db")
cursor = conn.cursor()

st.header("Part 2 - Cell Population Frequencies")

# Create summary table for frequencies of populations
df = pd.read_sql_query("""
                        WITH base AS (
                        SELECT *, b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte as total_count
                        FROM samples
                        )
                        SELECT sample_id as sample, total_count, population, count, ROUND(CAST(count AS FLOAT) / total_count * 100, 2) as percentage
                        FROM (
                            SELECT sample_id, total_count, 'b_cell' as population, b_cell as count FROM base
                            UNION ALL
                            SELECT sample_id, total_count, 'cd8_t_cell' as population, cd8_t_cell as count FROM base
                            UNION ALL
                            SELECT sample_id, total_count, 'cd4_t_cell' as population, cd4_t_cell as count FROM base
                            UNION ALL
                            SELECT sample_id, total_count, 'nk_cell' as population, nk_cell as count FROM base
                            UNION ALL
                            SELECT sample_id, total_count, 'monocyte' as population, monocyte as count FROM base
                            )
                        ORDER BY sample
                       """, conn)
st.dataframe(df)

st.header("Part 3 - Population Frequencies in Responders vs Non-responders")

# Query data for PBMC samples, melanoma patients, miraclib treatment, and responses
cursor.execute("""
                WITH filtered AS (
                    SELECT samples.*, subjects.response, b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte as total_count
                    FROM samples
                    JOIN subjects ON samples.subject_id = subjects.subject_id
                    WHERE condition = 'melanoma' AND treatment = 'miraclib' AND sample_type = 'PBMC'
               )
                SELECT sample_id as sample, population, ROUND(CAST(count AS FLOAT) / total_count * 100, 2) as percentage, response
                FROM (
                    SELECT sample_id, total_count, 'b_cell' as population, b_cell as count, response FROM filtered
                    UNION ALL
                    SELECT sample_id, total_count, 'cd8_t_cell' as population, cd8_t_cell as count, response FROM filtered
                    UNION ALL
                    SELECT sample_id, total_count, 'cd4_t_cell' as population, cd4_t_cell as count, response FROM filtered
                    UNION ALL
                    SELECT sample_id, total_count, 'nk_cell' as population, nk_cell as count, response FROM filtered
                    UNION ALL
                    SELECT sample_id, total_count, 'monocyte' as population, monocyte as count, response FROM filtered
                    )
                ORDER BY sample
                """)

# Filter data based on response yes or no
rows = cursor.fetchall()
populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
data = {pop: {"yes": [], "no": []} for pop in populations}
for row in rows:
    data[row[1]][row[3]].append(row[2])

# Plot data as 5 sets of 2 boxplots to observe differences in populations based on response
fig, axes = plt.subplots(1, 5, figsize=(15, 6))

for i, pop in enumerate(populations):
    axes[i].boxplot([data[pop]["yes"], data[pop]["no"]], labels=["Responders", "Non-responders"])
    axes[i].set_title(pop)
    axes[i].set_ylabel("Percentage")

plt.tight_layout()
st.pyplot(fig)

cols = st.columns(5)

# Calculate and display p-values
for i, pop in enumerate(populations):
    stat, p = mannwhitneyu(data[pop]["yes"], data[pop]["no"])
    cols[i].write(f"**{pop}**:  \np-value = {p:.4f}")

st.header("Part 4 - Baseline Sample Analysis")

# Create a view in the db for all samples with the given conditions
cursor.executescript("""
                DROP VIEW IF EXISTS baseline_samples;

                CREATE VIEW baseline_samples AS
                SELECT samples.*, subjects.response, subjects.sex, subjects.project
                FROM samples
                JOIN subjects ON samples.subject_id = subjects.subject_id
                WHERE condition = 'melanoma'
                AND treatment = 'miraclib'
                AND sample_type = 'PBMC'
                AND time_from_treatment_start = 0;
               
               """)

baseline_df = pd.read_sql_query("SELECT * FROM baseline_samples", conn)
st.dataframe(baseline_df)

baseline_cols = st.columns(3)

# Count how many of these samples are from each project
cursor.execute("SELECT project, COUNT(*) FROM baseline_samples GROUP BY project")
rows = cursor.fetchall()
for row in rows:
    baseline_cols[0].write(f"Samples from {row[0]}: {row[1]}")

# Count how many of these samples are from responders/non-responders
cursor.execute("SELECT response, COUNT(*) FROM baseline_samples GROUP BY response")
rows = cursor.fetchall()
for row in rows:
    baseline_cols[1].write(f"Samples with response {row[0]}: {row[1]}")

# Count how many of these samples are from males/females
cursor.execute("SELECT sex, COUNT(*) FROM baseline_samples GROUP BY sex")
rows = cursor.fetchall()
for row in rows:
    baseline_cols[2].write(f"Samples from {row[0]}: {row[1]}")