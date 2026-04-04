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
def generate_portfolio(n, mult, disc_rate):
    np.random.seed(42)
    debt = np.random.uniform(500, 15000, n)
    # Generate Days Delinquent (up to 720 days / 24 months)
    days_delinquent = np.random.randint(1, 720, n)
    
    # Probability Logic: Baseline drops to 0 at 720 days
    prob = np.clip((1 - (days_delinquent / 720)) * mult, 0, 1)
    
    # Financial Logic: Net Present Value (NPV)
    # Using Daily Discounting for accuracy with 'Days'
    daily_rate = disc_rate / 365
    expected_recovery = debt * prob
    npv = expected_recovery / ((1 + daily_rate) ** days_delinquent)
    
    return pd.DataFrame({
        'Account_ID': [f"L-{np.random.randint(10000, 99999)}" for _ in range(n)],
        'Debt_Amount': debt,
        'Days_Delinquent': days_delinquent,
        'Recovery_Prob': prob,
        'NPV_Value': npv,
        'Recency_Score': 720 - days_delinquent 
    })

df = generate_portfolio(num_accounts, multiplier, annual_discount_rate)

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

fig = px.scatter(
    df, 
    x="Recency_Score", 
    y="NPV_Value",
    size="Debt_Amount", 
    color="Days_Delinquent",
    hover_name="Account_ID",
    trendline="ols",
    hover_data={
        'Recency_Score': False,
        'Debt_Amount': ':$,.2f',
        'NPV_Value': ':$,.2f',
        'Recovery_Prob': ':.1%',
        'Days_Delinquent': True
    },
    color_continuous_scale="RdBu_r",
    labels={"Recency_Score": "Age (720=New, 0=Old)", "NPV_Value": "Expected NPV ($)"},
    template="plotly_white",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# --- Data Export & Refined Table ---
st.divider()
col_table, col_download = st.columns()

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

# Select and format columns for display
display_df = df[['Account_ID', 'Debt_Amount', 'Days_Delinquent', 'Recovery_Prob', 'NPV_Value']].copy()

st.dataframe(
    display_df.sort_values(by='NPV_Value', ascending=False),
    column_config={
        "Account_ID": "Account ID",
        "Debt_Amount": st.column_config.NumberColumn(
            "Debt Amount", 
            format="$%,.2f"  # Comma for thousands, 2 decimals
        ),
        "NPV_Value": st.column_config.NumberColumn(
            "Expected NPV", 
            format="$%,.2f"  # Comma for thousands, 2 decimals
        ),
        "Recovery_Prob": st.column_config.ProgressColumn(
            "Recovery Prob", 
            format="%.0f%%", # Displays 0-100% based on decimal value
            min_value=0, 
            max_value=1
        ),
        "Days_Delinquent": st.column_config.NumberColumn(
            "Days Delinquent", 
            format="%d"
        )
    },
    use_container_width=True,
    hide_index=True
)
