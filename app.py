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
    * **CGPA Distribution:** Rata-rata, **sebilangan besar pelajar menunjukkan prestasi yang kukuh**, dengan CGPA tertinggi berada dalam julat 3.0 hingga 3.7.
    * **Gender Distribution:** Agihan pelajar lelaki dan perempuan adalah **seimbang**.
    * **Average CGPA by Gender:** Pelajar **perempuan mempunyai purata CGPA yang sedikit lebih tinggi** berbanding pelajar lelaki.
    """) # Closing the markdown block here

    # --- Summary Box ---
    st.subheader("Summary Box")
    st.info(
        """
        **📊 Summary (Objective 1):**
        Analisis awal menunjukkan **prestasi akademik keseluruhan yang tinggi**, dengan majoriti pelajar mencapai CGPA yang baik. Taburan jantina adalah seimbang.
        Perbandingan jantina mendedahkan bahawa **pelajar perempuan mencapai purata CGPA yang sedikit lebih tinggi** daripada pelajar lelaki.
        """
    ) # Closing the info block here

# --- PAGE 2: OBJECTIVE 2 - STUDY HABITS AND PERFORMANCE ---

def page_2_study_habits():
    st.title("Objective 2: Relationship Between Study Habits and Performance 📚")
    st.markdown("---")

    df = load_and_clean_data(DATA_FILE)

    # --- Section: Objective Statement ---
    st.subheader("Objective Statement")
    st.write(
        "Untuk menyiasat bagaimana faktor disiplin akademik seperti jam belajar, kehadiran kelas, dan kekerapan ulangkaji berkolerasi dengan pencapaian akademik (CGPA)."
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
                color_discrete_sequence=px.colors.qualitative.Deep
            )
            fig_box.update_layout(xaxis_title='Attendance Category', yaxis_title='CGPA')
            st.plotly_chart(fig_box, use_container_width=True)

        # 3. Heatmap: Correlation between Study Habits and CGPA
        st.write("**Correlation Matrix of Academic Discipline Factors and CGPA**")
        correlation_cols = ['Study Hours per Day', 'Attendance_numeric', 'Study Sessions per Day', 'CGPA']
        corr_matrix = df[correlation_cols].corr()
        
        z = corr_matrix.values
        x = corr_matrix.columns.tolist()
        y = corr_matrix.index.tolist()

        fig_heatmap = ff.create_annotated_heatmap(
            z,
            x=x,
            y=y,
            annotation_text=corr_matrix.round(2).values,
            colorscale='mako',
            showscale=True
        )
        
        fig_heatmap.update_layout(
            title='Correlation Matrix of Academic Discipline Factors and CGPA',
            autosize=True,
            xaxis={'side': 'bottom'},
            margin={'t': 50, 'l': 50, 'r': 50, 'b': 50}
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

    # --- Interpretation/Discussion ---
    st.subheader("Interpretation/Discussion")
    st.markdown("""
    * **Study Hours vs. CGPA:** Terdapat **kolerasi positif** yang jelas antara bilangan jam belajar harian dengan CGPA.
    * **CGPA by Attendance:** Pelajar dalam kategori kehadiran **'High' (Tinggi) mempunyai median CGPA yang lebih tinggi** berbanding kategori lain.
    * **Correlation Matrix:** Matriks kolerasi mengesahkan bahawa **'Attendance' dan 'Study Hours per Day' mempunyai kolerasi positif terkuat dengan CGPA**.
    """)

    # --- Summary Box ---
    st.subheader("Summary Box")
    st.info(
        """
        **📊 Summary (Objective 2):**
        Keputusan secara muktamad menunjukkan bahawa **disiplin akademik adalah pemacu utama prestasi pelajar**.
        **Kehadiran kelas yang tinggi** (kolerasi kuat) dan **jumlah jam belajar yang lebih banyak** (kolerasi sederhana hingga kuat) dikaitkan secara langsung dengan CGPA yang lebih tinggi.
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
        "Untuk menilai impak faktor-faktor sosio-ekonomi dan gaya hidup bukan akademik, seperti penggunaan media sosial, status biasiswa, dan pendapatan keluarga, terhadap pencapaian akademik pelajar (CGPA)."
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
                color_discrete_sequence=px.colors.sequential.Deep,
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
        ordered_income_categories = ['Low Income (<50k)', 'Medium Income (50k-150k)', 'High Income (>150k)']

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


    # --- Interpretation/Discussion ---
    st.subheader("Interpretation/Discussion")
    st.markdown("""
    * **Social Media Usage:** Pelajar yang menggunakan media sosial secara sederhana **(1-2 jam) menunjukkan purata CGPA tertinggi**, manakala penggunaan berlebihan (>5 jam) dikaitkan dengan penurunan CGPA.
    * **Scholarship Status:** Pelajar yang mempunyai **biasiswa mempunyai taburan CGPA yang lebih tinggi** dan kurang sebaran yang rendah.
    * **Family Income:** Purata **CGPA meningkat secara beransur-ansur mengikut kenaikan kategori pendapatan keluarga**, menunjukkan peranan sokongan sosio-ekonomi.
    """)

    # --- Summary Box ---
    st.subheader("Summary Box")
    st.info(
        """
        **📊 Summary (Objective 3):**
        Faktor bukan akademik didapati mempunyai impak yang signifikan. **Penggunaan media sosial yang berlebihan adalah faktor risiko terbesar**.
        **Status biasiswa** jelas dikaitkan dengan kecemerlangan akademik, manakala **pendapatan keluarga yang lebih tinggi** menunjukkan kolerasi positif dengan purata CGPA.
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
