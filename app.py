import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Arts Faculty Data Viewer")
st.title("📊 Arts Faculty Data Viewer")

url = "https://raw.githubusercontent.com/syahadira/S22A0053/refs/heads/main/arts_faculty_data.csv"
response = requests.get(url)

with open("arts_faculty_data.csv", "wb") as f:
    f.write(response.content)

arts_faculty_df_from_github = pd.read_csv("arts_faculty_data.csv")

st.subheader("Preview of Data")
st.dataframe(arts_faculty_df_from_github.head())

st.write(f"Total rows: {arts_faculty_df_from_github.shape[0]}")
st.write(f"Total columns: {arts_faculty_df_from_github.shape[1]}")
