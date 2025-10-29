import streamlit as st
import pandas as pd
import numpy as np

# --- CONSTANTS ---
DATA_FILE = "Students_Performance_data_set.csv"

# --- UTILITY FUNCTION: DATA LOADING AND CLEANING ---

# Cache the data loading for better performance
@st.cache_data
def load_and_clean_data(file_path):
    """Loads, renames, cleans, and prepares the core student data."""
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
        'Do you have personal Computer?': 'PC Status',
        'Do you attend in teacher consultancy for any kind of academical problems?': 'Consultancy Status',
        'Status of your English language proficiency': 'English Proficiency'
    }
    df.rename(columns=column_rename_map, inplace=True)
    
    # Ensure CGPA is numeric
    df['CGPA'] = pd.to_numeric(df['CGPA'], errors='coerce')
    
    return df

# --- PLO Metric Calculation Function ---

def calculate_plo_metrics(df):
    """Calculates the PLO metric values."""
    
    # 1. PLO 2: Cognitive Skill (Mean CGPA)
    plo2_value = df['CGPA'].mean()

    # 2. PLO 3: Digital Skill (PC Ownership Percentage)
    if 'PC Status' in df.columns:
        df['PC Status_Binary'] = df['PC Status'].astype(str).str.lower().map({'yes': 1, 'no': 0})
        plo3_value = df['PC Status_Binary'].mean() * 100
    else:
        plo3_value = np.nan 

    # 3. PLO 4: Interpersonal Skill (Consultancy Attendance Percentage)
    if 'Consultancy Status' in df.columns:
        df['Consultancy Status_Binary'] = df['Consultancy Status'].astype(str).str.lower().map({'yes': 1, 'no': 0})
        plo4_value = df['Consultancy Status_Binary'].mean() * 100
    else:
        plo4_value = np.nan

    # 4. PLO 5: Communication Skill (Average English Proficiency Score)
    proficiency_map = {'basic': 1, 'intermediate': 2, 'advance': 3, 'advanced': 3}
    if 'English Proficiency' in df.columns:
        df['English Proficiency_Score'] = df['English Proficiency'].astype(str).str.lower().map(proficiency_map)
        plo5_value = df['English Proficiency_Score'].mean()
    else:
        plo5_value = np.nan

    # --- Final Formatting ---
    plo2_formatted = f"{plo2_value:.2f}" if not np.isnan(plo2_value) else "N/A"
    plo3_formatted = f"{plo3_value:.1f}%" if not np.isnan(plo3_value) else "N/A"
    plo4_formatted = f"{plo4_value:.1f}%" if not np.isnan(plo4_value) else "N/A"
    plo5_formatted = f"{plo5_value:.2f}" if not np.isnan(plo5_value) else "N/A"
    
    return plo2_formatted, plo3_formatted, plo4_formatted, plo5_formatted

# --- MAIN HOMEPAGE LOGIC ---

def main():
    # Load and clean data
    df = load_and_clean_data(DATA_FILE)
    
    # Calculate PLO metrics
    plo2_val, plo3_val, plo4_val, plo5_val = calculate_plo_metrics(df)
    
    st.set_page_config(
        page_title="Student Performance Dashboard", 
        layout="wide"
    )

    # --- Homepage Content ---
    st.title("📊 Student Performance Analysis Dashboard")
    st.markdown("This homepage summarizes the status of key Program Learning Outcomes (PLOs) based on student survey data.")
    st.subheader("Program Learning Outcomes (PLOs) Status")

    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        label="PLO 2",
        value=plo2_val,
        help="PLO 2: Cognitive Skill (Average CGPA: Target is typically 3.0)",
        delta="Average CGPA",
        delta_color="normal"
    )
    col2.metric(
        label="PLO 3",
        value=plo3_val,
        help="PLO 3: Digital Skill (Percentage of students with personal PC)",
        delta="PC Ownership %",
        delta_color="normal"
    )
    col3.metric(
        label="PLO 4",
        value=plo4_val,
        help="PLO 4: Interpersonal Skill (Percentage of students who attend teacher consultancy)",
        delta="Consultancy Attendance %",
        delta_color="normal"
    )
    col4.metric(
        label="PLO 5",
        value=plo5_val,
        help="PLO 5: Communication Skill (Average English Proficiency Score: 1=Basic, 3=Advance)",
        delta="Avg. English Proficiency Score",
        delta_color="normal"
    )

if __name__ == "__main__":
    main()
