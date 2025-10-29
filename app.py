import streamlit as st

st.set_page_config(
    page_title="Student Performance"
)

visualise = st.Page('StudentPerformance.py', title='Student Performance', icon=":material/school:")

home = st.Page('StudentPerformance.py', title='Homepage', default=True, icon=":material/home:")

pg = st.navigation(
        {
            "Menu": [home, visualise]
        }
    )

pg.run()

col1, col2, col3, col4 = st.columns(4)
 
col1.metric(
    label="PLO 2",
    value="3.17",
    help="PLO 2: Cognitive Skill (Average CGPA)",
    delta="Based on average student performance",
    delta_color="normal"
)

col2.metric(
    label="PLO 3",
    value="91.7%",
    help="PLO 3: Digital Skill (Percentage of students with personal PC)",
    delta="High digital access among students",
    delta_color="normal"
)

col3.metric(
    label="PLO 4",
    value="55.2%",
    help="PLO 4: Interpersonal Skill (Percentage of students who attend teacher consultancy)",
    delta="Moderate engagement with teachers",
    delta_color="normal"
)

col4.metric(
    label="PLO 5",
    value="1.93",
    help="PLO 5: Communication Skill (Average English Proficiency Score (1=Basic, 3=Advance))",
    delta="Intermediate proficiency level",
    delta_color="normal"
)
