import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Arts Faculty Data Viewer")
st.title("📊 Arts Faculty Data Viewer")

# Load CSV dari GitHub
url = "https://raw.githubusercontent.com/syahadira/S22A0053/main/arts_faculty_data.csv"
response = requests.get(url)

with open("arts_faculty_data.csv", "wb") as f:
    f.write(response.content)

df = pd.read_csv("arts_faculty_data.csv")

# Semak CSV
st.write("📌 Columns:", df.columns)
if df.empty:
    st.error("❌ CSV file kosong atau gagal dibaca!")
else:
    st.success("✅ CSV file berjaya dibaca")

st.subheader("📄 Data Table")
st.dataframe(df.head())

# PIE CHART
column_name = "Gender"  # ubah ikut nama sebenar kolum
if column_name in df.columns:
    st.subheader("🥧 Gender Distribution Pie Chart")
    gender_counts = df[column_name].value_counts()

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        gender_counts,
        labels=gender_counts.index,
        autopct="%1.1f%%",
        startangle=140
    )
    ax.set_title("Gender Distribution in Arts Faculty")
    ax.axis("equal")

    st.pyplot(fig)
else:
    st.warning(f"⚠️ Kolum '{column_name}' tidak dijumpai. Kolum sebenar: {list(df.columns)}")

st.write(f"Total rows: {df.shape[0]}")
st.write(f"Total columns: {df.shape[1]}")

