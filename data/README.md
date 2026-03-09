# Data Documentation

## Dataset Information

### Primary Dataset: UCI Online Retail II

| Field | Value |
|-------|-------|
| **Name** | Online Retail II |
| **Source** | UCI Machine Learning Repository |
| **URL** | https://archive.ics.uci.edu/dataset/502/online+retail+ii |
| **Download Date** | [Your download date] |
| **License** | CC BY 4.0 |
| **Citation** | Daqing Chen, Sai Laing Sain, and Kun Guo (2012). Data mining for the online retail industry. Journal of Database Marketing & Customer Strategy Management. |

### Dataset Description

This is a transactional dataset containing all transactions occurring between 01/12/2009 and 09/12/2011 for a UK-based and registered non-store online retail. The company mainly sells unique all-occasion gifts. Many customers of the company are wholesalers.

### Schema

| Column | Type | Description |
|--------|------|-------------|
| Invoice | String | 6-digit invoice number. Prefix 'C' indicates cancellation |
| StockCode | String | 5-digit product code |
| Description | String | Product name |
| Quantity | Integer | Number of units per transaction |
| InvoiceDate | Datetime | Invoice date and time |
| Price | Float | Unit price in GBP (£) |
| Customer ID | Float | 5-digit customer ID |
| Country | String | Customer's country of residence |

### Data Quality Notes

**Original Dataset:**
- 1,067,371 total transactions across 2 sheets (2009-2010 and 2010-2011)
- ~25% of transactions have missing Customer ID
- ~2% are cancellations (Invoice starts with 'C')
- Some negative quantities (returns/adjustments)
- Some extreme outliers in Quantity and Price

**Cleaning Applied:**
1. Removed cancellations (Invoice starting with 'C')
2. Removed rows with missing Customer ID
3. Removed negative/zero quantities and prices
4. Removed outliers (>99th percentile for Quantity and Price)

**Cleaned Dataset:**
- 541,909 transactions (50.7% of original)
- 5,942 unique customers
- 38 countries

---

## Sample Data

### Purpose
The `sample_data.csv` file is a synthetic dataset that mimics the structure and patterns of the real UCI dataset. It allows users to:
- Test the code without downloading the full dataset
- Quick development and debugging
- Demo purposes

### Sample Data Statistics
- 7,143 transactions
- 2,000 invoices
- 452 customers
- 19 countries
- Total revenue: £184,598.22

### Important Note
**The sample data is synthetically generated** and should not be used for actual business analysis. For real analysis, download the original UCI dataset.

---

## Download Instructions

1. Visit: https://archive.ics.uci.edu/dataset/502/online+retail+ii
2. Click "Download" to get the dataset
3. Extract the Excel file: `online_retail_II.xlsx`
4. Place the file in: `data/raw/online_retail_II.xlsx`
5. Run preprocessing: `python src/preprocessing.py`

---

## Ethical Considerations

- Customer IDs are anonymized (no PII)
- Country-level location only (no granular geographic data)
- Transaction data is from 2009-2011 (historical, no real-time privacy concerns)
- Dataset is publicly available for research purposes

---

## Calculated Fields

The preprocessing script adds these fields:

| Column | Calculation | Description |
|--------|-------------|-------------|
| Revenue | Quantity × Price | Transaction value in GBP |
| Year | Year from InvoiceDate | For YoY analysis |
| Month | Month from InvoiceDate | For seasonality analysis |
| YearMonth | Period (YYYY-MM) | For monthly aggregation |
| DayOfWeek | 0-6 (Mon-Sun) | For day-of-week patterns |
| Hour | 0-23 | For hourly patterns |
