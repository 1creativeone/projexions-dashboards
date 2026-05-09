import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Reconciliation Workflow — Projexions", page_icon="🔍", layout="wide")

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
.flag-badge { display: inline-block; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; }
.flag-high { background: #fee2e2; color: #991b1b; }
.flag-medium { background: #fef3c7; color: #92400e; }
.flag-low { background: #d1fae5; color: #065f46; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Projexions")
    st.caption("Reconciliation Workflow Demo")
    st.markdown("---")
    st.markdown("**Product 2 of 3**")
    st.markdown("This demo shows how payout mismatches, refund disputes, and fee exceptions are surfaced automatically — before they become a problem.")
    st.markdown("---")
    severity_filter = st.multiselect("Filter by severity", ["high", "medium", "low"], default=["high", "medium", "low"])
    status_filter = st.multiselect("Filter by status", ["open", "resolved", "escalated"], default=["open", "escalated"])
    st.markdown("---")
    st.caption("[projexions.net](https://projexions.net)")

@st.cache_data
def load_data():
    txn = pd.read_csv("data/transactions.csv")
    txn["transaction_date"] = pd.to_datetime(txn["transaction_date"], format="mixed")
    txn["month"] = txn["transaction_date"].dt.to_period("M").astype(str)

    exc = pd.read_csv("data/exceptions.csv")
    exc["detected_date"] = pd.to_datetime(exc["detected_date"], format="mixed")
    exc["detected_month"] = exc["detected_date"].dt.to_period("M").astype(str)
    return txn, exc

txn, exc = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Reconciliation Workflow")
st.markdown("Payout status mismatches, exception flags, and fee anomalies — surfaced automatically.")
st.markdown("---")

# ── KPI Strip ────────────────────────────────────────────────────────────────
total_txn = len(txn)
pending_payouts = (txn["payout_status"] == "pending").sum()
failed_payouts = (txn["payout_status"] == "failed").sum()
open_exc = exc[exc["status"] == "open"]
high_exc = exc[(exc["status"] != "resolved") & (exc["severity"] == "high")]
pending_value = txn[txn["payout_status"] == "pending"]["net_amount"].sum()

c1, c2, c3, c4 = st.columns(4)
metrics = [
    (c1, "Total Transactions", f"{total_txn:,}", "", ""),
    (c2, "Pending Payouts", f"{pending_payouts:,}", "alert", f"${pending_value:,.0f} held"),
    (c3, "Failed Payouts", f"{failed_payouts:,}", "alert" if failed_payouts > 0 else "", ""),
    (c4, "Open High Exceptions", f"{len(high_exc):,}", "alert" if len(high_exc) > 0 else "", ""),
]
for col, label, value, css_cls, sub in metrics:
    with col:
        sub_html = f'<div style="font-size:0.8rem;color:#6b7280;margin-top:4px">{sub}</div>' if sub else ""
        st.markdown(f"""
<div class="metric-card {css_cls}">
<div class="label">{label}</div>
<div class="value">{value}</div>
{sub_html}
</div>""", unsafe_allow_html=True)

# ── Payout Status Breakdown ───────────────────────────────────────────────────
st.markdown('<h3 class="section-header">Payout Status Breakdown</h3>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    payout_summary = txn.groupby("payout_status").agg(
        count=("transaction_id", "count"),
        net_amount=("net_amount", "sum")
    ).reset_index()
    payout_summary.columns = ["Status", "Count", "Net Amount ($)"]
    color_map = {"paid_out": "#1B3A2F", "pending": "#d97706", "failed": "#dc2626", "processing": "#6b7280"}
    fig_ps = px.bar(
        payout_summary, x="Status", y="Count",
        color="Status", color_discrete_map=color_map,
        labels={"Count": "Transactions", "Status": ""},
    )
    fig_ps.update_layout(template="plotly_white", height=260, margin=dict(t=10, b=20, l=0, r=0),
                          showlegend=False)
    st.plotly_chart(fig_ps, use_container_width=True)
    st.caption("Transaction count by payout status")

with col_r:
    fig_val = px.bar(
        payout_summary, x="Status", y="Net Amount ($)",
        color="Status", color_discrete_map=color_map,
        labels={"Net Amount ($)": "Net Amount ($)", "Status": ""},
    )
    fig_val.update_layout(template="plotly_white", height=260, margin=dict(t=10, b=20, l=0, r=0),
                           showlegend=False, yaxis=dict(tickprefix="$", tickformat=",.0f"))
    st.plotly_chart(fig_val, use_container_width=True)
    st.caption("Net dollar value by payout status")

# ── Exception Log ─────────────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">Exception Log</h3>', unsafe_allow_html=True)

exc_filtered = exc[
    exc["severity"].isin(severity_filter) & exc["status"].isin(status_filter)
].copy()

col_type, col_aging = st.columns(2)

with col_type:
    type_summary = exc_filtered.groupby("exception_type").size().reset_index(name="Count")
    type_summary = type_summary.sort_values("Count", ascending=True)
    fig_et = px.bar(
        type_summary, x="Count", y="exception_type", orientation="h",
        color_discrete_sequence=["#d97706"],
        labels={"exception_type": "", "Count": "Exceptions"},
    )
    fig_et.update_layout(template="plotly_white", height=240, margin=dict(t=10, b=10, l=0, r=0))
    st.plotly_chart(fig_et, use_container_width=True)
    st.caption("Exception count by type")

with col_aging:
    aging_bins = pd.cut(
        exc_filtered["days_open"],
        bins=[0, 7, 14, 30, 60, float("inf")],
        labels=["0–7d", "8–14d", "15–30d", "31–60d", "60d+"],
        right=True,
    )
    aging_summary = aging_bins.value_counts().sort_index().reset_index()
    aging_summary.columns = ["Age Bucket", "Count"]
    fig_ag = px.bar(
        aging_summary, x="Age Bucket", y="Count",
        color_discrete_sequence=["#1B3A2F"],
        labels={"Age Bucket": "", "Count": "Open Exceptions"},
    )
    fig_ag.update_layout(template="plotly_white", height=240, margin=dict(t=10, b=10, l=0, r=0))
    st.plotly_chart(fig_ag, use_container_width=True)
    st.caption("Open exception aging — older buckets need escalation")

# ── Exceptions Table ──────────────────────────────────────────────────────────
st.markdown(f"**{len(exc_filtered):,} exceptions** match current filters")

display_exc = exc_filtered[[
    "exception_id", "customer_id", "exception_type", "severity", "status",
    "owner", "days_open", "detected_date"
]].copy()
display_exc["detected_date"] = display_exc["detected_date"].dt.strftime("%Y-%m-%d")
display_exc = display_exc.sort_values(["severity", "days_open"], ascending=[True, False])
display_exc.columns = ["ID", "Customer", "Type", "Severity", "Status", "Owner", "Days Open", "Detected"]

st.dataframe(
    display_exc.reset_index(drop=True),
    use_container_width=True,
    height=320,
    column_config={
        "Severity": st.column_config.TextColumn("Severity"),
        "Days Open": st.column_config.NumberColumn("Days Open", format="%d"),
    }
)

# ── Refund & Payment Status ────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">Payment & Refund Status</h3>', unsafe_allow_html=True)

col_ps, col_ref = st.columns(2)

with col_ps:
    pay_summary = txn.groupby("payment_status").agg(
        count=("transaction_id", "count"),
        gross=("gross_amount", "sum")
    ).reset_index()
    pay_summary.columns = ["Status", "Count", "Gross ($)"]
    fig_pay = px.pie(
        pay_summary, names="Status", values="Count",
        color_discrete_sequence=["#1B3A2F", "#d97706", "#dc2626", "#6b7280", "#3d7a5c"],
        hole=0.4,
    )
    fig_pay.update_layout(template="plotly_white", height=240, margin=dict(t=10, b=30, l=0, r=0),
                           legend=dict(orientation="h", yanchor="top", y=-0.1))
    st.plotly_chart(fig_pay, use_container_width=True)
    st.caption("Transaction count by payment status")

with col_ref:
    refunded = txn[txn["payment_status"] == "refunded"]
    if len(refunded) > 0:
        ref_by_month = refunded.groupby("month").agg(
            count=("transaction_id", "count"),
            gross=("gross_amount", "sum")
        ).reset_index()
        fig_ref = px.bar(
            ref_by_month, x="month", y="gross",
            color_discrete_sequence=["#dc2626"],
            labels={"month": "", "gross": "Refunded Amount ($)"},
        )
        fig_ref.update_layout(template="plotly_white", height=240, margin=dict(t=10, b=20, l=0, r=0),
                               yaxis=dict(tickprefix="$", tickformat=",.0f"))
        st.plotly_chart(fig_ref, use_container_width=True)
        st.caption("Refunded gross by month — spikes worth investigating")
    else:
        st.info("No refunded transactions in dataset.")
