import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Projexions — Workflow Automation Demos",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 {
    font-family: 'Source Serif 4', serif;
}

[data-testid="stSidebar"] {
    background-color: #1B3A2F;
}
[data-testid="stSidebar"] * {
    color: #e8f0ec !important;
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #fef3c7 !important;
    font-family: 'Source Serif 4', serif;
}
[data-testid="stSidebar"] hr {
    border-color: #2d5240 !important;
}

/* Stretch column blocks so cards fill equal height */
[data-testid="stColumns"] > div {
    display: flex;
    flex-direction: column;
}
[data-testid="stColumns"] > div > [data-testid="stVerticalBlock"] {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.product-card {
    background: #fff;
    border: 1px solid #d4c9b0;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #1B3A2F;
    flex: 1;
    display: flex;
    flex-direction: column;
}
.product-card h3 {
    font-family: 'Source Serif 4', serif;
    color: #1B3A2F;
    margin-top: 0;
}
.product-card .tag {
    display: inline-block;
    background: #fef3c7;
    color: #92400e;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 12px;
    margin-bottom: 0.5rem;
}
.product-card .card-body {
    flex: 1;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Projexions")
    st.caption("Workflow Automation Demos")
    st.markdown("---")
    st.markdown("Navigate using the pages in the sidebar above.")
    st.markdown("---")
    st.caption("These are interactive demos built on realistic sample data. [projexions.net](https://projexions.net)")

st.title("Workflow Automation Demos")
st.markdown("**Three products. One Streamlit app. Real workflows, real outcomes.**")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
<div class="product-card">
<span class="tag">Product 1</span>
<h3>Reporting Automation</h3>
<div class="card-body">
<p>Monthly KPIs, revenue trends, fee breakdowns, and MoM growth — assembled automatically from raw transaction exports.</p>
<p><strong>Best for:</strong> Businesses that spend hours assembling the same monthly report from spreadsheets and accounting exports.</p>
</div>
</div>
""", unsafe_allow_html=True)
    if st.button("Open Reporting Demo →", use_container_width=True):
        st.switch_page("pages/1_Reporting.py")

with col2:
    st.markdown("""
<div class="product-card">
<span class="tag">Product 2</span>
<h3>Reconciliation Workflow</h3>
<div class="card-body">
<p>Flags unmatched payouts, disputed transactions, and fee mismatches before they become a problem.</p>
<p><strong>Best for:</strong> Ecommerce and service businesses with high transaction volume and lots of payout noise.</p>
</div>
</div>
""", unsafe_allow_html=True)
    if st.button("Open Reconciliation Demo →", use_container_width=True):
        st.switch_page("pages/2_Reconciliation.py")

with col3:
    st.markdown("""
<div class="product-card">
<span class="tag">Product 3</span>
<h3>Operations Visibility</h3>
<div class="card-body">
<p>Exception aging, owner workload, customer risk concentration, and backlog health — all in one view.</p>
<p><strong>Best for:</strong> Ops teams and agencies that know something is inefficient but can't see where the friction is.</p>
</div>
</div>
""", unsafe_allow_html=True)
    if st.button("Open Operations Demo →", use_container_width=True):
        st.switch_page("pages/3_Operations.py")

st.markdown("---")
st.markdown("""
**What these demos show:**
Each product automates a specific recurring task — monthly reporting, transaction reconciliation, or operations monitoring — and surfaces the result as a clean, readable dashboard. The buyer is not paying for software in the abstract. They are paying to eliminate a task they hate doing.

Use the sidebar to navigate between demos.
""")
