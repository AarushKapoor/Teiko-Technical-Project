import sqlite3
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

# Open connection to cell counts db
conn = sqlite3.connect("cell-counts.db")
cursor = conn.cursor()

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
plt.show()

# Calculate p-values
for pop in populations:
    stat, p = mannwhitneyu(data[pop]["yes"], data[pop]["no"])
    print(f"{pop}: p-value = {p:.4f}")