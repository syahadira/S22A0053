import streamlit as st
import pandas as pd
import requests
import altair as alt

# 🏷️ Page config
st.set_page_config(page_title="Arts Faculty Data Viewer")
st.title("📊 Arts Faculty Data Viewer")

# 🌐 Download CSV dari GitHub
url = "https://raw.githubusercontent.com/syahadira/S22A0053/main/arts_faculty_data.csv"
response = requests.get(url)

with open("arts_faculty_data.csv", "wb") as f:
    f.write(response.content)

# 📥 Baca CSV
df = pd.read_csv("arts_faculty_data.csv")

# 🖥️ Papar data
st.subheader("📄 Data Table")
st.dataframe(df.head())

# 🧮 Semak kolum Gender
column_name = "Gender"  # ubah ikut nama kolum sebenar
if column_name in df.columns:
    st.subheader("🥧 Gender Distribution (Interactive Pie Chart with Labels)")

    # Kira jumlah & peratus
    gender_counts = df[column_name].value_counts().reset_index()
    gender_counts.columns = [column_name, "Count"]
    total = gender_counts["Count"].sum()
    gender_counts["Percentage"] = (gender_counts["Count"] / total * 100).round(1).astype(str) + "%"

    # Arc (pie chart)
    pie = alt.Chart(gender_counts).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field=column_name, type="nominal", legend=alt.Legend(title=column_name)),
        tooltip=[column_name, "Count", "Percentage"]
    )

    # Label peratus atas chart
    text = pie.mark_text(radius=120, size=14).encode(
        text=alt.Text(field="Percentage", type="nominal")
    )

    # Gabungkan pie + text
    chart = (pie + text).properties(
        width=400,
        height=400,
        title="Gender Distribution in Arts Faculty"
    )

    st.altair_chart(chart, use_container_width=True)

else:
    st.warning(f"⚠️ Kolum '{column_name}' tidak dijumpai. Kolum sebenar: {list(df.columns)}")

# 📊 Info tambahan
st.write(f"Total rows: {df.shape[0]}")
st.write(f"Total columns: {df.shape[1]}")



