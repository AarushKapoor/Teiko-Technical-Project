import sqlite3

# Open connection to cell counts db
conn = sqlite3.connect("cell-counts.db")
cursor = conn.cursor()

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

# Count how many of these samples are from each project
cursor.execute("SELECT project, COUNT(*) FROM baseline_samples GROUP BY project")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Count how many of these samples are from responders/non-responders
cursor.execute("SELECT response, COUNT(*) FROM baseline_samples GROUP BY response")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Count how many of these samples are from males/females
cursor.execute("SELECT sex, COUNT(*) FROM baseline_samples GROUP BY sex")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Considering Melanoma males, what is the average number of B cells for responders at time=0? 10206.15
cursor.execute("""
                SELECT AVG(samples.b_cell)
                FROM samples
                JOIN subjects ON samples.subject_id = subjects.subject_id
                WHERE condition = 'melanoma'
                AND time_from_treatment_start = 0
                AND sex = 'M'
                AND response = 'yes'
               """)
row = cursor.fetchall()
print(f"{row[0][0]:.2f}")