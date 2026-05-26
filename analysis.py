import sqlite3

conn = sqlite3.connect("cell-counts.db")
cursor = conn.cursor()

cursor.execute("""
                SELECT sample_id as sample, total_count, population, count, ROUND(CAST(count AS FLOAT) / total_count * 100, 2) as percentage
                FROM (
                    SELECT sample_id, b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte as total_count,
                    'b_cell' as population, b_cell as count FROM samples
                    UNION ALL
                    SELECT sample_id, b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte as total_count,
                    'cd8_t_cell' as population, cd8_t_cell as count FROM samples
                    UNION ALL
                    SELECT sample_id, b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte as total_count,
                    'cd4_t_cell' as population, cd4_t_cell as count FROM samples
                    UNION ALL
                    SELECT sample_id, b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte as total_count,
                    'nk_cell' as population, nk_cell as count FROM samples
                    UNION ALL
                    SELECT sample_id, b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte as total_count,
                    'monocyte' as population, monocyte as count FROM samples
                    )
                ORDER BY sample
                """)

rows = cursor.fetchall()
for row in rows:
    print(row)