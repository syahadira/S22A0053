import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as pximport streamlit as st
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
        # Load the dataset (try common encodings)
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
        labels = ['Low Income', 'Medium Income', 'High Income'] 
        df['Family Income Category'] = pd.cut(
            df['Family Income'], bins=bins, labels=labels, right=True, include_lowest=True
        )
        df['Family Income Category'] = df['Family Income Category'].astype(str).replace('nan', df['Family Income Category'].mode()[0]).astype('category')
        
    # 4. Fill missing values for core columns (CGPA, Gender) if any
    for col in ['CGPA', 'Gender']:
        if col in df.columns and df[col].isnull().any():
            df[col].fillna(df[col].mode()[0] if df[col].dtype == 'object' else df[col].mean(), inplace=True)

    return df

# --- PAGE 1: OBJECTIVE 1 - GENERAL OVERVIEW ---

def page_1_overview():
    st.title("Objective 1: General Overview of Student Performance 🎓")
    st.markdown("---")

    df = load_and_clean_data(DATA_FILE)

    # --- Section: Objective Statement ---
    st.subheader("Objective Statement")
    st.write(
        "To explore the overall distribution of students’ academic performance and basic demographic patterns such as gender and CGPA categories."
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

    # --- Summary Box ---
    st.subheader("Summary Box")
    st.info(
        """
        This page provides a general overview of the student population and their academic results. The visualizations show the distribution of CGPA among all students, the gender ratio, and how CGPA differs between male and female students. These visuals help identify overall academic patterns and highlight whether any performance gap exists between genders. The charts also reveal the common performance range (average to good) among most students. This overview helps understand the dataset structure and provides a foundation for deeper analysis in the next objectives.
        """
    )

# --- PAGE 2: OBJECTIVE 2 - STUDY HABITS AND PERFORMANCE ---

def page_2_study_habits():
    st.title("Objective 2: Relationship Between Study Habits and Performance 📚")
    st.markdown("---")

    df = load_and_clean_data(DATA_FILE)

    # --- Section: Objective Statement ---
    st.subheader("Objective Statement")
    st.write(
        "To examine how study habits, attendance, and daily study hours affect students’ academic performance."
    )

    # --- Visualizations ---
    st.subheader("Visualizations")

    required_cols = ['Study Hours per Day', 'CGPA', 'Attendance_Category', 'Attendance_numeric', 'Study Sessions per Day']
    if all(col in df.columns for col in required_cols):
        
        col1, col2 = st.columns(2)

        # 1. Scatter Plot: Study Hours per Day vs CGPA
        with col1:
            st.write("**Study Hours per Day vs. CGPA**")
            fig_scatter = px.scatter(
                df,
                x='Study Hours per Day',
                y='CGPA',
                title='Study Hours per Day vs. CGPA',
                opacity=0.6,
                trendline="ols",
                color_discrete_sequence=['darkgreen']
            )
            fig_scatter.update_layout(xaxis_title='Study Hours per Day', yaxis_title='CGPA')
            st.plotly_chart(fig_scatter, use_container_width=True)

        # 2. Boxplot: CGPA by Attendance Category
        with col2:
            st.write("**CGPA Distribution by Attendance Category**")
            # Explicitly set the order for the plot
            order = ['Low (<=70%)', 'Medium (71-85%)', 'High (>85%)']
            
            fig_box = px.box(
                df,
                x='Attendance_Category',
                y='CGPA',
                title='CGPA Distribution by Attendance Category',
                color='Attendance_Category',
                category_orders={'Attendance_Category': order}, # Ensure correct order
                color_discrete_sequence=px.colors.qualitative.D3 
            )
            fig_box.update_layout(xaxis_title='Attendance Category', yaxis_title='CGPA')
            st.plotly_chart(fig_box, use_container_width=True)

        # 3. Heatmap: Correlation between Study Habits and CGPA
        st.write("**Correlation Matrix of Academic Discipline Factors and CGPA**")
        correlation_cols = ['Study Hours per Day', 'Attendance_numeric', 'Study Sessions per Day', 'CGPA']
        corr_matrix = df[correlation_cols].corr()
        
        # Use Plotly Figure Factory for a visually appealing heatmap
        z = corr_matrix.values
        x = corr_matrix.columns.tolist()
        y = corr_matrix.index.tolist()

        fig_heatmap = ff.create_annotated_heatmap(
            z,
            x=x,
            y=y,
            annotation_text=corr_matrix.round(2).values,
            # FIX: Changed 'mako' (Matplotlib colormap) to 'Viridis' (standard Plotly colormap)
            colorscale='Viridis', 
            showscale=True
        )
        
        fig_heatmap.update_layout(
            title='Correlation Matrix of Academic Discipline Factors and CGPA',
            autosize=True,
            xaxis={'side': 'bottom'},
            margin={'t': 50, 'l': 50, 'r': 50, 'b': 50}
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

    # --- Summary Box ---
    st.subheader("Summary Box")
    st.info(
        """
        This page focuses on the relationship between academic discipline and results. The visualizations include a scatter plot comparing study hours and CGPA, a boxplot of attendance vs CGPA distribution, and a correlation heatmap highlighting disciplinary factors. From these visuals, students who spend more time studying and attend classes regularly tend to achieve higher grades. These patterns highlight how daily effort and attendance play a significant role in student success. The correlation matrix confirms that Attendance and Study Hours have the strongest positive links to CGPA.
        """
    )

# --- PAGE 3: OBJECTIVE 3 - IMPACT OF NON-ACADEMIC FACTORS ---

def page_3_non_academic():
    st.title("Objective 3: Impact of Non-Academic Factors on Student Performance 🌍")
    st.markdown("---")

    df = load_and_clean_data(DATA_FILE)

    # --- Section: Objective Statement ---
    st.subheader("Objective Statement")
    st.write(
        "To analyze how lifestyle factors such as social media usage, scholarship status, and family income relate to academic outcomes."
    )

    # --- Visualizations ---
    st.subheader("Visualizations")

    required_cols = ['Social Media Category', 'CGPA', 'Scholarship Status', 'Family Income Category']
    if all(col in df.columns for col in required_cols):

        col1, col2 = st.columns(2)

        # 1. Average CGPA by Social Media Usage (Bar Chart)
        with col1:
            st.write("**Average CGPA by Social Media Usage Category**")
            # Explicitly set the order for the plot
            ordered_categories = ['0 hours', '1-2 hours', '3-5 hours', '>5 hours']
            average_cgpa_by_social_media = df.groupby('Social Media Category', observed=False)['CGPA'].mean().reset_index()

            fig_bar = px.bar(
                average_cgpa_by_social_media,
                x='Social Media Category',
                y='CGPA',
                title='Average CGPA by Social Media Usage',
                color='Social Media Category',
                category_orders={'Social Media Category': ordered_categories}, # Ensure correct order
                color_discrete_sequence=px.colors.sequential.Viridis,
                text_auto='.2f'
            )
            fig_bar.update_layout(yaxis_title='Average CGPA', xaxis_title='Social Media Usage (Hours/Day)')
            st.plotly_chart(fig_bar, use_container_width=True)

        # 2. Violin Plot: CGPA by Scholarship Status
        with col2:
            st.write("**CGPA Distribution by Scholarship Status**")
            fig_violin = px.violin(
                df,
                x='Scholarship Status',
                y='CGPA',
                box=True, 
                points="all", 
                title='CGPA Distribution by Scholarship Status',
                color='Scholarship Status',
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig_violin.update_layout(xaxis_title='Scholarship Status', yaxis_title='CGPA')
            st.plotly_chart(fig_violin, use_container_width=True)
        
        # 3. Boxplot: CGPA by Family Income Category
        st.write("**CGPA Distribution by Family Income Category**")
        # Explicitly set the order for the plot
        ordered_income_categories = ['Low Income', 'Medium Income', 'High Income']

        fig_box = px.box(
            df,
            x='Family Income Category',
            y='CGPA',
            title='CGPA Distribution by Family Income Category',
            color='Family Income Category',
            category_orders={'Family Income Category': ordered_income_categories}, # Ensure correct order
            color_discrete_sequence=px.colors.qualitative.T10
        )
        fig_box.update_layout(xaxis_title='Family Income Category', yaxis_title='CGPA')
        st.plotly_chart(fig_box, use_container_width=True)


    # --- Summary Box ---
    st.subheader("Summary Box")
    st.info(
        """
        This page explores non-academic influences on student performance. The visuals include a bar chart of social media usage vs CGPA, a violin plot of scholarship status vs CGPA, and a boxplot comparing family income categories. Results show that excessive social media use tends to lower CGPA slightly, while students with moderate usage balance academics better. Scholarship holders show a tendency toward higher CGPA distributions. Family income shows a positive trend with CGPA, suggesting that financial background may provide some advantage. These findings imply that personal discipline and socio-economic support matter.
        """
    )


# --- MAIN APPLICATION LOGIC ---

def main():
    st.set_page_config(
        page_title="Student Survey Analysis",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Dictionary mapping page names (for sidebar) to their respective functions
    PAGES = {
        "Objective 1: Performance Overview 🎓": page_1_overview,
        "Objective 2: Study Habits & Performance 📚": page_2_study_habits,
        "Objective 3: Non-Academic Factors 🌍": page_3_non_academic
    }

    st.sidebar.title("Student Performance Analysis")
    st.sidebar.markdown("---")
    
    # Navigation widget
    selection = st.sidebar.radio("Go to Objective", list(PAGES.keys()))
    
    # Call the selected page function
    page = PAGES[selection]
    page()

if __name__ == "__main__":
    main()
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
