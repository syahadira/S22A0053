import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

# --- Configuration and Data Loading ---
st.set_page_config(layout="wide", page_title="Arts Faculty Data Analysis")

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

def plot_gender_distribution(df):
    """Creates an interactive Pie Chart for Gender Distribution."""
    gender_counts = df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig = px.pie(
        gender_counts,
        values='Count',
        names='Gender',
        title='**Gender Distribution in Arts Faculty**',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def plot_arts_program_distribution(df):
    """Creates an interactive Bar Chart for Arts Program Enrollment."""
    fig = px.histogram(
        df,
        x='Arts Program',
        title='**Distribution of Arts Programs**',
        labels={'Arts Program': 'Arts Program', 'count': 'Count'},
        color_discrete_sequence=['#4C78A8']
    )
    fig.update_xaxes(tickangle=45)
    return fig

def plot_gpa_histogram(df, column_name):
    """Creates an interactive Histogram for GPA distribution."""
    fig = px.histogram(
        df,
        x=column_name,
        nbins=20,
        marginal="box", # Adds a box plot for summary statistics
        title=f'**Distribution of {column_name}**',
        color_discrete_sequence=['#F58518']
    )
    fig.update_layout(xaxis_title=column_name, yaxis_title='Frequency')
    return fig

def plot_class_modality(df, hue=None):
    """Creates an interactive Bar Chart for Class Modality."""
    if hue:
        title = '**Distribution of Class Modality by Gender**'
        barmode = 'group'
        df_plot = df.groupby(['Classes are mostly', hue]).size().reset_index(name='Count')
        fig = px.bar(
            df_plot,
            x='Classes are mostly',
            y='Count',
            color=hue,
            barmode=barmode,
            title=title,
            labels={'Classes are mostly': 'Class Modality'}
        )
    else:
        title = '**Overall Distribution of Class Modality**'
        fig = px.histogram(
            df,
            x='Classes are mostly',
            title=title,
            color_discrete_sequence=['#5BA04F']
        )

    fig.update_xaxes(tickangle=45)
    return fig

# --- Layout and Plotting ---

# Section 1: Demographics and Enrollment
st.header("1. Gender and Program Enrollment")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_gender_distribution(arts_faculty_df), use_container_width=True)
with col2:
    st.plotly_chart(plot_arts_program_distribution(arts_faculty_df), use_container_width=True)

st.markdown("---")

# Section 2: Academic Performance
st.header("2. Academic Performance (GPA)")
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(plot_gpa_histogram(arts_faculty_df, 'S.S.C (GPA)'), use_container_width=True)
with col4:
    st.plotly_chart(plot_gpa_histogram(arts_faculty_df, 'H.S.C (GPA)'), use_container_width=True)

st.markdown("---")

# Section 3: Class Modality
st.header("3. Class Modality and Gender Preference")
st.plotly_chart(plot_class_modality(arts_faculty_df, hue='Gender'), use_container_width=True)
st.plotly_chart(plot_class_modality(arts_faculty_df), use_container_width=True)


