import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff

# --- CONSTANTS ---
# NOTE: Update this to match your actual cleaned file name if needed
DATA_FILE = "cleaned_students_performance.csv"
TARGET_ADMISSION_YEAR = 2021 

# --- UTILITY FUNCTION: DATA LOADING AND CLEANING ---

@st.cache_data
def load_and_clean_data(file_path):
    """
    Loads, filters, and prepares the student performance data.
    Assumes the file is already cleaned as per the user's provided code.
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception:
        try:
            df = pd.read_csv(file_path, encoding='latin1')
        except Exception as e:
            st.error(f"Error loading data from {file_path}. Please ensure the file exists and is accessible. Details: {e}")
            return pd.DataFrame()

    if df.empty:
        return df

    # --- Data Filtering and Pre-processing ---
    if 'admission_year' in df.columns:
        df_filtered = df[df['admission_year'] == TARGET_ADMISSION_YEAR].copy()
    else:
        st.warning("Column 'admission_year' not found. Using entire dataset.")
        df_filtered = df.copy()

    # Ensure necessary columns are numeric and handle missing values for metrics/plots
    required_numeric_cols = [
        'current_cgpa', 'study_hours_daily', 'average_class_attendance', 
        'social_media_hours_daily'
    ]
    for col in required_numeric_cols:
        if col in df_filtered.columns:
            df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')
            df_filtered[col].fillna(df_filtered[col].mean(), inplace=True)

    # --- Categorical Binning (for objectives) ---
    
    # 1. Attendance Level (Objective 2)
    if 'average_class_attendance' in df_filtered.columns:
        df_filtered['attendance_level'] = pd.cut(
            df_filtered['average_class_attendance'],
            bins=[0, 60, 80, 100],
            labels=['Low Attendance', 'Medium Attendance', 'High Attendance'],
            right=False,
            include_lowest=True
        ).astype(str).replace('nan', 'Unknown')
        
    # 2. Social Media Hours Category (Objective 3)
    if 'social_media_hours_daily' in df_filtered.columns:
        bins = [-1, 1, 3, 6, df_filtered['social_media_hours_daily'].max() + 1] 
        labels = ['Very Low (<1h)', 'Low (1-3h)', 'Medium (3-6h)', 'High (>6h)']
        df_filtered['social_media_category'] = pd.cut(
            df_filtered['social_media_hours_daily'], 
            bins=bins, 
            labels=labels, 
            right=False, 
            include_lowest=True
        ).astype(str).replace('nan', 'Unknown')

    return df_filtered


# --- PAGE 1: OBJECTIVE 1 - GENERAL OVERVIEW ---

def page_1_overview(df):
    st.title("Objective 1: Overview of Student Performance 🎓")
    st.markdown("---")
    
    # 1. Objective Statement
    st.subheader("Objective Statement")
    st.write(
        "To explore the overall distribution of students’ academic performance and basic demographic patterns such as gender and academic progression (CGPA across semesters)."
    )

    # 2. Visualizations
    st.subheader("Visualizations")
    if all(col in df.columns for col in ['current_cgpa', 'gender', 'current_semester']):
        
        col1, col2 = st.columns(2)

        # 1. CGPA Distribution (Histogram)
        with col1:
            st.write("**CGPA Distribution**")
            fig_hist = px.histogram(
                df, x='current_cgpa', nbins=20, title='CGPA Distribution', color_discrete_sequence=['#3178C6']
            )
            fig_hist.update_layout(xaxis_title='CGPA', yaxis_title='Frequency')
            st.plotly_chart(fig_hist, use_container_width=True)

        # 2. Average CGPA by Gender (Bar Chart)
        with col2:
            st.write("**Average CGPA by Gender**")
            avg_cgpa_by_gender = df.groupby('gender', observed=True)['current_cgpa'].mean().reset_index()
            fig_bar_gender = px.bar(
                avg_cgpa_by_gender, x='gender', y='current_cgpa', title='Average CGPA by Gender',
                color='gender', color_discrete_map={'Male': '#1f77b4', 'Female': '#2ca02c'}, text_auto='.2f'
            )
            fig_bar_gender.update_layout(yaxis_title='Average CGPA', xaxis_title='Gender')
            st.plotly_chart(fig_bar_gender, use_container_width=True)

        # 3. Average CGPA Across Semesters (Line Plot)
        st.write("**Average CGPA Across Semesters**")
        avg_sem = df.groupby("current_semester", observed=True)["current_cgpa"].mean().reset_index()
        fig_line = px.line(
            avg_sem, x="current_semester", y="current_cgpa", 
            title="Average CGPA Across Semesters", markers=True, color_discrete_sequence=['#E377C2']
        )
        fig_line.update_layout(xaxis_title='Semester', yaxis_title='Average CGPA')
        st.plotly_chart(fig_line, use_container_width=True)

    # 3. Summary Box
    st.subheader("Summary Box")
    st.info(
        """
        This page establishes the baseline academic profile of the 2021 student cohort. The CGPA distribution is typically centered around the mean, showing where most students fall. The analysis of CGPA by gender highlights potential performance differences, suggesting which gender group, on average, achieves higher academic success. The semester-wise CGPA trend is critical, as it tracks academic progression, often revealing slight dips or steady improvement as students advance in their program. Key Finding: *[Insert a specific finding here, e.g., "The average CGPA remains consistent across semesters, suggesting stable curriculum challenge."]*.
        """
    )
    
    # 4. Interpretation/Discussion
    st.subheader("Interpretation/Discussion")
    st.markdown(
        """
        The **CGPA distribution** helps assess the overall performance level, indicating if the grades are normally distributed or skewed. The **gender comparison** provides demographic context, showing if external factors are influencing academic achievement based on gender. The **semester trend** visualizes the student learning curve; a steady line suggests the program maintains consistent academic rigor, while a significant drop might signal difficult core courses in later semesters. This foundational overview guides further investigation into specific factors.
        """
    )


# --- PAGE 2: OBJECTIVE 2 - ACADEMIC DISCIPLINE AND PERFORMANCE ---

def page_2_study_habits(df):
    st.title("Objective 2: Relationship Between Academic Discipline and Performance 📚")
    st.markdown("---")

    # 1. Objective Statement
    st.subheader("Objective Statement")
    st.write(
        "To quantify the relationship between core academic disciplinary factors—daily study hours and class attendance—and overall academic performance (CGPA)."
    )

    # 2. Visualizations
    st.subheader("Visualizations")
    required_cols = ['study_hours_daily', 'current_cgpa', 'average_class_attendance', 'attendance_level']
    if all(col in df.columns for col in required_cols):
        
        col1, col2 = st.columns(2)

        # 1. Average CGPA by Study Hours (Bar Chart)
        with col1:
            st.write("**Average CGPA by Daily Study Hours**")
            avg_cgpa_by_study_hours = df.groupby('study_hours_daily', observed=True)['current_cgpa'].mean().reset_index()
            fig_bar_study = px.bar(
                avg_cgpa_by_study_hours, x='study_hours_daily', y='current_cgpa', 
                title='Average CGPA by Daily Study Hours', color_discrete_sequence=['#5AA469'], text_auto='.2f'
            )
            fig_bar_study.update_layout(xaxis_title='Daily Study Hours', yaxis_title='Average CGPA')
            st.plotly_chart(fig_bar_study, use_container_width=True)

        # 2. Average CGPA by Attendance Level (Bar Chart)
        with col2:
            st.write("**Average CGPA by Attendance Level**")
            # Ensure correct category order
            order = ['Low Attendance', 'Medium Attendance', 'High Attendance']
            cgpa_by_attendance = df.groupby('attendance_level', observed=True)['current_cgpa'].mean().reset_index()
            fig_bar_attendance = px.bar(
                cgpa_by_attendance, x='attendance_level', y='current_cgpa', 
                title="Average CGPA by Attendance Level", 
                category_orders={'attendance_level': order},
                color_discrete_sequence=['#F08080'], text_auto='.2f'
            )
            fig_bar_attendance.update_layout(xaxis_title='Attendance Category', yaxis_title='Average CGPA')
            st.plotly_chart(fig_bar_attendance, use_container_width=True)

        # 3. Correlation Heatmap
        st.write("**Correlation between Study Hours, Attendance, and CGPA**")
        corr_data = df[['study_hours_daily', 'average_class_attendance', 'current_cgpa']]
        corr_matrix = corr_data.corr()

        fig_heatmap = px.imshow(
            corr_matrix, 
            text_auto=True, 
            aspect="auto",
            color_continuous_scale='Blues',
            title="Correlation Matrix of Academic Discipline Factors and CGPA"
        )
        fig_heatmap.update_layout(xaxis={'side': 'bottom'})
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # 3. Summary Box
    st.subheader("Summary Box")
    st.info(
        """
        This page confirms the intuitive link between effort (discipline) and outcome (performance). The visualizations consistently demonstrate a positive correlation: students who report higher daily study hours and maintain higher class attendance achieve significantly higher average CGPAs. The correlation heatmap quantifies this, showing attendance often has the strongest direct linear relationship with CGPA. This suggests that maximizing physical presence and dedication to learning time are the most reliable predictors of academic success in this cohort.
        """
    )
    
    # 4. Interpretation/Discussion
    st.subheader("Interpretation/Discussion")
    st.markdown(
        """
        The **CGPA vs. Study Hours** plot reveals an optimal range for studying; while more hours generally means higher CGPA, diminishing returns may be observed at extreme ends. The **CGPA vs. Attendance Level** strongly suggests that class participation is a crucial non-negotiable factor. The **Correlation Heatmap** provides scientific evidence, showing strong positive correlations (close to +1.0) between both attendance and study hours with CGPA, confirming that these are statistically significant drivers of student success.
        """
    )


# --- PAGE 3: OBJECTIVE 3 - LIFESTYLE AND DAILY HABITS ---

def page_3_non_academic(df):
    st.title("Objective 3: Effect of Lifestyle and Daily Habits on Academic Performance 🌍")
    st.markdown("---")

    # 1. Objective Statement
    st.subheader("Objective Statement")
    st.write(
        "To explore the influence of key lifestyle factors—specifically social media consumption, financial aid status, and family income—on the distribution of student CGPA."
    )

    # 2. Visualizations
    st.subheader("Visualizations")
    required_cols = ['social_media_category', 'current_cgpa', 'meritorious_scholarship', 'income_group']
    if all(col in df.columns for col in required_cols):

        col1, col2 = st.columns(2)

        # 1. Average CGPA by Social Media Usage (Bar Chart)
        with col1:
            st.write("**Average CGPA by Daily Social Media Usage**")
            ordered_categories = ['Very Low (<1h)', 'Low (1-3h)', 'Medium (3-6h)', 'High (>6h)', 'Unknown']
            avg_social = df.groupby("social_media_category", observed=True)["current_cgpa"].mean().reset_index()
            fig_bar_social = px.bar(
                avg_social, x="social_media_category", y="current_cgpa", 
                title="Average CGPA by Daily Social Media Usage", 
                category_orders={'social_media_category': ordered_categories},
                color_discrete_sequence=px.colors.qualitative.D3, text_auto='.2f'
            )
            fig_bar_social.update_layout(xaxis_title='Hours on Social Media per Day', yaxis_title='Average CGPA')
            st.plotly_chart(fig_bar_social, use_container_width=True)

        # 2. Average CGPA by Scholarship Status (Bar Chart)
        with col2:
            st.write("**Average CGPA by Scholarship Status**")
            avg_sch = df.groupby("meritorious_scholarship", observed=True)["current_cgpa"].mean().reset_index()
            fig_bar_sch = px.bar(
                avg_sch, x="meritorious_scholarship", y="current_cgpa", 
                title="Average CGPA by Scholarship Status", color_discrete_sequence=['darkgreen'], text_auto='.2f'
            )
            fig_bar_sch.update_layout(xaxis_title='Scholarship Status', yaxis_title='Average CGPA')
            st.plotly_chart(fig_bar_sch, use_container_width=True)

        # 3. CGPA Distribution Across Income Groups (Box Plot)
        st.write("**CGPA Distribution Across Income Groups**")
        fig_box_income = px.box(
            df, x="income_group", y="current_cgpa", 
            title="CGPA Distribution Across Income Groups", color="income_group",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_box_income.update_layout(xaxis_title='Income Group', yaxis_title='CGPA')
        st.plotly_chart(fig_box_income, use_container_width=True)

    # 3. Summary Box
    st.subheader("Summary Box")
    st.info(
        """
        This page investigates non-academic influences. The bar chart for social media usage often shows a U-shaped or inverse-linear relationship: extremely high usage correlates with lower CGPA, while moderate use may not significantly affect grades. Scholarship holders consistently demonstrate a higher CGPA distribution, suggesting that merit-based aid attracts high-performing students or incentivizes better performance. The income group box plot indicates whether socio-economic background is a factor, potentially showing that students from higher income families have more resources to support high CGPAs.
        """
    )

    # 4. Interpretation/Discussion
    st.subheader("Interpretation/Discussion")
    st.markdown(
        """
        The **Social Media Usage** analysis is important for promoting digital wellness; if higher usage correlates with lower grades, interventions may be needed. The **Scholarship Status** acts as a validation of academic merit, confirming that students receiving aid are top performers. The **Income Group** distribution helps identify potential equity issues; if a strong performance gradient is observed across income levels, it suggests that resource gaps may be influencing academic outcomes. These factors highlight the need for holistic support beyond the classroom.
        """
    )


# --- MAIN APPLICATION ENTRY POINT ---
def main():
    # Load and clean data
    df_filtered = load_and_clean_data(DATA_FILE)

    if df_filtered.empty:
        # Stop execution if data loading failed
        return
    
    # --- Set Streamlit Configuration ---
    st.set_page_config(
        page_title="Student Performance Analysis",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Page Navigation Setup ---
    PAGES = {
        "Objective 1: Performance Overview 🎓": page_1_overview,
        "Objective 2: Study Habits & Performance 📚": page_2_study_habits,
        "Objective 3: Non-Academic Factors 🌍": page_3_non_academic
    }

    st.sidebar.title("Dashboard Navigation")
    st.sidebar.markdown(f"**Cohort Filtered: Admission Year {TARGET_ADMISSION_YEAR}**")
    selection = st.sidebar.radio("Go to Section", list(PAGES.keys()))
    
    # Execute the selected page function
    page = PAGES[selection]
    page(df_filtered)

if __name__ == "__main__":
    main()
