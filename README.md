# 📈 Loan Collectability & Recovery Analytics Toolbox

**Author:** Gram99  
**Target Stakeholders:** Recovery Operations & Strategy (1st & 2nd Line of Defense)

A Streamlit-based interactive analytics dashboard that can be used for modeling **loan collectability**, **expected recovery value**, and **portfolio‑level cash‑flow projections**. This app allows analysts to upload real data or generate synthetic demo portfolios, visualize recovery potential, view goals, expected recoveries, and export results for further analysis.

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

streamlit
pandas
numpy
plotly
xlsxwriter
```

---

## Screen shots


<img width="1914" height="904" alt="Screenshot 2026-04-08 at 11 59 06 AM" src="https://github.com/user-attachments/assets/71f5ae07-2810-4c64-8618-18f5f53a4439" />

<img width="1890" height="801" alt="Screenshot 2026-04-08 at 11 59 35 AM" src="https://github.com/user-attachments/assets/0c066d92-fd56-42d6-9033-a55f35bcc205" />

<img width="1909" height="840" alt="Screenshot 2026-04-08 at 12 00 02 PM" src="https://github.com/user-attachments/assets/c89863fe-87e5-481c-87cc-8f6d042ce57a" />

<img width="1909" height="865" alt="Screenshot 2026-04-08 at 12 00 30 PM" src="https://github.com/user-attachments/assets/33b34f21-0367-449a-be56-5b36ac77e82f" />


