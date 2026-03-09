"""
Generate Sample Data
Creates a realistic sample dataset for testing without the full UCI download.
Run: python data/sample/generate_sample.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
N_TRANSACTIONS = 10000
START_DATE = datetime(2010, 1, 1)
END_DATE = datetime(2011, 12, 9)

# Sample products (realistic gift items from the actual dataset)
PRODUCTS = [
    ('85123A', 'WHITE HANGING HEART T-LIGHT HOLDER', 2.55),
    ('71053', 'WHITE METAL LANTERN', 3.39),
    ('84406B', 'CREAM CUPID HEARTS COAT HANGER', 2.75),
    ('84029G', 'KNITTED UNION FLAG HOT WATER BOTTLE', 3.39),
    ('84029E', 'RED WOOLLY HOTTIE WHITE HEART', 3.39),
    ('22752', 'SET 7 BABUSHKA NESTING BOXES', 7.65),
    ('21730', 'GLASS STAR FROSTED T-LIGHT HOLDER', 4.25),
    ('22633', 'HAND WARMER UNION JACK', 1.85),
    ('22632', 'HAND WARMER RED POLKA DOT', 1.85),
    ('84879', 'ASSORTED COLOUR BIRD ORNAMENT', 1.69),
    ('22745', 'POPPY\'S PLAYHOUSE BEDROOM', 2.10),
    ('22748', 'POPPY\'S PLAYHOUSE KITCHEN', 2.10),
    ('22749', 'FELTCRAFT PRINCESS CHARLOTTE DOLL', 3.75),
    ('22310', 'PANTRY MAGNETIC SHOPPING LIST', 1.95),
    ('84997B', 'RED 3 PIECE RETROSPOT CUTLERY SET', 4.15),
    ('22623', 'BOX OF VINTAGE JIGSAW BLOCKS', 4.95),
    ('22622', 'BOX OF VINTAGE ALPHABET BLOCKS', 4.95),
    ('21754', 'HOME BUILDING BLOCK WORD', 5.95),
    ('21755', 'LOVE BUILDING BLOCK WORD', 5.95),
    ('21777', 'RECIPE BOX WITH METAL HEART', 7.95),
    ('48187', 'DOORMAT NEW ENGLAND', 7.95),
    ('22469', 'HEART OF WICKER SMALL', 1.65),
    ('21212', 'PACK OF 72 RETROSPOT CAKE CASES', 0.55),
    ('22835', 'HOT WATER BOTTLE I AM SO POORLY', 4.95),
    ('22423', 'REGENCY CAKESTAND 3 TIER', 12.75),
    ('22720', 'SET OF 3 CAKE TINS PANTRY DESIGN', 4.95),
    ('47566', 'PARTY BUNTING', 4.95),
    ('84997D', 'BLUE 3 PIECE POLKADOT CUTLERY SET', 4.15),
    ('23298', 'SPOTTY BUNTING', 4.95),
    ('23300', 'GARDENERS KNEELING PAD CUP OF TEA', 2.10),
    ('22386', 'JUMBO BAG PINK POLKADOT', 1.95),
    ('22382', 'LUNCH BAG SPACEBOY DESIGN', 1.65),
    ('22384', 'LUNCH BAG PINK POLKADOT', 1.65),
    ('22726', 'ALARM CLOCK BAKELIKE GREEN', 3.75),
    ('22727', 'ALARM CLOCK BAKELIKE RED', 3.75),
    ('22728', 'ALARM CLOCK BAKELIKE PINK', 3.75),
    ('22730', 'ALARM CLOCK BAKELIKE IVORY', 3.75),
    ('20725', 'LUNCH BAG RED RETROSPOT', 1.65),
    ('20727', 'LUNCH BAG BLACK SKULL', 1.65),
    ('22383', 'LUNCH BAG SUKI DESIGN', 1.65),
    ('22197', 'POPCORN HOLDER', 0.85),
    ('22198', 'SMALL HEART FLOWERS HOOK', 0.85),
    ('POST', 'POSTAGE', 18.00),
    ('DOT', 'DOTCOM POSTAGE', 15.00),
    ('M', 'MANUAL', 0.00),
    ('85099B', 'JUMBO BAG RED RETROSPOT', 1.95),
    ('85099C', 'JUMBO BAG STRAWBERRY', 1.95),
    ('23084', 'RABBIT NIGHT LIGHT', 1.85),
    ('23166', 'MEDIUM CERAMIC TOP STORAGE JAR', 1.25),
    ('23167', 'SMALL CERAMIC TOP STORAGE JAR', 0.85),
]

# Countries with weights (UK dominant, matches real distribution)
COUNTRIES = [
    ('United Kingdom', 0.82),
    ('Germany', 0.04),
    ('France', 0.03),
    ('EIRE', 0.02),
    ('Netherlands', 0.015),
    ('Belgium', 0.015),
    ('Spain', 0.01),
    ('Switzerland', 0.008),
    ('Portugal', 0.006),
    ('Italy', 0.005),
    ('Australia', 0.005),
    ('Norway', 0.004),
    ('Sweden', 0.004),
    ('Japan', 0.003),
    ('Finland', 0.003),
    ('Denmark', 0.003),
    ('Channel Islands', 0.002),
    ('Poland', 0.002),
    ('Cyprus', 0.005),  # Total = 1.0
]

def generate_customers(n_customers=500):
    """Generate customer IDs with varying purchase frequencies."""
    # Some customers buy frequently, most buy rarely (power law)
    customer_ids = list(range(12346, 12346 + n_customers))
    # Assign purchase probability weights (power law distribution)
    weights = np.random.pareto(1.5, n_customers) + 1
    weights = weights / weights.sum()
    return customer_ids, weights

def generate_invoice_date():
    """Generate a random date with seasonal weighting (more in Nov-Dec)."""
    # Generate base date
    days_range = (END_DATE - START_DATE).days
    
    # Weight towards November and December (holiday season)
    month_weights = [0.06, 0.06, 0.07, 0.07, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.12, 0.12]
    month = np.random.choice(range(1, 13), p=month_weights)
    
    # Random day in that month
    if month == 2:
        day = random.randint(1, 28)
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30)
    else:
        day = random.randint(1, 31)
    
    # Random year (2010 or 2011)
    year = random.choice([2010, 2011])
    
    try:
        date = datetime(year, month, day)
    except ValueError:
        date = datetime(year, month, 28)  # Fallback for invalid dates
    
    # Add time (business hours weighted - peak around lunch)
    hour_weights = [0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 
                    0.12, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.03, 0.02, 0.01, 
                    0.005, 0.005, 0.005, 0.005]
    # Normalize to sum to 1
    hour_weights = np.array(hour_weights) / sum(hour_weights)
    hour = np.random.choice(range(24), p=hour_weights)
    minute = random.randint(0, 59)
    
    return date.replace(hour=hour, minute=minute)

def generate_sample_data():
    """Generate the complete sample dataset."""
    print("🔄 Generating sample data...")
    
    # Generate customers
    customer_ids, customer_weights = generate_customers(500)
    
    # Generate invoices (groups of items)
    n_invoices = N_TRANSACTIONS // 5  # Average 5 items per invoice
    
    transactions = []
    invoice_num = 536365  # Starting invoice number (matches real data)
    
    for _ in range(n_invoices):
        # Generate invoice details
        invoice_id = str(invoice_num)
        invoice_date = generate_invoice_date()
        customer_id = np.random.choice(customer_ids, p=customer_weights)
        country = np.random.choice([c[0] for c in COUNTRIES], p=[c[1] for c in COUNTRIES])
        
        # Number of items in this invoice (1-12, weighted towards smaller)
        n_items = np.random.choice(range(1, 13), p=[0.25, 0.20, 0.15, 0.12, 0.08, 0.06, 0.05, 0.03, 0.02, 0.02, 0.01, 0.01])
        
        # Select products for this invoice
        selected_products = random.sample(PRODUCTS, min(n_items, len(PRODUCTS)))
        
        for product in selected_products:
            stock_code, description, unit_price = product
            
            # Quantity (1-24, weighted towards smaller)
            if unit_price < 1:
                quantity = np.random.choice(range(1, 73), p=np.array([1/(i+1) for i in range(72)]) / sum([1/(i+1) for i in range(72)]))
            else:
                quantity = np.random.choice(range(1, 25), p=np.array([1/(i+1) for i in range(24)]) / sum([1/(i+1) for i in range(24)]))
            
            # Small price variation (+/- 10%)
            price = unit_price * (1 + np.random.uniform(-0.1, 0.1))
            price = round(price, 2)
            
            transactions.append({
                'Invoice': invoice_id,
                'StockCode': stock_code,
                'Description': description,
                'Quantity': quantity,
                'InvoiceDate': invoice_date,
                'Price': price,
                'Customer ID': customer_id,
                'Country': country
            })
        
        invoice_num += 1
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    
    # Sort by date
    df = df.sort_values('InvoiceDate').reset_index(drop=True)
    
    # Add calculated fields (matching preprocessing.py output)
    df['Revenue'] = df['Quantity'] * df['Price']
    df['Year'] = df['InvoiceDate'].dt.year
    df['Month'] = df['InvoiceDate'].dt.month
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    df['DayOfWeek'] = df['InvoiceDate'].dt.dayofweek
    df['Hour'] = df['InvoiceDate'].dt.hour
    
    print(f"✅ Generated {len(df):,} transactions")
    print(f"   - {df['Invoice'].nunique():,} invoices")
    print(f"   - {df['Customer ID'].nunique():,} customers")
    print(f"   - {df['Country'].nunique()} countries")
    print(f"   - Date range: {df['InvoiceDate'].min().date()} to {df['InvoiceDate'].max().date()}")
    print(f"   - Total revenue: £{df['Revenue'].sum():,.2f}")
    
    return df

def main():
    """Generate and save sample data."""
    # Generate data
    df = generate_sample_data()
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save to CSV
    output_path = os.path.join(script_dir, 'sample_data.csv')
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved to: {output_path}")
    
    # Also save to processed folder for immediate use
    processed_dir = os.path.join(script_dir, '..', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    df.to_csv(os.path.join(processed_dir, 'cleaned_transactions.csv'), index=False)
    print(f"💾 Also saved to: data/processed/cleaned_transactions.csv")
    
    return df

if __name__ == '__main__':
    main()
