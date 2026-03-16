# E-commerce Sales Dashboard

**Worked on:** Winter 2024

**Stack:** _Python, Pandas, Plotly, Streamlit_

**Analyze $9.7M in transactions to identify revenue drivers, seasonal patterns, and high-value customer segments for a UK online retailer.**

---

## 🚀 Overview

This project delivers an interactive **Streamlit dashboard** and reproducible analysis pipeline built on the Online Retail II dataset.

It focuses on:

- Revenue seasonality and trends
- Geographic performance across countries
- Product-level performance drivers
- Customer segmentation (high-value customers, retention patterns)

**Scope:** ~1.07M raw rows (cleaned to ~541K transactions) · 38 countries · 2009–2011.

---

## 📂 Project Structure

```
ecommerce_sales/
├── data/
│   ├── raw/                    # Original dataset (download instructions below)
│   ├── processed/              # Cleaned data
│   └── sample/                 # Small sample for quick testing
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   └── 03_analysis.ipynb
├── src/
│   ├── data_loader.py          # Data loading utilities
│   ├── preprocessing.py        # Cleaning functions
│   └── metrics.py              # KPI calculations
├── demo/
│   └── app.py                  # Streamlit dashboard
├── docs/
│   ├── case_study.md           # One-page case study
│   ├── case_study.pdf          # PDF version
│   └── img/                    # Visualizations
├── requirements.txt
├── Makefile
└── README.md
```

---

## ⚙️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MarcSaghiah/ecommerce_sales.git
   cd ecommerce_sales
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

(Optional) Create and activate a virtual environment if you prefer isolated dependencies.

---

## 📊 Streamlit Dashboard

Run the dashboard locally:

```bash
streamlit run demo/app.py
```

---

## 🔄 Reproduce the Analysis

Full pipeline:

```bash
make reproduce
```

Or step-by-step:

```bash
python src/preprocessing.py     # Clean raw data
jupyter notebook notebooks/     # Run analysis notebooks
streamlit run demo/app.py       # Launch dashboard
```

---

## 🗂️ Data

### Dataset

**Source:** Online Retail II (UCI Machine Learning Repository)

The dataset includes:

- Transaction-level purchases (quantity, unit price, date)
- Product identifiers and descriptions
- Customer IDs (often missing in raw data)
- Customer country

### How to get the data

**Option 1 (Recommended): Download from UCI**

- Download the dataset from UCI and place it in:
  `data/raw/online_retail_II.xlsx`

**Option 2: Use the sample data**

- A small preprocessed sample is included under `data/sample/` for quick testing.

> Tip: See `data/README.md` for detailed data documentation and cleaning notes.

---

## 🏆 Key Insights

### 1) Revenue is Highly Seasonal

![Seasonal Trend](docs/img/seasonal_trend.png)

November generates **1.5–3× average monthly revenue** due to holiday gift shopping. January shows a sharp drop post-holidays.

**Recommendation:** Increase inventory in October; run clearance campaigns in January.

### 2) The 80/20 Rule Applies

![Customer Segments](docs/img/customer_segments.png)

Top customers generate the majority of revenue (high-LTV “Champions”).

**Recommendation:** Build a VIP program and prioritize retention.

### 3) UK Dominates, But Europe is Growing

![Geographic Distribution](docs/img/geographic.png)

UK drives most revenue; Germany, France, and EIRE are leading international markets.

**Recommendation:** Invest in EU marketing; consider EU-based fulfillment.

---

**Author: Marc Saghiah**