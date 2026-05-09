import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Operations Visibility — Projexions", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Source Serif 4', serif; }
[data-testid="stSidebar"] { background-color: #1B3A2F; }
[data-testid="stSidebar"] * { color: #e8f0ec !important; }
[data-testid="stSidebar"] .stMarkdown h3 { color: #fef3c7 !important; font-family: 'Source Serif 4', serif; }
[data-testid="stSidebar"] hr { border-color: #2d5240 !important; }
.metric-card {
    background: #fff;
    border: 1px solid #d4c9b0;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    text-align: center;
}
.metric-card .label { font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
.metric-card .value { font-size: 2rem; font-weight: 700; color: #1B3A2F; font-family: 'Source Serif 4', serif; line-height: 1.2; }
.metric-card.alert .value { color: #dc2626; }
.metric-card.warn .value { color: #d97706; }
.section-header { font-family: 'Source Serif 4', serif; color: #1B3A2F; border-bottom: 2px solid #d97706; padding-bottom: 4px; margin-top: 2rem; margin-bottom: 1rem; }
.risk-high { color: #dc2626; font-weight: 700; }
.risk-medium { color: #d97706; font-weight: 700; }
.risk-low { color: #059669; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Projexions")
    st.caption("Operations Visibility Demo")
    st.markdown("---")
    st.markdown("**Product 3 of 3**")
    st.markdown("This demo shows workload distribution, exception aging by owner, and customer risk concentration — the friction that ops teams can rarely see clearly.")
    st.markdown("---")
    owner_filter = st.multiselect(
        "Filter by owner",
        options=["Finance", "Ops Team", "Account Manager", "Risk Team", "Compliance"],
        default=["Finance", "Ops Team", "Account Manager", "Risk Team", "Compliance"],
    )
    st.markdown("---")
    st.caption("[projexions.net](https://projexions.net)")

@st.cache_data
def load_data():
    exc = pd.read_csv("data/exceptions.csv")
    exc["detected_date"] = pd.to_datetime(exc["detected_date"], format="mixed")

    cust = pd.read_csv("data/customers.csv")
    risk = pd.read_csv("data/customer_risk_summary.csv")
    risk_merged = risk.merge(cust[["customer_id", "industry", "segment", "region"]], on="customer_id", how="left")
    return exc, cust, risk_merged

exc, cust, risk = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Operations Visibility")
st.markdown("Workload concentration, exception backlogs, and customer risk exposure — in one view.")
st.markdown("---")

# ── KPI Strip ────────────────────────────────────────────────────────────────
open_exc = exc[exc["status"] == "open"]
escalated_exc = exc[exc["status"] == "escalated"]
avg_days_open = open_exc["days_open"].mean() if len(open_exc) > 0 else 0
high_risk_customers = (risk["risk_level"] == "high").sum()
total_exceptions = len(exc)

c1, c2, c3, c4 = st.columns(4)
metrics = [
    (c1, "Open Exceptions", f"{len(open_exc):,}", "alert" if len(open_exc) > 30 else ""),
    (c2, "Escalated", f"{len(escalated_exc):,}", "warn" if len(escalated_exc) > 0 else ""),
    (c3, "Avg Days Open", f"{avg_days_open:.0f}d", "warn" if avg_days_open > 14 else ""),
    (c4, "High Risk Customers", f"{high_risk_customers}", "alert" if high_risk_customers > 5 else ""),
]
for col, label, value, css_cls in metrics:
    with col:
        st.markdown(f"""
<div class="metric-card {css_cls}">
<div class="label">{label}</div>
<div class="value">{value}</div>
</div>""", unsafe_allow_html=True)

# ── Workload by Owner ─────────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">Workload by Owner</h3>', unsafe_allow_html=True)

exc_owner = exc[exc["owner"].isin(owner_filter)] if owner_filter else exc

col_w1, col_w2 = st.columns(2)

with col_w1:
    open_by_owner = exc_owner[exc_owner["status"] != "resolved"].groupby(["owner", "severity"]).size().reset_index(name="Count")
    color_map = {"high": "#dc2626", "medium": "#d97706", "low": "#059669"}
    fig_owner = px.bar(
        open_by_owner, x="Count", y="owner", color="severity",
        color_discrete_map=color_map, orientation="h",
        labels={"owner": "", "Count": "Open Exceptions", "severity": "Severity"},
        barmode="stack",
    )
    fig_owner.update_layout(template="plotly_white", height=280, margin=dict(t=10, b=20, l=0, r=0),
                             legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_owner, use_container_width=True)
    st.caption("Open exception count per owner, stacked by severity")

with col_w2:
    avg_aging = exc_owner[exc_owner["status"] != "resolved"].groupby("owner")["days_open"].mean().reset_index()
    avg_aging.columns = ["Owner", "Avg Days Open"]
    avg_aging = avg_aging.sort_values("Avg Days Open", ascending=True)
    fig_aging = px.bar(
        avg_aging, x="Avg Days Open", y="Owner", orientation="h",
        color_discrete_sequence=["#1B3A2F"],
        labels={"Avg Days Open": "Avg Days Open", "Owner": ""},
    )
    fig_aging.update_layout(template="plotly_white", height=280, margin=dict(t=10, b=20, l=0, r=0))
    st.plotly_chart(fig_aging, use_container_width=True)
    st.caption("Average open duration by owner — higher = backlog risk")

# ── Exception Type Distribution ───────────────────────────────────────────────
st.markdown('<h3 class="section-header">Exception Patterns</h3>', unsafe_allow_html=True)

col_type, col_trend = st.columns(2)

with col_type:
    sev_type = exc_owner.groupby(["exception_type", "severity"]).size().reset_index(name="Count")
    color_map = {"high": "#dc2626", "medium": "#d97706", "low": "#059669"}
    fig_sev = px.bar(
        sev_type, x="exception_type", y="Count", color="severity",
        color_discrete_map=color_map, barmode="group",
        labels={"exception_type": "", "Count": "Exceptions", "severity": "Severity"},
    )
    fig_sev.update_layout(template="plotly_white", height=260, margin=dict(t=10, b=20, l=0, r=0),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02),
                           xaxis=dict(tickangle=-20))
    st.plotly_chart(fig_sev, use_container_width=True)
    st.caption("Exception type breakdown by severity")

with col_trend:
    exc_owner_copy = exc_owner.copy()
    exc_owner_copy["detected_month"] = exc_owner_copy["detected_date"].dt.to_period("M").astype(str)
    monthly_exc = exc_owner_copy.groupby(["detected_month", "status"]).size().reset_index(name="Count")
    status_color_map = {"open": "#d97706", "resolved": "#1B3A2F", "escalated": "#dc2626"}
    fig_trend = px.line(
        monthly_exc, x="detected_month", y="Count", color="status",
        color_discrete_map=status_color_map,
        labels={"detected_month": "", "Count": "Exceptions", "status": "Status"},
        markers=True,
    )
    fig_trend.update_layout(template="plotly_white", height=260, margin=dict(t=10, b=20, l=0, r=0),
                             legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_trend, use_container_width=True)
    st.caption("Exception trend by month and resolution status")

# ── Customer Risk Concentration ────────────────────────────────────────────────
st.markdown('<h3 class="section-header">Customer Risk Concentration</h3>', unsafe_allow_html=True)

col_r1, col_r2 = st.columns(2)

with col_r1:
    risk_counts = risk.groupby("risk_level").size().reset_index(name="Customer Count")
    risk_color = {"high": "#dc2626", "medium": "#d97706", "low": "#059669"}
    fig_risk = px.pie(
        risk_counts, names="risk_level", values="Customer Count",
        color="risk_level", color_discrete_map=risk_color,
        hole=0.4,
    )
    fig_risk.update_layout(template="plotly_white", height=260, margin=dict(t=10, b=30, l=0, r=0),
                            legend=dict(orientation="h", yanchor="top", y=-0.1))
    st.plotly_chart(fig_risk, use_container_width=True)
    st.caption("Customer distribution by risk level")

with col_r2:
    exc_count = risk.groupby("risk_level")["exception_count"].sum().reset_index()
    exc_count.columns = ["Risk Level", "Total Exceptions"]
    fig_exc_risk = px.bar(
        exc_count, x="Risk Level", y="Total Exceptions",
        color="Risk Level", color_discrete_map=risk_color,
        labels={"Risk Level": "", "Total Exceptions": "Total Exceptions"},
    )
    fig_exc_risk.update_layout(template="plotly_white", height=260, margin=dict(t=10, b=20, l=0, r=0),
                                showlegend=False)
    st.plotly_chart(fig_exc_risk, use_container_width=True)
    st.caption("Exception volume concentrated in high-risk segment")

# ── Customer Risk Table ────────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">Customer Risk Register</h3>', unsafe_allow_html=True)

risk_filter = st.selectbox("Show risk level", ["All", "high", "medium", "low"], index=0)
risk_display = risk.copy() if risk_filter == "All" else risk[risk["risk_level"] == risk_filter].copy()
risk_display = risk_display.sort_values(["risk_level", "exception_count"], ascending=[True, False])

display_cols = ["customer_id", "business_name", "risk_level", "monthly_volume_band", "exception_count", "industry", "segment", "region"]
display_cols = [c for c in display_cols if c in risk_display.columns]
risk_out = risk_display[display_cols].copy()
risk_out.columns = [c.replace("_", " ").title() for c in display_cols]

st.dataframe(risk_out.reset_index(drop=True), use_container_width=True, height=320)

# ── Volume Band vs Exception Count Scatter ─────────────────────────────────────
with st.expander("Volume vs exception scatter"):
    vol_order = {"$0-$10k": 0, "$10k-$50k": 1, "$50k-$100k": 2, "$100k-$500k": 3, "$500k-$1M": 4, "$1M+": 5}
    risk_plot = risk.copy()
    risk_plot["vol_rank"] = risk_plot["monthly_volume_band"].map(vol_order).fillna(0)
    fig_scatter = px.scatter(
        risk_plot, x="vol_rank", y="exception_count",
        color="risk_level", color_discrete_map=risk_color,
        hover_data={"business_name": True, "monthly_volume_band": True, "vol_rank": False},
        labels={"vol_rank": "Monthly Volume Band", "exception_count": "Exception Count", "risk_level": "Risk"},
        size_max=14,
    )
    tick_labels = {v: k for k, v in vol_order.items()}
    fig_scatter.update_layout(
        template="plotly_white",
        height=320,
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis=dict(tickvals=list(tick_labels.keys()), ticktext=list(tick_labels.values()), tickangle=-20),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("High-volume customers with high exception counts need account review")
