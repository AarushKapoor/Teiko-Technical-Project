# Teiko Technical Project
**Aarush Kapoor**

## Setup & Running

### Requirements
- Python 3.x
- All dependencies are listed in `requirements.txt`

### Instructions
1. Clone the repository
2. Make sure `cell-count.csv` is in the root directory
3. Run the following commands:

```bash
make setup      # installs all dependencies
make pipeline   # loads the data into the database
make dashboard  # starts the dashboard
```

4. Open your browser and navigate to `http://localhost:8501`

---

## Database Schema

The data is split into two tables: `subjects` and `samples`.

**`subjects`** stores information about each patient that doesn't change across their samples:
- `subject_id` (primary key)
- `project`
- `condition`
- `age`
- `sex`
- `treatment`
- `response`

**`samples`** stores each individual sample taken from a subject:
- `sample_id` (primary key)
- `subject_id` (foreign key referencing `subjects`)
- `sample_type`
- `time_from_treatment_start`
- `b_cell`, `cd8_t_cell`, `cd4_t_cell`, `nk_cell`, `monocyte`

### Rationale
Each subject has 3 samples taken at different timepoints (0, 7, and 14 days). Storing subject-level information like age, sex, and treatment response in a separate table avoids repeating that data 3 times per subject. The `samples` table then only stores what's unique to each individual sample — the timepoint and the cell counts.

### Scalability
This design scales well. With hundreds of projects and thousands of samples, keeping subject metadata separate from sample measurements means queries stay efficient — you're not scanning redundant repeated data. Adding new cell population types would just mean adding columns to `samples`. Adding new metadata fields would just mean adding columns to `subjects`. Analytics that need both (like filtering by condition and comparing cell counts) are handled cleanly with a JOIN on `subject_id`. Views like `baseline_samples` can be defined once and reused across different analyses without duplicating query logic.

---

## Code Structure

- **`load_data.py`** — initializes the SQLite database with the `subjects` and `samples` schema, then loads all rows from `cell-count.csv`. This is the first thing that needs to run.
- **`analysis.py`** — queries the database to produce the cell population frequency summary table (Part 2).
- **`statistical_analysis.py`** — filters for melanoma PBMC miraclib samples, computes relative frequencies by responder status, plots boxplots, and runs Mann-Whitney U tests (Part 3).
- **`subset_analysis.py`** — creates a view for baseline samples and answers the subset queries about project counts, response counts, sex counts, and average b_cell count (Part 4).
- **`Loblaw-Bio-Dashboard.py`** — Streamlit dashboard that ties everything together in an interactive UI with home and project pages.

---

## Statistical Findings (Part 3)

To identify whether any immune cell populations differ significantly between responders and non-responders, a Mann-Whitney U test was run on the relative frequencies of each population. The results were:

| Population | p-value |
|------------|---------|
| b_cell | 0.0557 |
| cd8_t_cell | 0.6392 |
| cd4_t_cell | 0.0134 |
| nk_cell | 0.1211 |
| monocyte | 0.1635 |

Using a significance threshold of p < 0.05, **cd4_t_cell** is the only population with a statistically significant difference between responders and non-responders. This means the difference observed is unlikely to be due to random chance.

It's worth noting that **b_cell** came close to the threshold at 0.0557 — just barely above significance. This could be worth monitoring as more data is collected.

Interestingly, the boxplots don't show an obvious visual difference between the two groups for any population — the distributions overlap heavily and the medians are close. This highlights an important distinction: statistical significance doesn't necessarily mean the difference is large or clinically meaningful. With a dataset of this size, even small differences can produce low p-values. Whether the cd4_t_cell finding is actionable is a question for further clinical investigation.

---

## Dashboard

Run `make dashboard` and navigate to `http://localhost:8501`
