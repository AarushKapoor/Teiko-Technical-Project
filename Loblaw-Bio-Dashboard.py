import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
import pandas as pd

# Open connection to cell counts db
conn = sqlite3.connect("cell-counts.db")
cursor = conn.cursor()

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Display home page elements
if st.session_state.page == "home":
    st.markdown("## Loblaw Bio Dashboard")

    cols = st.columns(3)

    # Button to access project
    with cols[0]:
        st.markdown("### Projects")
        if st.button("Miraclib Clinical Trial"):
            st.session_state.page = "project"
            st.rerun()

# Display project page elements
elif st.session_state.page == "project":
    
    # Button to go back to home page
    if st.sidebar.button("Back"):
        st.session_state.page = "home"
        st.rerun()
    
    # Sidebar title and buttons to view different analyses
    st.sidebar.markdown("## Miraclib Clinical Trial")
    section = st.sidebar.radio("View", ["Part 2 - Cell Frequencies", "Part 3 - Responder Analysis", "Part 4 - Baseline Analysis"])

    # View for part 2 analysis
    if section == "Part 2 - Cell Frequencies":
        st.markdown("## Part 2 - Cell Frequencies")
        st.markdown("")

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
        # Display summary table
        st.dataframe(df)

        st.write("""
                This table displays the relative frequency of each immune cell population across all samples. For each sample, 
                the total cell count is calculated by summing all five populations, and each population's percentage is computed 
                relative to that total.
                 """)
        
    # View for part 3 analysis
    elif section == "Part 3 - Responder Analysis":
        st.markdown("## Part 3 - Responder Analysis")
        st.markdown("")
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
        # fig1 is the first 3 boxplots, fig2 is the last 2 boxplots, made on separate plots for better visibility
        fig1, axes1 = plt.subplots(1, 3, figsize=(15, 6))
        fig2, axes2 = plt.subplots(1, 2, figsize=(10, 6))

        populations1 = populations[:3]
        populations2 = populations[3:]

        colors = ["#5F9FFF", "#F2E63F", "#6DE431", "#F97C80", "#BF6DE6"]

        for i, pop in enumerate(populations1):
            bp = axes1[i].boxplot([data[pop]["yes"], data[pop]["no"]], labels=["Responders", "Non-responders"], patch_artist=True)
            axes1[i].set_title(pop, fontsize=14)
            axes1[i].set_ylabel("Percentage", fontsize=10)
            axes1[i].tick_params(axis='x', labelsize=12)

            for patch in bp["boxes"]:
                patch.set_facecolor(colors[i])
            for median in bp["medians"]:
                median.set_color("black")

        for i, pop in enumerate(populations2):
            bp = axes2[i].boxplot([data[pop]["yes"], data[pop]["no"]], labels=["Responders", "Non-responders"], patch_artist=True)
            axes2[i].set_title(pop, fontsize=18)
            axes2[i].set_ylabel("Percentage", fontsize=12)
            axes2[i].tick_params(axis='x', labelsize=16)

            for patch in bp["boxes"]:
                patch.set_facecolor(colors[i+3])
            for median in bp["medians"]:
                median.set_color("black")

        # Display boxplots
        plt.tight_layout()
        st.pyplot(fig1, use_container_width=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.pyplot(fig2, use_container_width=True)

        st.write("""
                These boxplots compare the distribution of each immune cell population's relative frequency 
                between responders and non-responders among melanoma patients treated with miraclib.
                 """)

        st.markdown("### P-Values")

        cols = st.columns(5)

        # Calculate and display p-values
        for i, pop in enumerate(populations):
            stat, p = mannwhitneyu(data[pop]["yes"], data[pop]["no"])
            cols[i].write(f"**{pop}**: {p:.4f}")
        
        st.write("""
                These are the p-values comparing responders vs non-responders for each cell population. 
                A p-value below 0.05 indicates that any difference between the two groups is statistically significant, 
                and likely not due to random chance.
                 """)
        
    # View for part 4 analysis
    elif section == "Part 4 - Baseline Analysis":
        st.markdown("## Part 4 - Baseline Analysis")
        st.markdown("")

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

        # Display dataframe view
        baseline_df = pd.read_sql_query("SELECT * FROM baseline_samples", conn)
        st.dataframe(baseline_df)

        st.write("""
                This table shows all baseline PBMC samples (time from treatment start = 0) 
                from melanoma patients treated with miraclib. The counts below summarize the 
                composition of this subset by project, response, and sex.
                 """)

        st.markdown("### Samples per Category")

        baseline_cols = st.columns(3)

        # Count how many of these samples are from each project
        cursor.execute("SELECT project, COUNT(*) FROM baseline_samples GROUP BY project")
        rows = cursor.fetchall()
        baseline_cols[0].markdown(f"<u>**Project**</u>  \n**Project 1**: {rows[0][1]}  \n**Project 2**: 0  \n**Project 3**: {rows[1][1]}", unsafe_allow_html=True)

        # Count how many of these samples are from responders/non-responders
        cursor.execute("SELECT response, COUNT(*) FROM baseline_samples GROUP BY response")
        rows = cursor.fetchall()
        baseline_cols[1].markdown(f"<u>**Response**</u>  \n**Yes**: {rows[1][1]}  \n**No**: {rows[0][1]}", unsafe_allow_html=True)

        # Count how many of these samples are from males/females
        cursor.execute("SELECT sex, COUNT(*) FROM baseline_samples GROUP BY sex")
        rows = cursor.fetchall()
        baseline_cols[2].markdown(f"<u>**Sex**</u>  \n**Male**: {rows[1][1]}  \n**Female**: {rows[0][1]}", unsafe_allow_html=True)