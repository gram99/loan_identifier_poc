# 📈 Loan Collectability & Recovery Analytics Toolbox

A Streamlit-based interactive analytics tool for modeling **loan collectability**, **expected recovery value**, and **portfolio‑level cash‑flow projections**. This app allows analysts to upload real data or generate synthetic demo portfolios, visualize recovery potential, and export results for further analysis.

---

## 🚀 Features

### 🔹 1. Synthetic or Uploaded Data
- Upload your own **CSV or Excel** file  
**OR**  
- Generate a synthetic portfolio with adjustable account count

### 🔹 2. Recovery Probability & NPV Modeling
The app computes:
- Recovery probability (based on delinquency & strategy)
- Expected Net Present Value (NPV)
- Estimated recovery month
- Delinquency bucket classification

### 🔹 3. Interactive Visualizations
Includes:
- **Recovery Map (Bubble Chart)** — NPV vs. recency with trendline  
- **12‑Month Projected Cash Flow**  
- **Bucket Concentration Bar Chart**  
- **Goal Progress Gauge**

### 🔹 4. Account Ledger & Export
- Sortable, formatted account table  
- Export full results to CSV  
- Downloadable Excel template with sample data  

### 🔹 5. Priority Action Items
Automatically identifies the **Top 5 accounts** with highest expected recovery value.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/loan-collectability-toolbox.git
cd loan-collectability-toolbox

# Install dependencies
pip install -r requirements.txt
