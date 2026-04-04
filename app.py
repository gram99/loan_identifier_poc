import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="Loan Collectability Toolbox", layout="wide", page_icon="📈")

# --- Helpers ---
def create_template_with_samples():
    buffer = io.BytesIO()
    samples = pd.DataFrame({
        'Account_ID': ['L-101', 'L-202', 'L-303'],
        'Debt_Amount': [5250.00, 10400.75, 890.00],
        'Days_Delinquent': [35, 120, 15]
    })
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        samples.to_excel(writer, index=False, sheet_name='Template')
    return buffer.getvalue()

st.title("📊 Loan Collectability & Recovery Analytics")

# --- Sidebar ---
st.sidebar.header("📂 Data Source")
data_source = st.sidebar.radio("Select Source:", ["Synthetic Demo", "Upload Data"])

if data_source == "Upload Data":
    uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])
    if uploaded_file:
        df_input = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    else:
        st.info("Upload a file to begin.")
        st.stop()
else:
    num_accounts = st.sidebar.slider("Number of Accounts", 50, 1000, 300)
    df_input = None

st.sidebar.divider()
st.sidebar.header("🎯 Recovery Goals")
recovery_target = st.sidebar.number_input("Set Recovery Target ($)", value=100000, step=5000)

st.sidebar.divider()
ann_rate = st.sidebar.slider("Discount Rate (%)", 1.0, 20.0, 8.0) / 100
scenario = st.sidebar.radio("Strategy:", ["Standard", "Aggressive", "Conservative"])
multiplier = {"Conservative": 0.6, "Standard": 1.0, "Aggressive": 1.4}[scenario]

# --- Data Engine ---
def process_data(data, is_synthetic=False):
    if is_synthetic:
        np.random.seed(42)
        data = pd.DataFrame({
            'Account_ID': [f"L-{np.random.randint(10000, 99999)}" for _ in range(num_accounts)],
            'Debt_Amount': np.random.uniform(500, 15000, num_accounts),
            'Days_Delinquent': np.random.randint(1, 720, num_accounts)
        })
    
    # Calculations
    daily_rate = ann_rate / 365
    data['Recovery_Prob'] = np.clip((1 - (data['Days_Delinquent'] / 720)) * multiplier, 0, 1)
    data['NPV_Value'] = (data['Debt_Amount'] * data['Recovery_Prob']) / ((1 + daily_rate) ** data['Days_Delinquent'])
    data['Est_Recovery_Month'] = np.clip((data['Days_Delinquent'] / 60).astype(int) + 1, 1, 12)
    
    bins = [0, 30, 60, 90, 180, 360, 720, float('inf')]
    labels = ['0-30', '31-60', '61-90', '91-180', '181-360', '361-720', '720+']
    data['Bucket'] = pd.cut(data['Days_Delinquent'], bins=bins, labels=labels)
    return data

df = process_data(df_input, is_synthetic=(data_source == "Synthetic Demo"))
total_npv = df['NPV_Value'].sum()

# --- Goal Tracker Gauge ---
st.divider()
fig_gauge = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = total_npv,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Recovery Goal Progress (Projected NPV vs. Target)", 'font': {'size': 20}},
    delta = {'reference': recovery_target, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
    gauge = {
        'axis': {'range': [None, max(recovery_target * 1.2, total_npv * 1.2)], 'tickformat': "$,.0f"},
        'bar': {'color': "#00CC96"},
        'steps': [
            {'range': [0, recovery_target], 'color': "#E5ECF6"},
            {'range': [recovery_target, recovery_target * 1.2], 'color': "#D1FFD1"}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': recovery_target}
    }
))
fig_gauge.update_layout(height=350, margin=dict(t=50, b=0))
st.plotly_chart(fig_gauge, use_container_width=True)

# --- Metrics ---
c1, c2, c3 = st.columns(3)
c1.metric("Total Book Value", f"${df['Debt_Amount'].sum():,.2f}")
c2.metric("Portfolio NPV", f"${total_npv:,.2f}", delta=f"{scenario} Strategy")
c3.metric("Avg. Recovery Prob", f"{df['Recovery_Prob'].mean():.1%}")

# --- Charts Section ---
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🗓️ 12-Month Projected Cash Flow")
    cash_flow = df.groupby('Est_Recovery_Month')['NPV_Value'].sum().reset_index()
    base_date = datetime.now()
    cash_flow['Month'] = cash_flow['Est_Recovery_Month'].apply(lambda x: (base_date + timedelta(days=x*30)).strftime('%b %Y'))
    st.plotly_chart(px.line(cash_flow, x='Month', y='NPV_Value', markers=True, template='plotly_white', color_discrete_sequence=['#00CC96']), use_container_width=True)

with col_right:
    st.subheader("📁 Bucket Concentration")
    bucket_sum = df.groupby('Bucket', observed=True)['Debt_Amount'].sum().reset_index()
    st.plotly_chart(px.bar(bucket_sum, x='Bucket', y='Debt_Amount', color='Debt_Amount', color_continuous_scale='Reds', template='plotly_white'), use_container_width=True)

# --- Map & Ledger ---
st.divider()
st.subheader("🔍 Recovery Map & Detailed Ledger")
st.plotly_chart(px.scatter(df, x=720-df['Days_Delinquent'], y="NPV_Value", size="Debt_Amount", color="Days_Delinquent",
                           hover_name="Account_ID", trendline="ols", template="plotly_white", color_continuous_scale="RdBu_r", 
                           labels={"x": "Recency Score (Newest on Right)", "NPV_Value": "Expected NPV ($)"}), use_container_width=True)

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

# Template Download
st.sidebar.divider()
st.sidebar.subheader("📥 Download Template")
st.sidebar.download_button("Excel Template", create_template_with_samples(), "loan_template.xlsx")
