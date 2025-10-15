import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Scientific Visualization"
)

st.header("Genetic Algorithm", divider="gray")


# 1. Load Data
@st.cache_data # Cache the data loading for better performance
def load_data(url):
    """Loads the dataset from a URL."""
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading data from URL: {e}")
        return pd.DataFrame() # Return an empty DataFrame on failure

url = 'https://raw.githubusercontent.com/aleya566/EC2024/refs/heads/main/arts_faculty_data.csv'
arts_df = load_data(url)

# Set the title of the Streamlit app
st.title('🎨 Arts Faculty Data Analysis')

if not arts_df.empty:
    st.subheader('Raw Data Preview')
    st.dataframe(arts_df.head())

    # --- 2. Data Processing ---
    # Calculate gender counts
    if 'Gender' in arts_df.columns:
        gender_counts = arts_df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']

        st.divider()

        # --- 3. Plotly Visualizations ---
        st.header('📊 Gender Distribution')

        # 3.1. Plotly Pie Chart (replacing the Matplotlib pie chart)
        st.subheader('Gender Distribution: Pie Chart')
        fig_pie = px.pie(
            gender_counts,
            values='Count',
            names='Gender',
            title='Gender Distribution in Arts Faculty',
            hole=.3 # Optional: makes it a donut chart
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.divider()

        # 3.2. Plotly Bar Chart (replacing the Matplotlib bar chart)
        st.subheader('Gender Distribution: Bar Chart')
        fig_bar = px.bar(
            gender_counts,
            x='Gender',
            y='Count',
            title='Gender Distribution in Arts Faculty',
            labels={'Count': 'Number of Individuals'}
        )
        # Customize the bar chart appearance
        fig_bar.update_xaxes(title_text='Gender')
        fig_bar.update_yaxes(title_text='Count')

        st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.warning("The DataFrame does not contain a 'Gender' column for analysis.")
else:
    st.warning("Could not proceed with analysis because the data could not be loaded.")

# --- How to Run the App ---
st.sidebar.markdown(
    """
    *To run this app:*
    1. Save the code above as a Python file (e.g., app.py).
    2. Open your terminal and navigate to the directory where you saved the file.
    3. Run the command: streamlit run app.py
    """
)



