import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Loan Collectability Toolbox", layout="wide")

st.title("📊 Loan Collectability & Recovery Analytics")
st.markdown("### Strategic Visualization of Debt Aging vs. Collection Probability")

# --- Sidebar Controls ---
st.sidebar.header("Portfolio Parameters")
num_accounts = st.sidebar.slider("Number of Loan Accounts", 50, 500, 100)
max_debt = st.sidebar.number_input("Max Debt Amount ($)", value=10000)

# --- Logic: Generate Synthetic Data ---
np.random.seed(42)
debt_owed = np.random.uniform(500, max_debt, num_accounts)
months_delinquent = np.random.randint(1, 24, num_accounts)

# Collection probability decreases as debt ages (0% at 24 months)
prob_collection = np.clip(1 - (months_delinquent / 24), 0, 1)

df = pd.DataFrame({
    'debt': debt_owed,
    'months': months_delinquent,
    'prob': prob_collection,
    'x_pos': 24 - months_delinquent, # Right (24) is new, Left (0) is old
    'y_pos': np.random.uniform(0, 10, num_accounts)
})

# --- UI: Top Level Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Portfolio Value", f"${df['debt'].sum():,.2f}")
col2.metric("Avg. Probability of Recovery", f"{df['prob'].mean()*100:.1f}%")
col3.metric("High-Risk Accounts (>12mo)", len(df[df['months'] > 12]))

# --- UI: Visualization ---
st.divider()
fig, ax = plt.subplots(figsize=(12, 6))
scatter = ax.scatter(
    df['x_pos'], df['y_pos'], 
    s=df['debt']/10, 
    c=df['months'], 
    cmap='RdBu_r', 
    alpha=0.7, edgecolors='w'
)

ax.set_title('Credit Risk Model: Debt Aging & Collection Probability')
ax.set_xlabel('Recency (Right: 0 Months Delinquent | Left: 24 Months Delinquent)')
ax.set_yticks([]) # Hide Y axis as it's just for visual spread
fig.colorbar(scatter, label='Months Delinquent')

st.pyplot(fig)

# --- UI: Data Breakdown ---
st.divider()
st.subheader("📋 Account Recovery Ledger")
st.dataframe(df[['debt', 'months', 'prob']].sort_values(by='prob'), use_container_width=True)
