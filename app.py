import streamlit as st

st.set_page_config(
    page_title="Student Survey"
)

visualise = st.Page('tutorial3.py', title='Pencapaian Akademik Pelajar', icon=":material/school:")

home = st.Page('home.py', title='Homepage', default=True, icon=":material/home:")

pg = st.navigation(
        {
            "Menu": [home, visualise]
        }
    )

pg.run()
