import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Loan Collectability Toolbox", layout="wide", page_icon="📈")

st.title("📊 Loan Collectability & Recovery Analytics")
st.markdown("### Strategic Financial Modeling for Debt Portfolios")

# --- Sidebar: Portfolio & Scenario Controls ---
st.sidebar.header("📁 Portfolio Parameters")
num_accounts = st.sidebar.slider("Number of Loan Accounts", 50, 1000, 200)
annual_discount_rate = st.sidebar.slider("Annual Discount Rate (%)", 1.0, 20.0, 8.0) / 100

st.sidebar.divider()
st.sidebar.header("🎯 Recovery Strategy")
scenario = st.sidebar.radio(
    "Select Strategy Mode:", 
    ["Standard", "Aggressive", "Conservative"],
    help="Adjusts the probability of successful collection based on effort level."
)

# Strategy Multipliers
scenario_map = {"Conservative": 0.6, "Standard": 1.0, "Aggressive": 1.4}
multiplier = scenario_map[scenario]

# --- Data Engine ---
@st.cache_data
def generate_portfolio(n, mult):
    np.random.seed(42)
    debt = np.random.uniform(500, 15000, n)
    months = np.random.randint(1, 24, n)
    
    # Probability Logic: Baseline drops to 0 at 24 months, modified by scenario
    prob = np.clip((1 - (months / 24)) * mult, 0, 1)
    
    # Financial Logic: Net Present Value (NPV)
    # PV = (Debt * Prob) / (1 + monthly_rate)^months
    m_rate = annual_discount_rate / 12
    expected_recovery = debt * prob
    npv = expected_recovery / ((1 + m_rate) ** months)
    
    return pd.DataFrame({
        'Account_ID': [f"L-{''.join(map(str, np.random.randint(0,9,5)))}" for _ in range(n)],
        'Debt_Amount': debt,
        'Months_Delinquent': months,
        'Recovery_Prob': prob,
        'NPV_Value': npv,
        'Recency_Score': 24 - months # 24 is new, 0 is old
    })

df = generate_portfolio(num_accounts, multiplier)

# --- Top-Level Metrics ---
total_book = df['Debt_Amount'].sum()
total_npv = df['NPV_Value'].sum()
avg_prob = df['Recovery_Prob'].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Total Book Value", f"${total_book:,.2f}")
c2.metric("Portfolio NPV (Expected)", f"${total_npv:,.2f}", 
          delta=f"{scenario} Strategy", delta_color="normal")
c3.metric("Avg. Recovery Chance", f"{avg_prob:.1%}")

# --- Interactive Visualization ---
st.divider()
st.subheader(f"Portfolio Recovery Map: {scenario} Analytics")
st.info("💡 **Hover over bubbles** to see specific Account IDs and Dollar Amounts. The **trendline** shows the value decay over time.")

# Generate Scatter with OLS Trendline
fig = px.scatter(
    df, 
    x="Recency_Score", 
    y="NPV_Value",
    size="Debt_Amount", 
    color="Months_Delinquent",
    hover_name="Account_ID",
    trendline="ols", # Ordinary Least Squares trendline
    hover_data={
        'Recency_Score': False,
        'Debt_Amount': ':$,.2f',
        'NPV_Value': ':$,.2f',
        'Recovery_Prob': ':.1%',
        'Months_Delinquent': True
    },
    color_continuous_scale="RdBu_r",
    labels={"Recency_Score": "Age (24=New, 0=24mo Old)", "NPV_Value": "Current NPV ($)"},
    template="plotly_white",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# --- Data Export & Table ---
st.divider()
col_table, col_download = st.columns([3, 1])

with col_table:
    st.subheader("📋 Account Recovery Ledger")

with col_download:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Recovery Report",
        data=csv,
        file_name='loan_recovery_report.csv',
        mime='text/csv',
    )

st.dataframe(
    df[['Account_ID', 'Debt_Amount', 'Months_Delinquent', 'Recovery_Prob', 'NPV_Value']]
    .sort_values(by='NPV_Value', ascending=False),
    use_container_width=True
)
