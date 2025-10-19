
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

# --- Configuration and Data Loading ---
st.set_page_config(layout="wide", page_title="Arts Faculty Data Analysis (with Insights)")

# Data source URL
URL = "https://raw.githubusercontent.com/syahadira/S22A0053/refs/heads/main/arts_faculty_data.csv"

@st.cache_data
def load_data(url):
    """Fetches and caches the data from the GitHub URL."""
    try:
        response = requests.get(url)
        response.raise_for_status() # Check for request errors
        data = pd.read_csv(StringIO(response.text))
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame() # Return an empty DataFrame on error

arts_faculty_df = load_data(URL)

# Check if data was loaded successfully
if arts_faculty_df.empty:
    st.stop()

# --- Streamlit Title and Overview ---
st.title("Arts Faculty Data Analysis 🎨")
st.write("A visual exploration of student demographics, academic performance, and class modality preferences.")
st.subheader("Raw Data Preview")
st.dataframe(arts_faculty_df.head(), use_container_width=True)

st.markdown("---")

# --- Visualization Functions (using Plotly Express) ---

# 1. Gender Distribution (Pie Chart)
def plot_gender_pie(df):
    """Creates an interactive Pie Chart for Gender Distribution."""
    gender_counts = df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig = px.pie(
        gender_counts,
        values='Count',
        names='Gender',
        title='1. Gender Distribution (Pie Chart)',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

# 2. Gender Distribution (Bar Chart)
def plot_gender_bar(df):
    """Creates an interactive Bar Chart for Gender Distribution."""
    gender_counts = df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig = px.bar(
        gender_counts,
        x='Gender',
        y='Count',
        title='2. Gender Distribution (Bar Chart)',
        color='Gender',
        color_discrete_sequence=['#A84C4C', '#4C78A8']
    )
    fig.update_layout(showlegend=False)
    return fig

# 3. Arts Program Distribution
def plot_arts_program_distribution(df):
    """Creates an interactive Bar Chart for Arts Program Enrollment."""
    fig = px.histogram(
        df,
        x='Arts Program',
        title='3. Distribution of Arts Programs',
        labels={'Arts Program': 'Arts Program', 'count': 'Count'},
        color_discrete_sequence=['#4C78A8']
    )
    fig.update_xaxes(tickangle=45)
    return fig

# 4. & 5. GPA Distributions (Histograms)
def plot_gpa_histogram(df, column_name, plot_number):
    """Creates an interactive Histogram for GPA distribution."""
    fig = px.histogram(
        df,
        x=column_name,
        nbins=20,
        marginal="box", # Adds a box plot for summary statistics
        title=f'{plot_number}. Distribution of {column_name}',
        color_discrete_sequence=['#F58518']
    )
    fig.update_layout(xaxis_title=column_name, yaxis_title='Frequency')
    return fig

# 6. Modality by Gender
def plot_modality_by_gender(df):
    """Creates an interactive Grouped Bar Chart for Class Modality by Gender."""
    df_plot = df.groupby(['Classes are mostly', 'Gender']).size().reset_index(name='Count')
    fig = px.bar(
        df_plot,
        x='Classes are mostly',
        y='Count',
        color='Gender',
        barmode='group',
        title='6. Distribution of Class Modality by Gender',
        labels={'Classes are mostly': 'Class Modality'}
    )
    fig.update_xaxes(tickangle=45)
    return fig

# 7. Overall Modality Distribution
def plot_overall_modality(df):
    """Creates an interactive Histogram for Overall Class Modality."""
    fig = px.histogram(
        df,
        x='Classes are mostly',
        title='7. Overall Distribution of Class Modality',
        color_discrete_sequence=['#5BA04F']
    )
    fig.update_xaxes(tickangle=45)
    return fig


# --- Layout and Plotting (7 Separated Visualizations with Insights) ---

# Removed st.header("1. Gender Demographics")
col_pie, col_bar = st.columns(2)
with col_pie:
    st.plotly_chart(plot_gender_pie(arts_faculty_df), use_container_width=True)
    st.markdown("""
        **Insight (1):** The pie chart clearly shows a **gender imbalance**, with a much higher percentage of students being **female**. This is typical for many Arts and Humanities faculties. It means the university should design student services and campus facilities to meet the needs of the larger female student population.
    """)
with col_bar:
    st.plotly_chart(plot_gender_bar(arts_faculty_df), use_container_width=True)
    st.markdown("""
        **Insight (2):** This bar chart confirms the **large numerical difference** between male and female students. For every male student, there are roughly two female students enrolled. This highlights the need to understand why male enrollment is lower and potentially develop strategies to balance the distribution.
    """)

st.markdown("---")

# Removed st.header("2. Program Enrollment")
st.plotly_chart(plot_arts_program_distribution(arts_faculty_df), use_container_width=True)
st.markdown("""
    **Insight (3):** The bar chart reveals the **popularity of different Arts programs**. Some programs have significantly higher student counts than others, leading to an unequal workload across departments. This information is vital for the faculty when deciding where to allocate teaching staff and classroom space.
""")

st.markdown("---")

# Removed st.header("3. Academic Performance (GPA)")
col_ssc, col_hsc = st.columns(2)
with col_ssc:
    st.plotly_chart(plot_gpa_histogram(arts_faculty_df, 'S.S.C (GPA)', '4'), use_container_width=True)
    st.markdown("""
        **Insight (4):** The S.S.C GPA distribution is **skewed towards the higher grades** (likely 4.0 and 5.0). This shows that most students entering the faculty have a **strong academic foundation** from their initial secondary school years. The school is generally admitting high-achieving applicants.
    """)
with col_hsc:
    st.plotly_chart(plot_gpa_histogram(arts_faculty_df, 'H.S.C (GPA)', '5'), use_container_width=True)
    st.markdown("""
        **Insight (5):** The H.S.C GPA distribution is also heavily concentrated at the **high end of the scale**. This pattern confirms that the student body maintained **excellent grades** throughout their senior high school years. The faculty has a pool of students well-prepared for university-level coursework.
    """)

st.markdown("---")

# Removed st.header("4. Class Modality Preferences")
col_gender_modality, col_overall_modality = st.columns(2)
with col_gender_modality:
    st.plotly_chart(plot_modality_by_gender(arts_faculty_df), use_container_width=True)
    st.markdown("""
        **Insight (6):** This chart compares class preference by gender. It shows if **females and males prefer different learning styles** (Online, Offline, or Hybrid). This helps the faculty understand if specific course formats are favored by one gender, which can affect student participation and performance.
    """)
with col_overall_modality:
    st.plotly_chart(plot_overall_modality(arts_faculty_df), use_container_width=True)
    st.markdown("""
        **Insight (7):** This overall chart clearly identifies the **most popular class modality** among all students. The highest bar indicates the teaching method most widely used or preferred. This allows administrators to focus resources and training on the dominant mode of instruction.
    """)
