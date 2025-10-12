import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# 🏷️ Page config
st.set_page_config(page_title="Arts Faculty Data Viewer")
st.title("📊 Arts Faculty Data Viewer")

# 🌐 Download CSV dari GitHub
url = "https://raw.githubusercontent.com/syahadira/S22A0053/refs/heads/main/arts_faculty_data.csv"
response = requests.get(url)

with open("arts_faculty_data.csv", "wb") as f:
    f.write(response.content)

# 📥 Baca CSV
df = pd.read_csv("arts_faculty_data.csv")

# 🖥️ Papar data
st.subheader("📄 Data Table")
st.dataframe(df.head())

# 🧮 Semak kalau kolum "Gender" wujud
if "Gender" in df.columns:
    st.subheader("🥧 Gender Distribution Pie Chart")

    # Kira jumlah setiap gender
    gender_counts = df["Gender"].value_counts()

    # Buat figure pie chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        gender_counts,
        labels=gender_counts.index,
        autopct="%1.1f%%",
        startangle=140
    )
    ax.set_title("Gender Distribution in Arts Faculty")
    ax.axis("equal")  # supaya pie chart jadi bulat

    # Papar graf dalam Streamlit
    st.pyplot(fig)
else:
    st.warning("⚠️ Kolum 'Gender' tidak dijumpai dalam CSV kamu.")

# 📊 Tambahan info
st.write(f"Total rows: {df.shape[0]}")
st.write(f"Total columns: {df.shape[1]}")
