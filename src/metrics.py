"""
Metrics Module
KPI calculations and business metrics for the e-commerce dashboard.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def calculate_revenue_metrics(df: pd.DataFrame) -> Dict:
    """Calculate revenue-related KPIs."""
    
    total_revenue = df['Revenue'].sum()
    
    # Monthly metrics
    monthly = df.groupby('YearMonth').agg({
        'Revenue': 'sum',
        'Invoice': 'nunique',
        'Customer ID': 'nunique'
    }).reset_index()
    monthly.columns = ['YearMonth', 'Revenue', 'Orders', 'Customers']
    
    # Growth rates
    monthly['Revenue_Growth'] = monthly['Revenue'].pct_change() * 100
    monthly['Orders_Growth'] = monthly['Orders'].pct_change() * 100
    
    return {
        'total_revenue': total_revenue,
        'avg_monthly_revenue': monthly['Revenue'].mean(),
        'best_month': monthly.loc[monthly['Revenue'].idxmax(), 'YearMonth'],
        'best_month_revenue': monthly['Revenue'].max(),
        'worst_month': monthly.loc[monthly['Revenue'].idxmin(), 'YearMonth'],
        'worst_month_revenue': monthly['Revenue'].min(),
        'monthly_data': monthly
    }


def calculate_customer_metrics(df: pd.DataFrame) -> Dict:
    """Calculate customer-related KPIs."""
    
    # Customer aggregates
    customer_stats = df.groupby('Customer ID').agg({
        'Revenue': 'sum',
        'Invoice': 'nunique',
        'InvoiceDate': ['min', 'max']
    })
    customer_stats.columns = ['TotalSpend', 'OrderCount', 'FirstPurchase', 'LastPurchase']
    customer_stats = customer_stats.reset_index()
    
    # Customer tenure
    customer_stats['TenureDays'] = (customer_stats['LastPurchase'] - customer_stats['FirstPurchase']).dt.days
    
    # Repeat customers
    repeat_customers = (customer_stats['OrderCount'] > 1).sum()
    total_customers = len(customer_stats)
    
    # Average order value per customer
    customer_stats['AOV'] = customer_stats['TotalSpend'] / customer_stats['OrderCount']
    
    return {
        'total_customers': total_customers,
        'repeat_customers': repeat_customers,
        'repeat_rate': repeat_customers / total_customers * 100,
        'avg_customer_value': customer_stats['TotalSpend'].mean(),
        'median_customer_value': customer_stats['TotalSpend'].median(),
        'avg_orders_per_customer': customer_stats['OrderCount'].mean(),
        'avg_aov': customer_stats['AOV'].mean(),
        'customer_data': customer_stats
    }


def calculate_product_metrics(df: pd.DataFrame) -> Dict:
    """Calculate product-related KPIs."""
    
    # Product performance
    product_stats = df.groupby(['StockCode', 'Description']).agg({
        'Revenue': 'sum',
        'Quantity': 'sum',
        'Invoice': 'nunique',
        'Customer ID': 'nunique'
    }).reset_index()
    product_stats.columns = ['StockCode', 'Description', 'Revenue', 'Quantity', 'Orders', 'Customers']
    product_stats = product_stats.sort_values('Revenue', ascending=False)
    
    # Top products
    top_by_revenue = product_stats.head(20)
    top_by_quantity = product_stats.nlargest(20, 'Quantity')
    
    return {
        'total_products': product_stats['StockCode'].nunique(),
        'top_products_by_revenue': top_by_revenue,
        'top_products_by_quantity': top_by_quantity,
        'avg_revenue_per_product': product_stats['Revenue'].mean(),
        'product_data': product_stats
    }


def calculate_geographic_metrics(df: pd.DataFrame) -> Dict:
    """Calculate geographic KPIs."""
    
    # Country performance
    country_stats = df.groupby('Country').agg({
        'Revenue': 'sum',
        'Invoice': 'nunique',
        'Customer ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    country_stats.columns = ['Country', 'Revenue', 'Orders', 'Customers', 'Quantity']
    country_stats = country_stats.sort_values('Revenue', ascending=False)
    
    # Market share
    total_revenue = country_stats['Revenue'].sum()
    country_stats['MarketShare'] = country_stats['Revenue'] / total_revenue * 100
    
    # UK vs International
    uk_revenue = country_stats[country_stats['Country'] == 'United Kingdom']['Revenue'].sum()
    international_revenue = total_revenue - uk_revenue
    
    return {
        'total_countries': len(country_stats),
        'uk_revenue': uk_revenue,
        'uk_share': uk_revenue / total_revenue * 100,
        'international_revenue': international_revenue,
        'top_countries': country_stats.head(10),
        'country_data': country_stats
    }


def calculate_time_metrics(df: pd.DataFrame) -> Dict:
    """Calculate time-based patterns."""
    
    # Day of week analysis
    dow_stats = df.groupby('DayOfWeek').agg({
        'Revenue': 'sum',
        'Invoice': 'nunique'
    }).reset_index()
    dow_stats['DayName'] = dow_stats['DayOfWeek'].map({
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    })
    
    # Hour analysis
    hour_stats = df.groupby('Hour').agg({
        'Revenue': 'sum',
        'Invoice': 'nunique'
    }).reset_index()
    
    # Peak times
    peak_day = dow_stats.loc[dow_stats['Revenue'].idxmax(), 'DayName']
    peak_hour = hour_stats.loc[hour_stats['Revenue'].idxmax(), 'Hour']
    
    return {
        'peak_day': peak_day,
        'peak_hour': peak_hour,
        'dow_data': dow_stats,
        'hourly_data': hour_stats
    }


def calculate_yoy_growth(df: pd.DataFrame) -> Dict:
    """Calculate year-over-year growth metrics."""
    
    # Filter to comparable periods (same months in both years)
    df_2010 = df[df['InvoiceDate'].dt.year == 2010]
    df_2011 = df[df['InvoiceDate'].dt.year == 2011]
    
    # Only compare overlapping months
    months_2010 = set(df_2010['Month'].unique())
    months_2011 = set(df_2011['Month'].unique())
    common_months = months_2010.intersection(months_2011)
    
    df_2010_comparable = df_2010[df_2010['Month'].isin(common_months)]
    df_2011_comparable = df_2011[df_2011['Month'].isin(common_months)]
    
    revenue_2010 = df_2010_comparable['Revenue'].sum()
    revenue_2011 = df_2011_comparable['Revenue'].sum()
    
    yoy_growth = (revenue_2011 - revenue_2010) / revenue_2010 * 100 if revenue_2010 > 0 else 0
    
    return {
        'revenue_2010': revenue_2010,
        'revenue_2011': revenue_2011,
        'yoy_growth': yoy_growth,
        'comparable_months': len(common_months)
    }


def get_all_metrics(df: pd.DataFrame) -> Dict:
    """Calculate all metrics and return as a single dictionary."""
    
    return {
        'revenue': calculate_revenue_metrics(df),
        'customers': calculate_customer_metrics(df),
        'products': calculate_product_metrics(df),
        'geographic': calculate_geographic_metrics(df),
        'time': calculate_time_metrics(df),
        'yoy': calculate_yoy_growth(df)
    }


def format_currency(value: float, currency: str = '£') -> str:
    """Format a number as currency."""
    if value >= 1_000_000:
        return f"{currency}{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{currency}{value/1_000:.1f}K"
    else:
        return f"{currency}{value:.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a number as percentage."""
    return f"{value:.{decimals}f}%"


def format_number(value: float) -> str:
    """Format a large number with commas."""
    return f"{value:,.0f}"
