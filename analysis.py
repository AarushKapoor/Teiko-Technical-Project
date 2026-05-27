import sqlite3

# Open connection to cell counts db
conn = sqlite3.connect("cell-counts.db")
cursor = conn.cursor()

# Create summary table for frequencies of populations
cursor.execute("""
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
                """)

# Display summary table
rows = cursor.fetchall()
for row in rows:
    print(row)