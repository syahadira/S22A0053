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
    """Loads, renames, cleans, and prepares the student performance data for all objectives."""
    try:
        # Load the dataset (try common encodings)
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='latin1')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1252')
            
    # Define a dictionary for renaming relevant columns (for Objectives AND PLOs)
    column_rename_map = {
        'What is your current CGPA?': 'CGPA',
        'Gender': 'Gender',
        'How many hour do you study daily?': 'Study Hours per Day',
        'How many times do you seat for study in a day?': 'Study Sessions per Day',
        'Average attendance on class': 'Attendance',
        'How many hour do you spent daily in social media?': 'Social Media Hours',
        'Do you have meritorious scholarship ?': 'Scholarship Status',
        'What is your monthly family income?': 'Family Income',
        'Do you have personal Computer?': 'PC Status',
        'Do you attend in teacher consultancy for any kind of academical problems?': 'Consultancy Status',
        'Status of your English language proficiency': 'English Proficiency'
    }

    # Rename columns if they exist
    df.rename(columns=column_rename_map, inplace=True)
    
    # Ensure CGPA is numeric
    df['CGPA'] = pd.to_numeric(df['CGPA'], errors='coerce')

    # --- Data Cleaning and Categorization for Objectives ---

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
        # Handle potential NaNs after cut
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
        labels = ['Low Income', 'Medium Income', 'High Income'] 
        df['Family Income Category'] = pd.cut(
            df['Family Income'], bins=bins, labels=labels, right=True, include_lowest=True
        )
        df['Family Income Category'] = df['Family Income Category'].astype(str).replace('nan', df['Family Income Category'].mode()[0]).astype('category')
        
    # 4. Fill missing values for core columns
    for col in ['CGPA', 'Gender']:
        if col in df.columns and df[col].isnull().any():
            df[col].fillna(df[col].mode()[0] if df[col].dtype == 'object' else df[col].mean(), inplace=True)

    return df

# --- PLO Metric Calculation Function ---

def calculate_plo_metrics(df):
    """Calculates the PLO metric values."""
    
    # 1. PLO 2: Cognitive Skill (Mean CGPA)
    plo2_value = df['CGPA'].mean()

    # 2. PLO 3: Digital Skill (PC Ownership Percentage)
    if 'PC Status' in df.columns:
        df['PC Status_Binary'] = df['PC Status'].astype(str).str.
