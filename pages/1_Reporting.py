import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
.metric-card .label {
    font-size: 0.8rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}
.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: #1B3A2F;
    font-family: 'Source Serif 4', serif;
    line-height: 1.2;
}
.metric-card .delta {
    font-size: 0.85rem;
    margin-top: 4px;
}
.delta-up { color: #059669; }
.delta-down { color: #dc2626; }
.section-header {
    font-family: 'Source Serif 4', serif;
    color: #1B3A2F;
    border-bottom: 2px solid #d97706;
    padding-bottom: 4px;
    margin-top: 2rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Projexions")
    st.caption("Reporting Automation Demo")
    st.markdown("---")
    st.markdown("**Product 1 of 3**")
    st.markdown("This demo shows how a monthly reporting workflow can be automated from raw transaction exports.")
    st.markdown("---")
    st.caption("[projexions.net](https://projexions.net)")

@st.cache_data
def load_data():
    monthly = pd.read_csv("data/monthly_summary.csv")
    monthly["month_dt"] = pd.to_datetime(monthly["month"])
    monthly = monthly.sort_values("month_dt")
    monthly["gross_mom"] = monthly["gross_sales"].pct_change() * 100
    monthly["net_mom"] = monthly["net_deposits"].pct_change() * 100
    monthly["fee_rate"] = monthly["total_fees"] / monthly["gross_sales"] * 100

    txn = pd.read_csv("data/transactions.csv")
    txn["transaction_date"] = pd.to_datetime(txn["transaction_date"], format="mixed")
    txn["month"] = txn["transaction_date"].dt.to_period("M").astype(str)
    return monthly, txn

monthly, txn = load_data()

# ── Header ──────────────────────────────────────────────────────────────────
st.title("Reporting Automation")
st.markdown("Monthly KPIs, revenue trends, and fee analytics — assembled automatically from raw exports.")
st.markdown("---")

# ── Month selector ───────────────────────────────────────────────────────────
months = monthly["month"].tolist()
selected_month = st.selectbox("Reporting month", months, index=len(months) - 1)
row = monthly[monthly["month"] == selected_month].iloc[0]
prev_rows = monthly[monthly["month"] < selected_month]
prev_row = prev_rows.iloc[-1] if len(prev_rows) > 0 else None

def fmt_currency(v):
    if v >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    elif v >= 1_000:
        return f"${v/1_000:.1f}K"
    return f"${v:,.0f}"

def delta_html(val, pct, invert=False):
    if pct is None:
        return '<span class="delta" style="color:#9ca3af">First month</span>'
    good = pct >= 0 if not invert else pct <= 0
    arrow = "▲" if pct >= 0 else "▼"
    cls = "delta-up" if good else "delta-down"
    return f'<span class="delta {cls}">{arrow} {abs(pct):.1f}% vs prior month</span>'

gross_pct = ((row.gross_sales - prev_row.gross_sales) / prev_row.gross_sales * 100) if prev_row is not None else None
net_pct = ((row.net_deposits - prev_row.net_deposits) / prev_row.net_deposits * 100) if prev_row is not None else None
fee_pct = ((row.total_fees - prev_row.total_fees) / prev_row.total_fees * 100) if prev_row is not None else None

c1, c2, c3, c4 = st.columns(4)
cards = [
    (c1, "Gross Sales", fmt_currency(row.gross_sales), delta_html(row.gross_sales, gross_pct)),
    (c2, "Net Deposits", fmt_currency(row.net_deposits), delta_html(row.net_deposits, net_pct)),
    (c3, "Total Fees", fmt_currency(row.total_fees), delta_html(row.total_fees, fee_pct, invert=True)),
    (c4, "Transactions", f"{int(row.transaction_count):,}", None),
]
for col, label, value, delta in cards:
    with col:
        delta_html_str = delta if delta else ""
        st.markdown(f"""
<div class="metric-card">
<div class="label">{label}</div>
<div class="value">{value}</div>
{delta_html_str}
</div>""", unsafe_allow_html=True)

# ── Revenue Trend ─────────────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">Revenue Trend</h3>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

with col_left:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["gross_sales"],
        name="Gross Sales", line=dict(color="#1B3A2F", width=2.5),
        mode="lines+markers", marker=dict(size=5)
    ))
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["net_deposits"],
        name="Net Deposits", line=dict(color="#d97706", width=2, dash="dash"),
        mode="lines+markers", marker=dict(size=5)
    ))
    fig.update_layout(
        template="plotly_white",
        height=280,
        margin=dict(t=20, b=20, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis_title=None, yaxis_title=None,
        yaxis=dict(tickprefix="$", tickformat=",.0f"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("**Month-over-month growth**")
    mom_df = monthly[monthly["month"] > months[0]][["month", "gross_mom", "net_mom"]].copy()
    mom_df.columns = ["Month", "Gross MoM %", "Net MoM %"]
    mom_df["Gross MoM %"] = mom_df["Gross MoM %"].map(lambda x: f"{x:+.1f}%")
    mom_df["Net MoM %"] = mom_df["Net MoM %"].map(lambda x: f"{x:+.1f}%")
    st.dataframe(mom_df.set_index("Month"), use_container_width=True, height=260)

# ── Fee Analysis ──────────────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">Fee Analysis</h3>', unsafe_allow_html=True)

col_fee1, col_fee2 = st.columns(2)

with col_fee1:
    fig_fee = px.bar(
        monthly, x="month", y="total_fees",
        color_discrete_sequence=["#d97706"],
        labels={"month": "", "total_fees": "Total Fees ($)"},
    )
    fig_fee.update_layout(template="plotly_white", height=240, margin=dict(t=20, b=20, l=0, r=0),
                          yaxis=dict(tickprefix="$", tickformat=",.0f"))
    st.plotly_chart(fig_fee, use_container_width=True)
    st.caption("Total fees by month")

with col_fee2:
    fig_rate = px.line(
        monthly, x="month", y="fee_rate",
        color_discrete_sequence=["#1B3A2F"],
        labels={"month": "", "fee_rate": "Fee Rate (%)"},
        markers=True,
    )
    fig_rate.update_layout(template="plotly_white", height=240, margin=dict(t=20, b=20, l=0, r=0),
                           yaxis=dict(ticksuffix="%"))
    st.plotly_chart(fig_rate, use_container_width=True)
    st.caption("Fee rate as % of gross sales — watch for drift")

# ── Category Breakdown ────────────────────────────────────────────────────────
st.markdown('<h3 class="section-header">Revenue by Category & Source</h3>', unsafe_allow_html=True)

month_txn = txn[txn["month"] == selected_month]

col_cat, col_src = st.columns(2)

with col_cat:
    if len(month_txn) > 0:
        cat_summary = month_txn.groupby("category")["gross_amount"].sum().reset_index()
        cat_summary.columns = ["Category", "Gross Amount"]
        cat_summary = cat_summary.sort_values("Gross Amount", ascending=True)
        fig_cat = px.bar(
            cat_summary, x="Gross Amount", y="Category", orientation="h",
            color_discrete_sequence=["#1B3A2F"],
            labels={"Gross Amount": "Gross ($)", "Category": ""},
        )
        fig_cat.update_layout(template="plotly_white", height=260, margin=dict(t=10, b=20, l=0, r=0),
                               xaxis=dict(tickprefix="$", tickformat=",.0f"))
        st.plotly_chart(fig_cat, use_container_width=True)
        st.caption("Transaction volume by category")
    else:
        st.info("No transactions found for this month.")

with col_src:
    if len(month_txn) > 0:
        src_summary = month_txn.groupby("source_system")["gross_amount"].sum().reset_index()
        src_summary.columns = ["Source", "Gross Amount"]
        fig_src = px.pie(
            src_summary, names="Source", values="Gross Amount",
            color_discrete_sequence=["#1B3A2F", "#d97706", "#3d7a5c", "#b45309", "#6b4c2a"],
            hole=0.45,
        )
        fig_src.update_layout(template="plotly_white", height=260, margin=dict(t=10, b=20, l=0, r=0),
                               legend=dict(orientation="h", yanchor="bottom", y=-0.3))
        st.plotly_chart(fig_src, use_container_width=True)
        st.caption("Gross volume by payment source")
    else:
        st.info("No transactions found for this month.")

# ── Full Year Summary Table ───────────────────────────────────────────────────
with st.expander("Full year summary table"):
    display = monthly[["month", "gross_sales", "total_fees", "net_deposits", "transaction_count", "gross_mom", "fee_rate"]].copy()
    display.columns = ["Month", "Gross Sales", "Total Fees", "Net Deposits", "Txn Count", "MoM %", "Fee Rate %"]
    display["Gross Sales"] = display["Gross Sales"].map(lambda x: f"${x:,.0f}")
    display["Total Fees"] = display["Total Fees"].map(lambda x: f"${x:,.0f}")
    display["Net Deposits"] = display["Net Deposits"].map(lambda x: f"${x:,.0f}")
    display["MoM %"] = display["MoM %"].map(lambda x: f"{x:+.1f}%" if pd.notna(x) else "—")
    display["Fee Rate %"] = display["Fee Rate %"].map(lambda x: f"{x:.2f}%")
    st.dataframe(display.set_index("Month"), use_container_width=True)
