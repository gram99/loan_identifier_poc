import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- Page Config ---
st.set_page_config(page_title="Loan Collectability Toolbox", layout="wide", page_icon="📈")

# --- Excel Template Generator with Samples ---
def create_template_with_samples():
    buffer = io.BytesIO()
    samples = pd.DataFrame({
        'Account_ID': ['L-12345', 'L-67890', 'L-54321'],
        'Debt_Amount': [5000.00, 12500.50, 750.00],
        'Days_Delinquent': [15, 45, 120]
    })
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        samples.to_excel(writer, index=False, sheet_name='Template')
    return buffer.getvalue()

st.title("📊 Loan Collectability & Recovery Analytics")

# --- Sidebar: Data Source & Parameters ---
st.sidebar.header("📂 Data Source")
data_source = st.sidebar.radio("Select Data Source:", ["Synthetic Demo", "Upload Data"])

st.sidebar.divider()
st.sidebar.subheader("📥 Need a Template?")
template_bytes = create_template_with_samples()
st.sidebar.download_button(
    label="Download Excel Template",
    data=template_bytes,
    file_name="loan_data_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

df = pd.DataFrame()

if data_source == "Upload Data":
    uploaded_file = st.sidebar.file_uploader("Upload your Loan CSV or Excel", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
            st.stop()
    else:
        st.info("👋 Please upload a file in the sidebar to begin or switch to 'Synthetic Demo'.")
        st.stop()
else:
    num_accounts = st.sidebar.slider("Number of Loan Accounts", 50, 1000, 200)

st.sidebar.divider()
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
    
    required = ['Debt_Amount', 'Days_Delinquent']
    if not all(col in data.columns for col in required):
        st.error(f"Data must contain these exact column names: {required}")
        st.stop()

    daily_rate = annual_discount_rate / 365
    data['Recovery_Prob'] = np.clip((1 - (data['Days_Delinquent'] / 720)) * multiplier, 0, 1)
    data['NPV_Value'] = (data['Debt_Amount'] * data['Recovery_Prob']) / ((1 + daily_rate) ** data['Days_Delinquent'])
    data['Recency_Score'] = 720 - data['Days_Delinquent']
    
    # Aging Bucket Logic
    bins = [0, 30, 60, 90, 180, 360, float('inf')]
    labels = ['0-30 Days', '31-60 Days', '61-90 Days', '91-180 Days', '181-360 Days', '360+ Days']
    data['Aging_Bucket'] = pd.cut(data['Days_Delinquent'], bins=bins, labels=labels)
    
    return data

df = process_data(df, is_synthetic=(data_source == "Synthetic Demo"))

# --- Dashboard Layout ---
total_book, total_npv = df['Debt_Amount'].sum(), df['NPV_Value'].sum()
c1, c2, c3 = st.columns(3)
c1.metric("Total Book Value", f"${total_book:,.2f}")
c2.metric("Portfolio NPV", f"${total_npv:,.2f}", delta=scenario)
c3.metric("Avg. Recovery Chance", f"{df['Recovery_Prob'].mean():.1%}")

# Visual Chart (Scatter)
st.divider()
st.subheader("🔍 Portfolio Recovery Map")
fig_scatter = px.scatter(df, x="Recency_Score", y="NPV_Value", size="Debt_Amount", color="Days_Delinquent",
                 hover_name="Account_ID" if 'Account_ID' in df.columns else None,
                 trendline="ols", template="plotly_white", height=500,
                 color_continuous_scale="RdBu_r", labels={"Recency_Score": "Age Score (720=Newest)"})
st.plotly_chart(fig_scatter, use_container_width=True)

# --- NEW: Aging Bucket Summary Section ---
st.divider()
st.subheader("📁 Aging Bucket Summary")
bucket_summary = df.groupby('Aging_Bucket', observed=True).agg({
    'Debt_Amount': 'sum',
    'NPV_Value': 'sum',
    'Account_ID': 'count'
}).reset_index()
bucket_summary.columns = ['Aging Bucket', 'Total Debt ($)', 'Expected NPV ($)', 'Account Count']

col_chart, col_table_b = st.columns([2, 1])

with col_chart:
    fig_bar = px.bar(bucket_summary, x='Aging Bucket', y='Total Debt ($)', 
                     text_auto='.2s', title="Total Debt Volume by Bucket",
                     color='Total Debt ($)', color_continuous_scale="Reds")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_table_b:
    st.dataframe(bucket_summary, use_container_width=True, hide_index=True,
                 column_config={
                     "Total Debt ($)": st.column_config.NumberColumn(format="$%,.0f"),
                     "Expected NPV ($)": st.column_config.NumberColumn(format="$%,.0f")
                 })

# Recovery Ledger Table
st.divider()
col_head, col_dl = st.columns([2, 1])
with col_head:
    st.subheader("📋 Detailed Account Ledger")
with col_dl:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Analysis to CSV", data=csv, file_name='recovery_analysis.csv', mime='text/csv')

st.dataframe(
    df[['Account_ID', 'Debt_Amount', 'Days_Delinquent', 'Recovery_Prob', 'NPV_Value']].sort_values(by='NPV_Value', ascending=False),
    column_config={
        "Debt_Amount": st.column_config.NumberColumn("Debt Amount", format="$%,.2f"),
        "NPV_Value": st.column_config.NumberColumn("Expected NPV", format="$%,.2f"),
        "Recovery_Prob": st.column_config.ProgressColumn("Recovery Prob", format="%.0f%%", min_value=0, max_value=1),
        "Days_Delinquent": st.column_config.NumberColumn("Days Delinquent", format="%d")
    },
    use_container_width=True, hide_index=True
)
