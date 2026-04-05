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
        'Days_Delinquent': [45, 120, 15]
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
        st.info("Upload a file in the sidebar to begin.")
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
    
    daily_rate = ann_rate / 365
    data['Recovery_Prob'] = np.clip((1 - (data['Days_Delinquent'] / 720)) * multiplier, 0, 1)
    data['NPV_Value'] = (data['Debt_Amount'] * data['Recovery_Prob']) / ((1 + daily_rate) ** data['Days_Delinquent'])
    data['Est_Recovery_Month'] = np.clip((data['Days_Delinquent'] / 60).astype(int) + 1, 1, 12)
    
    bins = [0, 30, 60, 90, 180, 360, 720, float('inf')]
    labels = ['0-30', '31-60', '61-90', '91-180', '181-360', '361-720', '720+']
    data['Bucket'] = pd.cut(data['Days_Delinquent'], bins=bins, labels=labels)
    
    # Pre-round data to ensure clean numeric foundations
    data['Debt_Amount'] = data['Debt_Amount'].round(2)
    data['NPV_Value'] = data['NPV_Value'].round(2)
    return data

df = process_data(df_input, is_synthetic=(data_source == "Synthetic Demo"))
total_npv = df['NPV_Value'].sum()

# --- 1. CENTERPIECE: Recovery Map (Bubble Graph) ---
st.divider()
st.subheader("🔍 Portfolio Recovery Map")

fig_map = px.scatter(
    df, x=720-df['Days_Delinquent'], y="NPV_Value", size="Debt_Amount", color="Days_Delinquent",
    hover_name="Account_ID", trendline="ols", template="plotly_white", color_continuous_scale="RdBu_r",
    custom_data=["Debt_Amount", "Days_Delinquent"], # Raw values for custom hover
    labels={"x": "Recency Score (Newest on Right)", "NPV_Value": "Expected NPV ($)"},
    height=550
)

# Robust Fix: Manually targeting the marker trace to force currency formatting
fig_map.update_traces(
    selector=dict(mode='markers'), # Only applies to bubbles, ignoring the trendline
    hovertemplate=(
        "<b>Account: %{hovertext}</b><br><br>" +
        "Expected NPV: $%{y:,.2f}<br>" +
        "Debt Amount: $%{customdata[0]:,.2f}<br>" +
        "Days Delinquent: %{customdata[1]}<extra></extra>"
    )
)

# Secondary Fix: Force the Y-Axis tick format to follow suit
fig_map.update_layout(yaxis_tickformat='$,.2f', hovermode="closest")

st.plotly_chart(fig_map, use_container_width=True)

# --- 2. Account Ledger ---
st.divider()
col_head, col_dl = st.columns(2)
with col_head:
    st.subheader("📋 Detailed Account Ledger")
with col_dl:
    st.download_button("📥 Export to CSV", df.to_csv(index=False).encode('utf-8'), "recovery_analysis.csv", "text/csv")

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

# --- 3. Analytics: Cash Flow & Buckets ---
st.divider()
col_cf, col_bc = st.columns(2)

with col_cf:
    st.subheader("🗓️ 12-Month Projected Cash Flow")
    cash_flow = df.groupby('Est_Recovery_Month')['NPV_Value'].sum().reset_index()
    base_date = datetime.now()
    cash_flow['Month'] = cash_flow['Est_Recovery_Month'].apply(lambda x: (base_date + timedelta(days=x*30)).strftime('%b %Y'))
    
    fig_cf = px.line(cash_flow, x='Month', y='NPV_Value', markers=True, template='plotly_white', color_discrete_sequence=['#00CC96'])
    fig_cf.update_traces(hovertemplate="Month: %{x}<br>Projected NPV: $%{y:,.2f}<extra></extra>")
    fig_cf.update_layout(yaxis_tickformat='$,.2f')
    st.plotly_chart(fig_cf, use_container_width=True)

with col_bc:
    st.subheader("📁 Bucket Concentration")
    bucket_sum = df.groupby('Bucket', observed=True)['Debt_Amount'].sum().reset_index()
    fig_bc = px.bar(bucket_sum, x='Bucket', y='Debt_Amount', color='Debt_Amount', color_continuous_scale='Reds', template='plotly_white')
    fig_bc.update_traces(hovertemplate="Bucket: %{x}<br>Total Debt: $%{y:,.2f}<extra></extra>")
    fig_bc.update_layout(yaxis_tickformat='$,.2f')
    st.plotly_chart(fig_bc, use_container_width=True)

# --- 4. FOOTER: Goal Tracker & Priority Table ---
st.divider()
col_goal, col_top = st.columns(2)

with col_goal:
    st.subheader("🎯 Recovery Goal Progress")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = total_npv,
        delta = {'reference': recovery_target, 'position': "top"},
        gauge = {
            'axis': {'range': [None, max(recovery_target * 1.2, total_npv * 1.2)], 'tickformat': "$,.2f"},
            'bar': {'color': "#00CC96"},
            'threshold': {'line': {'color': "red", 'width': 3}, 'value': recovery_target}
        }
    ))
    fig_gauge.update_layout(height=300, margin=dict(t=30, b=0, l=30, r=30))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_top:
    st.subheader("🏆 Priority Action Items")
    st.write("Top 5 collectible accounts to prioritize for your goal:")
    top_5 = df[['Account_ID', 'Debt_Amount', 'NPV_Value']].sort_values(by='NPV_Value', ascending=False).head(5)
    st.table(top_5.style.format({'Debt_Amount': '${:,.2f}', 'NPV_Value': '${:,.2f}'}))

# Sidebar Template Download
st.sidebar.divider()
st.sidebar.download_button("📥 Download Excel Template", create_template_with_samples(), "loan_template.xlsx")
