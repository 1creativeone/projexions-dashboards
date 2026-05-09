import streamlit as st

st.set_page_config(
    page_title="Projexions — Workflow Automation Demos",
    page_icon="📊",
    layout="wide",
)

pg = st.navigation([
    st.Page("Home.py", title="Home", icon="🏠"),
    st.Page("pages/1_Reporting.py", title="Reporting Automation", icon="📈"),
    st.Page("pages/2_Reconciliation.py", title="Reconciliation Workflow", icon="🔍"),
    st.Page("pages/3_Operations.py", title="Operations Visibility", icon="🏗️"),
])
pg.run()
