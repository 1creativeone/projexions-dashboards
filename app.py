import streamlit as st

st.set_page_config(
    page_title="Projexions — Workflow Automation Demos",
    page_icon="📊",
    layout="wide",
)

pg = st.navigation([
    st.Page("Home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/1_Reporting.py", title="Reporting Automation", icon="📈", url_path="Reporting_Automation"),
    st.Page("pages/2_Reconciliation.py", title="Reconciliation Workflow", icon="🔍", url_path="Reconciliation_Workflow"),
    st.Page("pages/3_Operations.py", title="Operations Visibility", icon="🏗️", url_path="Operations_Visibility"),
])
pg.run()
