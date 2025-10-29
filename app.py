import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff

# --- CONSTANTS ---
DATA_FILE = "Students_Performance_data_set.csv"

# --- UTILITY FUNCTION: DATA LOADING AND CLEANING ---

@st.cache_data
def load_and_clean_data(file_path):
    """Loads, renames, cleans, and prepares the student performance data."""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='latin1')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1252')
            
    # Define a dictionary for renaming relevant columns
    column_rename_map = {
        'What is your current CGPA?': 'CGPA',
        'Gender': 'Gender',
        'How many hour do you study daily?': 'Study Hours per Day',
        'How many times do you seat for study in a day?': 'Study Sessions per Day',
        'Average attendance on class': 'Attendance',
        'How many hour do you spent daily in social media?': 'Social Media Hours',
        'Do you have meritorious scholarship ?': 'Scholarship Status',
        'What is your monthly family income?': 'Family Income'
    }

    # Rename columns if they exist
    df.rename(columns=column_rename_map, inplace=True)

    # --- Data Cleaning and Categorization ---

    # 1. Attendance: Convert to numeric and categorize (Objective 2)
    if 'Attendance' in df.columns:
        df['Attendance_numeric'] = pd.to_numeric(
            df['Attendance'].astype(str).str.replace('%', ''), errors='coerce'
        )
        if df['Attendance_numeric'].isnull().any():
            df['Attendance_numeric'].fillna(df['Attendance_numeric'].mean(), inplace=True)
            
        bins = [0, 70, 85, 100]
        labels = ['Low (<=70%)', 'Medium (71-85%)', 'High (>85%)']
        df['Attendance_Category'] = pd.cut(
            df['Attendance_numeric'], bins=bins, labels=labels, right=True, include_lowest=True
        )
        # Handle potential NaNs after cut by filling with the mode and ensuring it's a category
        df['Attendance_Category'] = df['Attendance_Category'].astype(str).replace('nan', df['Attendance_Category'].mode()[0]).astype('category')


    # 2. Social Media Hours: Categorize (Objective 3)
    if 'Social Media Hours' in df.columns and np.issubdtype(df['Social Media Hours'].dtype, np.number):
        bins = [-1, 0, 2, 5, df['Social Media Hours'].max() + 1] 
        labels = ['0 hours', '1-2 hours', '3-5 hours', '>5 hours']
        df['Social Media Category'] = pd.cut(
            df['Social Media Hours'], bins=bins, labels=labels, right=True, include_lowest=True
        )
        df['Social Media Category'] = df['Social Media Category'].astype(str).replace('nan', df['Social Media Category'].mode()[0]).astype('category')


    # 3. Family Income: Categorize (Objective 3)
    if 'Family Income' in df.columns and np.issubdtype(df['Family Income'].dtype, np.number):
        bins = [0, 50000, 150000, df['Family Income'].max() + 1]
        labels = ['Low Income (<50k)', 'Medium Income (50k-150k)', 'High Income (>150k)']
        df['Family Income Category'] = pd.cut(
            df['Family Income'], bins=bins, labels=labels, right=True, include_lowest=True
        )
        df['Family Income Category'] = df['Family Income Category'].astype(str).replace('nan', df['Family Income Category'].mode()[0]).astype('category')
        
    # 4. Fill missing values for core columns (CGPA, Gender) if any
    for col in ['CGPA', 'Gender']:
        if col in df.columns and df[col].isnull().any():
            df[col].fillna(df[col].mode()[0] if df[col].dtype == 'object' else df[col].mean(), inplace=True)

    return df

# --- PAGE 1: OBJECTIVE 1 - OVERVIEW OF STUDENT PERFORMANCE ---

def page_1_overview():
    st.title("Objective 1: Overview of Student Performance 🎓")
    st.markdown("---")

    df = load_and_clean_data(DATA_FILE)

    # --- Section: Objective Statement ---
    st.subheader("Objective Statement")
    st.write(
        "Untuk menyediakan gambaran menyeluruh tentang data prestasi pelajar dengan menganalisis taburan Gred Purata Kumulatif (CGPA) dan perbezaan prestasi akademik antara jantina."
    )

    # --- Visualizations ---
    st.subheader("Visualizations")

    if 'CGPA' in df.columns and 'Gender' in df.columns:
        col1, col2 = st.columns(2)

        # 1. CGPA Distribution (Histogram)
        with col1:
            st.write("**CGPA Distribution**")
            fig_hist = px.histogram(
                df,
                x='CGPA',
                nbins=20,
                title='Distribution of Student CGPA',
                color_discrete_sequence=['#3178C6']
            )
            fig_hist.update_layout(xaxis_title='CGPA', yaxis_title='Frequency')
            st.plotly_chart(fig_hist, use_container_width=True)

        # 2. Gender Distribution (Pie Chart)
        with col2:
            st.write("**Gender Distribution**")
            gender_counts = df['Gender'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'Count']
            fig_pie = px.pie(
                gender_counts,
                names='Gender',
                values='Count',
                title='Gender Distribution',
                color='Gender',
                color_discrete_map={'Male': '#1f77b4', 'Female': '#2ca02c'}
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        # 3. Average CGPA by Gender (Bar Chart)
        st.write("**Average CGPA by Gender**")
        average_cgpa_by_gender = df.groupby('Gender')['CGPA'].mean().reset_index().sort_values(by='CGPA', ascending=False)
        fig_bar = px.bar(
            average_cgpa_by_gender,
            x='Gender',
            y='CGPA',
            title='Average CGPA by Gender',
            color='Gender',
            color_discrete_map={'Male': '#1f77b4', 'Female': '#2ca02c'},
            text_auto='.2f'
        )
        fig_bar.update_layout(yaxis_title='Average CGPA')
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Interpretation/Discussion ---
    st.subheader("Interpretation/Discussion")
    st.markdown("""
    * **CGPA Distribution:** Rata-rata,
