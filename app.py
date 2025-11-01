import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff

# --- CONSTANTS ---
# NOTE: Update this to match your actual cleaned file name if needed
DATA_FILE = "cleaned_students_performance.csv"
TARGET_ADMISSION_YEAR = 2021 

# --- Consistent Color Palette for Dashboard Consistency (BOLD and VIBRANT) ---
# New Bold Palette:
COLOR_PRIMARY_CGPA = '#00bcd4'  # Cyan/Aqua - Bold for General Performance/CGPA
COLOR_DISCIPLINE = '#ff5722'    # Deep Orange/Red - Bold for Study Habits/Attendance
COLOR_LIFESTYLE = '#9c27b0'     # Vibrant Purple - Bold for Non-Academic/Lifestyle Factors
COLOR_GENDER_MALE = '#2196f3'   # Bright Blue
COLOR_GENDER_FEMALE = '#e91e63' # Hot Pink/Magenta

# --- UTILITY FUNCTION: DATA LOADING AND CLEANING ---

@st.cache_data
def load_and_clean_data(file_path):
    """
    Loads, filters, and prepares the student performance data, assuming 
    columns based on the user's provided code snippets (e.g., current_cgpa, gender).
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
            # Fill NaNs with the mean for numerical columns
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
    st.title("Objective 1: General Overview of Student Performance 🎓")
    st.markdown("---")
    
    # 1. Summary Box (Metric Cards) - MOVED UP
    st.subheader("Key Metrics Summary")
    
    # Calculate metrics for Objective 1
    avg_cgpa = df['current_cgpa'].mean()
    avg_semester = df['current_semester'].mean()
    male_avg_cgpa = df[df['gender'] == 'Male']['current_cgpa'].mean()
    female_avg_cgpa = df[df['gender'] == 'Female']['current_cgpa'].mean()

    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(label="Overall Avg CGPA", value=f"{avg_cgpa:.2f}", 
                help="Average CGPA for the entire 2021 cohort.", border=True)
    col2.metric(label="Avg Current Semester", value=f"{avg_semester:.1f}", 
                help="Average semester level of students in the cohort.", border=True)
    col3.metric(label="Male Avg CGPA", value=f"{male_avg_cgpa:.2f}", 
                help="Average CGPA specifically for Male students.", border=True)
    col4.metric(label="Female Avg CGPA", value=f"{female_avg_cgpa:.2f}", 
                help="Average CGPA specifically for Female students.", border=True)
    
    # 2. Objective Statement
    st.subheader("Objective Statement")
    st.write(
        "To explore the overall distribution of students’ academic performance and basic demographic patterns such as gender and academic progression (CGPA across semesters)."
    )

    # 3. Visualizations
    st.subheader("Visualizations")
    if all(col in df.columns for col in ['current_cgpa', 'gender', 'current_semester']):
        
        # Charts 1 and 2 (Half-width)
        col1, col2 = st.columns(2)

        # 1. CGPA Distribution (Histogram)
        with col1:
            st.write("**CGPA Distribution**")
            # Keeping this chart as requested (single color)
            fig_hist = px.histogram(
                df, x='current_cgpa', nbins=20, title='CGPA Distribution of Students', 
                color_discrete_sequence=[COLOR_PRIMARY_CGPA] # BOLD COLOR 1
            )
            fig_hist.update_layout(xaxis_title='CGPA', yaxis_title='Frequency')
            st.plotly_chart(fig_hist, use_container_width=True)

        # 2. Average CGPA by Gender (Bar Chart) - Already uses multiple colors
        with col2:
            st.write("**Average CGPA by Gender**")
            avg_cgpa_by_gender = df.groupby('gender', observed=True)['current_cgpa'].mean().reset_index()
            fig_bar_gender = px.bar(
                avg_cgpa_by_gender, x='gender', y='current_cgpa', title='Average CGPA by Gender',
                color='gender', 
                # Uses distinct bold colors for Male/Female
                color_discrete_map={'Male': COLOR_GENDER_MALE, 'Female': COLOR_GENDER_FEMALE}, 
                text_auto='.2f'
            )
            fig_bar_gender.update_layout(yaxis_title='Average CGPA', xaxis_title='Gender')
            st.plotly_chart(fig_bar_gender, use_container_width=True)

        # 3. Average CGPA Across Semesters (Line Plot)
        # Wrapping in columns to enforce half-width size consistency
        col3, _ = st.columns(2)
        with col3:
            st.write("**Average CGPA Across Semesters**")
            avg_sem = df.groupby("current_semester", observed=True)["current_cgpa"].mean().reset_index()
            fig_line = px.line(
                avg_sem, x="current_semester", y="current_cgpa", 
                title="Average CGPA Across Semesters", markers=True, 
                color_discrete_sequence=[COLOR_PRIMARY_CGPA] # BOLD COLOR 1
            )
            fig_line.update_layout(xaxis_title='Semester', yaxis_title='Average CGPA')
                
            st.plotly_chart(fig_line, use_container_width=True)

    # 4. Interpretation/Discussion (Simplified English - Broken down by chart)
    st.subheader("Interpretation/Discussion")
    st.markdown(
        """
        **1. CGPA Distribution:** This histogram shows where most of the students' grades fall. If the curve is high in the middle, it means most students are performing around the average.
        
        **2. Average CGPA by Gender:** This chart helps us check if male and female students perform differently on average. Small differences are normal, but a large gap might suggest a factor affecting one group more than the other.
        
        **3. Average CGPA Across Semesters:** This line shows the average performance of students as they move through their course. A flat line means the difficulty stays the same, while a dip might point to a specific, harder semester.
        """
    )


# --- PAGE 2: OBJECTIVE 2 - ACADEMIC DISCIPLINE AND PERFORMANCE ---

def page_2_study_habits(df):
    st.title("Objective 2: Relationship Between Academic Discipline and Performance 📚")
    st.markdown("---")

    # 1. Summary Box (Metric Cards) - MOVED UP
    st.subheader("Key Metrics Summary")

    # Calculate metrics for Objective 2
    avg_study_hours = df['study_hours_daily'].mean()
    avg_attendance = df['average_class_attendance'].mean()
    # Calculate CGPA for High Attendance, handling potential missing group
    high_attendance_cgpa = df[df['attendance_level'] == 'High Attendance']['current_cgpa'].mean()
    if pd.isna(high_attendance_cgpa): high_attendance_cgpa = 0.0
    
    # Correlation between study_hours_daily and current_cgpa
    study_cgpa_corr = df[['study_hours_daily', 'current_cgpa']].corr().iloc[0, 1]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label="Avg Daily Study Hrs", value=f"{avg_study_hours:.1f} hrs", 
                help="Average daily hours spent studying.", border=True)
    col2.metric(label="Avg Class Attendance", value=f"{avg_attendance:.1f}%", 
                help="Overall average percentage of class attendance.", border=True)
    col3.metric(label="CGPA (High Attendance)", value=f"{high_attendance_cgpa:.2f}", 
                help="Average CGPA for students with High Attendance (80%+).", border=True)
    col4.metric(label="Study/CGPA Correlation", value=f"{study_cgpa_corr:.2f}", 
                help="Correlation coefficient between daily study hours and CGPA.", border=True)

    # 2. Objective Statement
    st.subheader("Objective Statement")
    st.write(
        "To quantify the relationship between core academic disciplinary factors—daily study hours and class attendance—and overall academic performance (CGPA)."
    )

    # 3. Visualizations
    st.subheader("Visualizations")
    required_cols = ['study_hours_daily', 'current_cgpa', 'average_class_attendance', 'attendance_level']
    if all(col in df.columns for col in required_cols):
        
        # Charts 1 and 2 (Half-width)
        col1, col2 = st.columns(2)

        # 1. Average CGPA by Study Hours (Bar Chart) - Now multi-colored
        with col1:
            st.write("**Average CGPA by Daily Study Hours**")
            avg_cgpa_by_study_hours = df.groupby('study_hours_daily', observed=True)['current_cgpa'].mean().reset_index()
            fig_bar_study = px.bar(
                avg_cgpa_by_study_hours, x='study_hours_daily', y='current_cgpa', 
                title='Average CGPA by Daily Study Hours', 
                color='study_hours_daily', # Color based on the category for distinct colors
                color_discrete_sequence=px.colors.qualitative.Vivid, # Use a bold, multi-color sequence
                text_auto='.2f'
            )
            fig_bar_study.update_layout(xaxis_title='Daily Study Hours', yaxis_title='Average CGPA')
            st.plotly_chart(fig_bar_study, use_container_width=True)

        # 2. Average CGPA by Attendance Level (Bar Chart) - Now multi-colored
        with col2:
            st.write("**Average CGPA by Attendance Level**")
            # Ensure correct category order
            order = ['Low Attendance', 'Medium Attendance', 'High Attendance']
            cgpa_by_attendance = df.groupby('attendance_level', observed=True)['current_cgpa'].mean().reset_index()
            fig_bar_attendance = px.bar(
                cgpa_by_attendance, x='attendance_level', y='current_cgpa', 
                title="Average CGPA by Attendance Level", 
                category_orders={'attendance_level': order},
                color='attendance_level', # Color based on the category for distinct colors
                color_discrete_sequence=px.colors.qualitative.Vivid, # Use a bold, multi-color sequence
                text_auto='.2f'
            )
            fig_bar_attendance.update_layout(xaxis_title='Attendance Category', yaxis_title='Average CGPA')
            st.plotly_chart(fig_bar_attendance, use_container_width=True)

        # 3. Correlation Heatmap
        # Wrapping in columns to enforce half-width size consistency
        col3, _ = st.columns(2)
        with col3:
            st.write("**Correlation between Study Hours, Attendance, and CGPA**")
            corr_data = df[['study_hours_daily', 'average_class_attendance', 'current_cgpa']]
            corr_matrix = corr_data.corr()

            fig_heatmap = px.imshow(
                corr_matrix, 
                text_auto=True, 
                aspect="auto",
                # Use a bold, modern gradient for the heatmap
                color_continuous_scale='Plasma', 
                title="Correlation Matrix of Academic Discipline Factors and CGPA"
            )
            fig_heatmap.update_layout(xaxis={'side': 'bottom'})
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 4. Interpretation/Discussion (Simplified English - Broken down by chart)
    st.subheader("Interpretation/Discussion")
    st.markdown(
        """
        **1. Average CGPA by Daily Study Hours:** This graph usually shows that more study hours lead to better grades. We look for an "ideal" study time where the grades are highest before they level off (or stop improving).
        
        **2. Average CGPA by Attendance Level:** This clearly shows how important class attendance is. We expect students with **High Attendance** to have the best average grades, proving that showing up is key to success.
        
        **3. Correlation Heatmap:** This map uses numbers to confirm our observations. A number close to **1** shows a strong, positive link. This proves that high study hours and high attendance are scientifically related to a high CGPA.
        """
    )


# --- PAGE 3: OBJECTIVE 3 - LIFESTYLE AND DAILY HABITS ---

def page_3_non_academic(df):
    st.title("Objective 3: Impact of Lifestyle and Daily Habits on Academic Performance 🌍")
    st.markdown("---")

    # 1. Summary Box (Metric Cards) - MOVED UP
    st.subheader("Key Metrics Summary")

    # Calculate metrics for Objective 3
    scholarship_cgpa = df[df['meritorious_scholarship'] == 'Yes']['current_cgpa'].mean()
    
    # Calculate CGPA for High Social Media Use, handling potential missing group
    high_social_media_cgpa = df[df['social_media_category'] == 'High (>6h)']['current_cgpa'].mean()
    if pd.isna(high_social_media_cgpa): high_social_media_cgpa = 0.0

    # Calculate mode for Income Group
    most_freq_income = df['income_group'].mode()[0] if not df['income_group'].empty else "N/A"
    
    # Calculate percentage with health issues (using the column name from data)
    health_issues_percent = 0
    if 'Do you have any health issues?' in df.columns:
        health_issues_percent = (df['Do you have any health issues?'].str.contains('Yes', case=False, na=False).sum() / len(df)) * 100
        
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label="CGPA (Scholarship)", value=f"{scholarship_cgpa:.2f}", 
                help="Average CGPA for students with a meritorious scholarship.", border=True)
    col2.metric(label="CGPA (High Social Media)", value=f"{high_social_media_cgpa:.2f}", 
                help="Average CGPA for students spending >6 hours on social media.", border=True)
    col3.metric(label="Most Frequent Income", value=f"{most_freq_income}", 
                help="The most common monthly family income group.", border=True)
    col4.metric(label="% With Health Issues", value=f"{health_issues_percent:.1f}%", 
                help="Percentage of students reporting a health issue.", border=True)

    # 2. Objective Statement
    st.subheader("Objective Statement")
    st.write(
        "To explore the influence of key lifestyle factors—specifically social media consumption, financial aid status, and family income—on the distribution of student CGPA."
    )

    # 3. Visualizations
    st.subheader("Visualizations")
    required_cols = ['social_media_category', 'current_cgpa', 'meritorious_scholarship', 'income_group']
    if all(col in df.columns for col in required_cols):

        # Charts 1 and 2 (Half-width)
        col1, col2 = st.columns(2)

        # 1. Average CGPA by Social Media Usage (Bar Chart) - Now multi-colored
        with col1:
            st.write("**Average CGPA by Daily Social Media Usage**")
            ordered_categories = ['Very Low (<1h)', 'Low (1-3h)', 'Medium (3-6h)', 'High (>6h)', 'Unknown']
            avg_social = df.groupby("social_media_category", observed=True)["current_cgpa"].mean().reset_index()
            fig_bar_social = px.bar(
                avg_social, x="social_media_category", y="current_cgpa", 
                title="Average CGPA by Daily Social Media Usage", 
                category_orders={'social_media_category': ordered_categories},
                color="social_media_category", # Color based on the category for distinct colors
                color_discrete_sequence=px.colors.qualitative.Vivid, # Use a bold, multi-color sequence
                text_auto='.2f'
            )
            fig_bar_social.update_layout(xaxis_title='Hours on Social Media per Day', yaxis_title='Average CGPA')
            st.plotly_chart(fig_bar_social, use_container_width=True)

        # 2. Average CGPA by Scholarship Status (Bar Chart) - Now multi-colored
        with col2:
            st.write("**Average CGPA by Scholarship Status**")
            avg_sch = df.groupby("meritorious_scholarship", observed=True)["current_cgpa"].mean().reset_index()
            fig_bar_sch = px.bar(
                avg_sch, x="meritorious_scholarship", y="current_cgpa", 
                title="Average CGPA by Scholarship Status", 
                color="meritorious_scholarship", # Color based on the category for distinct colors
                color_discrete_sequence=px.colors.qualitative.Vivid, # Use a bold, multi-color sequence
                text_auto='.2f'
            )
            fig_bar_sch.update_layout(xaxis_title='Scholarship Status', yaxis_title='Average CGPA')
            st.plotly_chart(fig_bar_sch, use_container_width=True)

        # 3. CGPA Distribution Across Income Groups (Box Plot) - Already multi-colored
        # Wrapping in columns to enforce half-width size consistency
        col3, _ = st.columns(2)
        with col3:
            st.write("**CGPA Distribution Across Income Groups**")
            fig_box_income = px.box(
                df, x="income_group", y="current_cgpa", 
                title="CGPA Distribution Across Income Groups", color="income_group",
                # This plot already uses a bold, multi-color sequence
                color_discrete_sequence=px.colors.qualitative.Vivid 
            )
            fig_box_income.update_layout(xaxis_title='Income Group', yaxis_title='CGPA')
            st.plotly_chart(fig_box_income, use_container_width=True)


    # 4. Interpretation/Discussion (Simplified English - Broken down by chart)
    st.subheader("Interpretation/Discussion")
    st.markdown(
        """
        **1. Average CGPA by Daily Social Media Usage:** This chart helps us see if too much screen time is hurting grades. If the average CGPA drops sharply for the "High" usage group, it suggests a need for better digital balance.
        
        **2. Average CGPA by Scholarship Status:** This shows whether students receiving merit-based aid perform better than those who do not. We generally expect scholarship recipients to have higher grades, confirming the merit system.
        
        **3. CGPA Distribution Across Income Groups:** The box plots let us compare the range of grades across different income groups. If the average grade is much lower for one group, it points to a need for more support or financial resources for those students.
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
        page_title="Student Performance Analysis", # Browser Tab Title
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
    st.sidebar.markdown(f"## Student Performance Analysis Dashboard - Cohort {TARGET_ADMISSION_YEAR}")
    selection = st.sidebar.radio("Go to Section", list(PAGES.keys()))
    
    # Execute the selected page function
    page = PAGES[selection]
    page(df_filtered)

if __name__ == "__main__":
    main()
