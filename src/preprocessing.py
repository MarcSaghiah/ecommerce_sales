"""
Data Preprocessing Module
Cleans and prepares the Online Retail II dataset for analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import warnings
warnings.filterwarnings('ignore')


def load_raw_data(filepath: str) -> pd.DataFrame:
    """Load raw data from Excel file."""
    print(f"📂 Loading data from {filepath}...")
    
    # The dataset has two sheets: Year 2009-2010 and Year 2010-2011
    df1 = pd.read_excel(filepath, sheet_name='Year 2009-2010')
    df2 = pd.read_excel(filepath, sheet_name='Year 2010-2011')
    
    df = pd.concat([df1, df2], ignore_index=True)
    print(f"   Loaded {len(df):,} rows")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataset:
    - Remove cancellations (InvoiceNo starting with 'C')
    - Remove rows with missing CustomerID
    - Remove negative quantities and prices
    - Remove outliers
    - Add calculated fields
    """
    print("🧹 Cleaning data...")
    initial_rows = len(df)
    
    # Standardize column names
    df.columns = df.columns.str.strip()
    
    # Remove cancellations
    df = df[~df['Invoice'].astype(str).str.startswith('C')]
    print(f"   Removed cancellations: {initial_rows - len(df):,} rows")
    
    # Remove missing CustomerID
    rows_before = len(df)
    df = df.dropna(subset=['Customer ID'])
    print(f"   Removed missing CustomerID: {rows_before - len(df):,} rows")
    
    # Remove negative/zero quantities and prices
    rows_before = len(df)
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    print(f"   Removed invalid quantity/price: {rows_before - len(df):,} rows")
    
    # Remove extreme outliers (keep 99th percentile)
    rows_before = len(df)
    quantity_cap = df['Quantity'].quantile(0.99)
    price_cap = df['Price'].quantile(0.99)
    df = df[(df['Quantity'] <= quantity_cap) & (df['Price'] <= price_cap)]
    print(f"   Removed outliers: {rows_before - len(df):,} rows")
    
    # Convert types
    df['Customer ID'] = df['Customer ID'].astype(int)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Add calculated fields
    df['Revenue'] = df['Quantity'] * df['Price']
    df['Year'] = df['InvoiceDate'].dt.year
    df['Month'] = df['InvoiceDate'].dt.month
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    df['DayOfWeek'] = df['InvoiceDate'].dt.dayofweek
    df['Hour'] = df['InvoiceDate'].dt.hour
    
    # Ajout des catégories produits
    categories_path = Path(__file__).parent.parent / 'data' / 'product_categories.csv'
    if categories_path.exists():
        categories = pd.read_csv(categories_path)
        df = df.merge(categories, on='StockCode', how='left')
        print(f"   Product categories merged: {df['Category'].notnull().sum()} rows with category")
    else:
        print("   Product categories file not found. Skipping category merge.")
    print(f"✅ Cleaning complete: {len(df):,} rows remaining ({len(df)/initial_rows*100:.1f}%)")
    return df


def create_sample(df: pd.DataFrame, n_rows: int = 10000, seed: int = 42) -> pd.DataFrame:
    """Create a deterministic sample for quick testing."""
    np.random.seed(seed)
    sample = df.sample(n=min(n_rows, len(df)), random_state=seed)
    return sample.sort_values('InvoiceDate')


def calculate_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate RFM (Recency, Frequency, Monetary) scores for customer segmentation.
    """
    print("📊 Calculating RFM scores...")
    
    # Reference date (day after last transaction)
    reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    
    # Calculate RFM metrics per customer
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
        'Invoice': 'nunique',  # Frequency
        'Revenue': 'sum'  # Monetary
    }).reset_index()
    
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    
    # Score each metric (1-5, where 5 is best)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1])
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    
    # Combined RFM Score
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    # Segment labels
    def segment_customer(row):
        r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])
        
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'New Customers'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'Lost'
        else:
            return 'Potential Loyalists'
    
    rfm['Segment'] = rfm.apply(segment_customer, axis=1)
    
    print(f"   Segmented {len(rfm):,} customers")
    return rfm


def generate_summary_stats(df: pd.DataFrame) -> dict:
    """Generate summary statistics for the dashboard."""
    stats = {
        'total_revenue': df['Revenue'].sum(),
        'total_transactions': df['Invoice'].nunique(),
        'total_customers': df['Customer ID'].nunique(),
        'total_products': df['StockCode'].nunique(),
        'avg_order_value': df.groupby('Invoice')['Revenue'].sum().mean(),
        'date_range': {
            'start': df['InvoiceDate'].min().strftime('%Y-%m-%d'),
            'end': df['InvoiceDate'].max().strftime('%Y-%m-%d')
        },
        'top_countries': df.groupby('Country')['Revenue'].sum().nlargest(10).to_dict(),
        'monthly_revenue': df.groupby('YearMonth')['Revenue'].sum().to_dict()
    }
    return stats


def main(use_sample: bool = False):
    """Main preprocessing pipeline."""
    
    # Paths
    project_root = Path(__file__).parent.parent
    raw_data_path = project_root / 'data' / 'raw' / 'online_retail_II.xlsx'
    processed_path = project_root / 'data' / 'processed'
    sample_path = project_root / 'data' / 'sample'
    
    # Create directories
    processed_path.mkdir(parents=True, exist_ok=True)
    sample_path.mkdir(parents=True, exist_ok=True)
    
    # Check if raw data exists
    if not raw_data_path.exists():
        print("⚠️  Raw data not found!")
        print(f"   Please download from: https://archive.ics.uci.edu/dataset/502/online+retail+ii")
        print(f"   And place 'online_retail_II.xlsx' in: {raw_data_path}")
        
        # Try to use sample if available
        sample_file = sample_path / 'sample_data.csv'
        if sample_file.exists():
            print(f"\n📂 Using existing sample data: {sample_file}")
            return
        else:
            print("\n❌ No sample data available. Please download the dataset.")
            return
    
    # Load and clean data
    df = load_raw_data(raw_data_path)
    df = clean_data(df)
    
    # Calculate RFM
    rfm = calculate_rfm(df)
    
    # Save processed data
    print("\n💾 Saving processed data...")
    df.to_csv(processed_path / 'cleaned_transactions.csv', index=False)
    rfm.to_csv(processed_path / 'customer_rfm.csv', index=False)
    
    # Create and save sample
    sample = create_sample(df)
    sample.to_csv(sample_path / 'sample_data.csv', index=False)
    print(f"   Saved sample: {len(sample):,} rows")
    
    # Generate summary
    stats = generate_summary_stats(df)
    print(f"\n📈 Summary Statistics:")
    print(f"   Total Revenue: £{stats['total_revenue']:,.2f}")
    print(f"   Total Transactions: {stats['total_transactions']:,}")
    print(f"   Total Customers: {stats['total_customers']:,}")
    print(f"   Avg Order Value: £{stats['avg_order_value']:.2f}")
    
    print("\n✅ Preprocessing complete!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess Online Retail II dataset')
    parser.add_argument('--sample', action='store_true', help='Use sample data only')
    args = parser.parse_args()
    
    main(use_sample=args.sample)
