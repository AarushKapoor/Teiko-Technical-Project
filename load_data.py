import sqlite3
import csv

# Open connection to cell counts db
conn = sqlite3.connect("cell-counts.db")
cursor = conn.cursor()

# Create tables for subjects and samples
cursor.executescript("""
                     DROP TABLE IF EXISTS samples;
                     DROP TABLE IF EXISTS subjects;

                     CREATE TABLE subjects (
                        subject_id TEXT PRIMARY KEY,
                        project TEXT,
                        condition TEXT,
                        age INTEGER,
                        sex TEXT,
                        treatment TEXT,
                        response TEXT
                     );

                     CREATE TABLE samples (
                        sample_id TEXT PRIMARY KEY,
                        subject_id TEXT,
                        sample_type TEXT,
                        time_from_treatment_start INTEGER,
                        b_cell INTEGER,
                        cd8_t_cell INTEGER,
                        cd4_t_cell INTEGER,
                        nk_cell INTEGER,
                        monocyte INTEGER,
                        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
                     );
                     
                     """)

# Open csv file and insert data from csv into tables
with open("cell-count.csv", "r") as f:
    reader = csv.DictReader(f)

    subjects_seen = set()

    for row in reader:
        if row["subject"] not in subjects_seen:
            subjects_seen.add(row["subject"])
            cursor.execute("""
                           INSERT INTO subjects (subject_id, project, condition, age, sex, treatment, response)
                           VALUES (?, ?, ?, ?, ?, ?, ?);
                           """, (row["subject"], row["project"], row["condition"], row["age"], row["sex"], row["treatment"], row["response"]))
            
        cursor.execute("""
                       INSERT INTO samples (sample_id, subject_id, sample_type, time_from_treatment_start, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                       """, (row["sample"], row["subject"], row["sample_type"], row["time_from_treatment_start"], row["b_cell"], row["cd8_t_cell"], row["cd4_t_cell"], row["nk_cell"], row["monocyte"]))

# Close connection
conn.commit()
conn.close()