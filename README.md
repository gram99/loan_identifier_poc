# Loan Collectability Toolbox

The **Loan Collectability Toolbox** is an interactive Streamlit application designed for financial analysts and recovery teams to evaluate the health of debt portfolios. By applying customizable discount rates and recovery probability multipliers, the tool calculates the **Expected Net Present Value (NPV)** of outstanding loans to prioritize high-value collection efforts.

## Key Features
*   **Dynamic Data Ingestion:** Toggle between synthetic demo data or upload your own CSV/Excel ledgers.
*   **Strategy Modeling:** Compare Conservative, Standard, and Aggressive recovery scenarios in real-time.
*   **Predictive Cash Flow:** View 12-month projections based on estimated recovery months derived from delinquency aging.
*   **Portfolio Mapping:** A multi-dimensional bubble chart plotting recency scores against expected NPV to identify "quick wins."

---

## Quick Start
Follow these steps to deploy the toolbox on your local machine or Streamlit Community Cloud.

### 1. Clone Repository
```bash
git clone https://github.com
cd loan-collectability-toolbox
