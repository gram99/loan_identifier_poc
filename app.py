import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Loan Collectability Toolbox", layout="wide", page_icon="📈")

st.title("📊 Loan Collectability & Recovery Analytics")

# --- Sidebar: Data Source & Parameters ---
st.sidebar.header("📂 Data Source")
data_source = st.sidebar.radio("Select Data Source:", ["Synthetic Demo", "Upload CSV"])

# Initialize variables
df = pd.DataFrame()

if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload your loan CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success("✅ File uploaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
    else:
        st.info("👋 Please upload a CSV file in the sidebar to begin.")
        st.stop()
else:
    # Synthetic Parameters
    num_accounts = st.sidebar.slider("Number of Loan Accounts", 50, 1000, 200)
    st.sidebar.divider()

# Shared Parameters
annual_discount_rate = st.sidebar.slider("Annual Discount Rate (%)", 1.0, 20.0, 8.0) / 100
scenario = st.sidebar.radio("Recovery Strategy Mode:", ["Standard", "Aggressive", "Conservative"])
multiplier = {"Conservative": 0.6, "Standard": 1.0, "Aggressive": 1.4}[scenario]

# --- Data Engine ---
def process_data(data, is_synthetic=False):
    if is_synthetic:
        np.random.seed(42)
        n = num_accounts
        data = pd.DataFrame({
            'Account_ID': [f"L-{np.random.randint(10000, 99999)}" for _ in range(n)],
            'Debt_Amount': np.random.uniform(500, 15000, n),
            'Days_Delinquent': np.random.randint(1, 720, n)
        })
    
    # Validation: Ensure required columns exist
    required = ['Debt_Amount', 'Days_Delinquent']
    if not all(col in data.columns for col in required):
        st.error(f"CSV must contain these columns: {required}")
        st.stop()

    # Financial Logic
    daily_rate = annual_discount_rate / 365
    data['Recovery_Prob'] = np.clip((1 - (data['Days_Delinquent'] / 720)) * multiplier, 0, 1)
    data['NPV_Value'] = (data['Debt_Amount'] * data['Recovery_Prob']) / ((1 + daily_rate) ** data['Days_Delinquent'])
    data['Recency_Score'] = 720 - data['Days_Delinquent']
    return data

# Process the selected data
df = process_data(df, is_synthetic=(data_source == "Synthetic Demo"))

# --- Dashboard Layout (Visuals & Table) ---
total_book, total_npv = df['Debt_Amount'].sum(), df['NPV_Value'].sum()
c1, c2, c3 = st.columns(3)
c1.metric("Total Book Value", f"${total_book:,.2f}")
c2.metric("Portfolio NPV", f"${total_npv:,.2f}", delta=scenario)
c3.metric("Avg. Recovery Chance", f"{df['Recovery_Prob'].mean():.1%}")

# Chart
fig = px.scatter(df, x="Recency_Score", y="NPV_Value", size="Debt_Amount", color="Days_Delinquent",
                 hover_name="Account_ID" if 'Account_ID' in df.columns else None,
                 trendline="ols", template="plotly_white", height=500,
                 color_continuous_scale="RdBu_r", labels={"Recency_Score": "Age (720=New)"})
st.plotly_chart(fig, use_container_width=True)

# Table
st.subheader("📋 Recovery Ledger")
st.dataframe(
    df.sort_values(by='NPV_Value', ascending=False),
    column_config={
        "Debt_Amount": st.column_config.NumberColumn("Debt Amount", format="$%,.2f"),
        "NPV_Value": st.column_config.NumberColumn("Expected NPV", format="$%,.2f"),
        "Recovery_Prob": st.column_config.ProgressColumn("Recovery Prob", format="%.0f%%", min_value=0, max_value=1),
        "Days_Delinquent": st.column_config.NumberColumn("Days Delinquent", format="%d")
    },
    use_container_width=True, hide_index=True
)
