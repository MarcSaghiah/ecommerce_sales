"""
E-commerce Sales Dashboard
Interactive dashboard for analyzing online retail performance.

Run: streamlit run demo/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from io import BytesIO
from fpdf import FPDF

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_loader import load_data, check_data_availability
from metrics import (
    calculate_revenue_metrics,
    calculate_customer_metrics,
    calculate_geographic_metrics,
    calculate_time_metrics,
    format_currency,
    format_percentage,
    format_number
)

# Page config
st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    .insight-box {
        background-color: #e8f4ea;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_data():
    """Load and cache data."""
    try:
        df = load_data(use_sample=False)
        return df
    except FileNotFoundError:
        st.error("⚠️ Data not found. Please run preprocessing first.")
        st.code("python src/preprocessing.py", language="bash")
        st.stop()

def render_specific_country_analysis(df: pd.DataFrame):
    """Detailed analysis for a specific country."""
    st.subheader("🌐 Specific Country Analysis")
    countries = sorted(df['Country'].unique().tolist())
    selected_country = st.selectbox("Select a country to analyze", countries, key="country_analysis")
    country_df = df[df['Country'] == selected_country]
    if country_df.empty:
        st.warning("No data available for this country.")
        return
    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Revenue", format_currency(country_df['Revenue'].sum()))
    with col2:
        st.metric("Unique Customers", country_df['Customer ID'].nunique())
    with col3:
        st.metric("Orders", country_df['Invoice'].nunique())
    # Monthly trend
    monthly = country_df.groupby('YearMonth')['Revenue'].sum().reset_index()
    monthly['YearMonth'] = monthly['YearMonth'].astype(str)
    fig = px.line(monthly, x='YearMonth', y='Revenue', markers=True,
                  title=f"Monthly Revenue Trend - {selected_country}",
                  labels={'Revenue': 'Revenue (£)', 'YearMonth': 'Month'})
    fig.update_layout(xaxis_tickangle=-45, height=350)
    st.plotly_chart(fig, use_container_width=True)
    # Top products
    st.markdown("**Top Products**")
    top_products = country_df.groupby(['StockCode', 'Description'])['Revenue'].sum().reset_index()
    top_products = top_products.sort_values('Revenue', ascending=False).head(5)
    st.dataframe(top_products[['Description', 'Revenue']], hide_index=True)


def render_kpi_cards(metrics: dict):
    """Render the top KPI cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=format_currency(metrics['revenue']['total_revenue']),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Customers",
            value=format_number(metrics['customers']['total_customers']),
            delta=f"{metrics['customers']['repeat_rate']:.1f}% repeat"
        )
    
    with col3:
        st.metric(
            label="Avg Order Value",
            value=format_currency(metrics['customers']['avg_aov']),
            delta=None
        )
    
    with col4:
        st.metric(
            label="Countries",
            value=metrics['geographic']['total_countries'],
            delta=f"UK: {metrics['geographic']['uk_share']:.0f}%"
        )


def render_revenue_trend(df: pd.DataFrame):
    """Render monthly revenue trend chart."""
    st.subheader("📈 Monthly Revenue Trend")
    
    monthly = df.groupby('YearMonth')['Revenue'].sum().reset_index()
    monthly['YearMonth'] = monthly['YearMonth'].astype(str)
    
    fig = px.area(
        monthly,
        x='YearMonth',
        y='Revenue',
        title=None,
        labels={'Revenue': 'Revenue (£)', 'YearMonth': 'Month'}
    )
    
    fig.update_traces(
        fill='tozeroy',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        margin=dict(l=50, r=50, t=30, b=80)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insight box
    peak_month = monthly.loc[monthly['Revenue'].idxmax()]
    st.markdown(f"""
    <div class="insight-box">
        <strong>💡 Insight:</strong> Peak revenue was in <strong>{peak_month['YearMonth']}</strong> 
        with <strong>{format_currency(peak_month['Revenue'])}</strong>. 
        November consistently shows 2-3x higher sales due to holiday shopping.
    </div>
    """, unsafe_allow_html=True)


def render_geographic_analysis(df: pd.DataFrame, metrics: dict):
    """Render geographic breakdown."""
    st.subheader("🌍 Revenue by Country")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Map or bar chart of top countries
        country_data = metrics['geographic']['country_data'].head(10)
        
        fig = px.bar(
            country_data,
            x='Revenue',
            y='Country',
            orientation='h',
            title=None,
            labels={'Revenue': 'Revenue (£)', 'Country': ''}
        )
        
        fig.update_traces(marker_color='#1f77b4')
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=400,
            margin=dict(l=100, r=50, t=30, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # UK vs International pie chart
        uk_int_data = pd.DataFrame({
            'Region': ['United Kingdom', 'International'],
            'Revenue': [
                metrics['geographic']['uk_revenue'],
                metrics['geographic']['international_revenue']
            ]
        })
        
        fig = px.pie(
            uk_int_data,
            values='Revenue',
            names='Region',
            title='UK vs International',
            color_discrete_sequence=['#1f77b4', '#ff7f0e']
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top 3 international markets
        st.markdown("**Top International Markets:**")
        intl = metrics['geographic']['country_data']
        intl = intl[intl['Country'] != 'United Kingdom'].head(3)
        for _, row in intl.iterrows():
            st.markdown(f"• {row['Country']}: {format_currency(row['Revenue'])}")


def render_customer_segments(df: pd.DataFrame):
    """Render RFM customer segmentation."""
    st.subheader("👥 Customer Segments (RFM Analysis)")
    
    # Calculate simple segmentation
    customer_stats = df.groupby('Customer ID').agg({
        'Revenue': 'sum',
        'Invoice': 'nunique'
    }).reset_index()
    
    # Create segments based on revenue quartiles
    customer_stats['Segment'] = pd.qcut(
        customer_stats['Revenue'],
        q=4,
        labels=['Low Value', 'Medium Value', 'High Value', 'Champions']
    )
    
    segment_summary = customer_stats.groupby('Segment').agg({
        'Customer ID': 'count',
        'Revenue': 'sum'
    }).reset_index()
    segment_summary.columns = ['Segment', 'Customers', 'Revenue']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            segment_summary,
            x='Segment',
            y='Customers',
            title='Customers by Segment',
            color='Segment',
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            segment_summary,
            x='Segment',
            y='Revenue',
            title='Revenue by Segment',
            color='Segment',
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Insight
    champions = segment_summary[segment_summary['Segment'] == 'Champions'].iloc[0]
    total_rev = segment_summary['Revenue'].sum()
    champ_pct = champions['Revenue'] / total_rev * 100
    
    st.markdown(f"""
    <div class="insight-box">
        <strong>💡 Insight:</strong> The top 25% of customers ("Champions") generate 
        <strong>{champ_pct:.0f}%</strong> of total revenue. 
        Focus retention efforts on this segment.
    </div>
    """, unsafe_allow_html=True)


def render_time_patterns(df: pd.DataFrame, metrics: dict):
    """Render time-based patterns."""
    st.subheader("⏰ Sales Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Day of week
        dow_data = metrics['time']['dow_data']
        
        fig = px.bar(
            dow_data,
            x='DayName',
            y='Revenue',
            title='Revenue by Day of Week',
            color='Revenue',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            showlegend=False,
            height=350,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Hour of day
        hour_data = metrics['time']['hourly_data']
        
        fig = px.line(
            hour_data,
            x='Hour',
            y='Revenue',
            title='Revenue by Hour of Day',
            markers=True
        )
        fig.update_traces(line_color='#ff7f0e')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    <div class="insight-box">
        <strong>💡 Insight:</strong> Peak sales occur on <strong>{metrics['time']['peak_day']}</strong> 
        at <strong>{metrics['time']['peak_hour']}:00</strong>. 
        Schedule marketing campaigns and promotions around these times.
    </div>
    """, unsafe_allow_html=True)


def render_top_products(df: pd.DataFrame):
    """Render top products analysis."""
    st.subheader("🏆 Top Products")
    
    product_stats = df.groupby(['StockCode', 'Description']).agg({
        'Revenue': 'sum',
        'Quantity': 'sum',
        'Invoice': 'nunique'
    }).reset_index()
    product_stats = product_stats.sort_values('Revenue', ascending=False).head(10)
    
    fig = px.bar(
        product_stats,
        x='Revenue',
        y='Description',
        orientation='h',
        title=None,
        labels={'Revenue': 'Revenue (£)', 'Description': ''}
    )
    
    fig.update_traces(marker_color='#2ca02c')
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=400,
        margin=dict(l=200, r=50, t=30, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_sidebar_filters(df: pd.DataFrame):
    """Render sidebar filters."""
    st.sidebar.header("🎛️ Filters")
    
    # Date range
    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Country filter
    countries = ['All'] + sorted(df['Country'].unique().tolist())
    selected_country = st.sidebar.selectbox("Country", countries)
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['InvoiceDate'].dt.date >= date_range[0]) &
            (filtered_df['InvoiceDate'].dt.date <= date_range[1])
        ]
    
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    
    # Show filter summary
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Filtered Data:**")
    st.sidebar.markdown(f"• {len(filtered_df):,} transactions")
    st.sidebar.markdown(f"• {filtered_df['Customer ID'].nunique():,} customers")
    st.sidebar.markdown(f"• {format_currency(filtered_df['Revenue'].sum())} revenue")
    
    return filtered_df

def render_category_analysis(df: pd.DataFrame):
    """Product Category Analysis (if the column exists)."""
    st.subheader("🗂️ Product Category Analysis")
    if 'Category' not in df.columns:
        st.info("Add a 'Category' column to your data to enable this analysis.")
        return
    categories = sorted(df['Category'].dropna().unique().tolist())
    selected_category = st.selectbox("Select a category to analyze", ['All'] + categories, key="category_analysis")
    cat_df = df.copy()
    if selected_category != 'All':
        cat_df = cat_df[cat_df['Category'] == selected_category]
    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Revenue", format_currency(cat_df['Revenue'].sum()))
    with col2:
        st.metric("Unique Products", cat_df['StockCode'].nunique())
    with col3:
        st.metric("Orders", cat_df['Invoice'].nunique())
    # Monthly trend
    monthly = cat_df.groupby('YearMonth')['Revenue'].sum().reset_index()
    monthly['YearMonth'] = monthly['YearMonth'].astype(str)
    fig = px.line(monthly, x='YearMonth', y='Revenue', markers=True,
                  title=f"Monthly Revenue Trend - {selected_category if selected_category != 'All' else 'All Categories'}",
                  labels={'Revenue': 'Revenue (£)', 'YearMonth': 'Month'})
    fig.update_layout(xaxis_tickangle=-45, height=350)
    st.plotly_chart(fig, use_container_width=True)
    # Top products
    st.markdown("**Top Products in Category**")
    top_products = cat_df.groupby(['StockCode', 'Description'])['Revenue'].sum().reset_index()
    top_products = top_products.sort_values('Revenue', ascending=False).head(5)
    st.dataframe(top_products[['Description', 'Revenue']], hide_index=True)


def render_cohort_analysis(df: pd.DataFrame):
    """Cohort Analysis: client retention heatmap by month of first order."""
    st.subheader("📊 Cohort Analysis (Customer Retention)")
    # Cohort calculation
    df = df.copy()
    df['CohortMonth'] = df.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
    df['OrderMonth'] = df['InvoiceDate'].dt.to_period('M')
    df['CohortIndex'] = (df['OrderMonth'] - df['CohortMonth']).apply(lambda x: x.n)
    cohort_data = df.groupby(['CohortMonth', 'CohortIndex'])['Customer ID'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='Customer ID')
    cohort_size = cohort_pivot.iloc[:,0]
    retention = cohort_pivot.divide(cohort_size, axis=0).round(3)
    import plotly.figure_factory as ff
    z = retention.fillna(0).values
    x = retention.columns.astype(str).tolist()
    y = retention.index.astype(str).tolist()
    fig = ff.create_annotated_heatmap(z, x=x, y=y, colorscale='Blues', showscale=True,
        annotation_text=(100*retention.fillna(0)).astype(int).astype(str)+"%")
    fig.update_layout(
        title="Customer Retention by Cohort Month",
        xaxis_title="Cohort Age (Months)",
        yaxis_title="Cohort Month",
        height=500,
        margin=dict(l=100, r=50, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    <div class="insight-box">
        <strong>💡 Insight :</strong> This heatmap shows customer retention by cohort month.<br>
        The darker the color remains to the right, the better the retention.<br>
        Monitor cohorts that maintain a high rate for several months: these are your most loyal customers.<br>
        If retention drops quickly, consider strengthening your loyalty actions (follow-ups, offers, etc.).
    </div>
    """, unsafe_allow_html=True)
    

def render_forecasting(df: pd.DataFrame):
    """Sales forecasting with Prophet (if available)."""
    st.subheader("🔮 Sales Forecasting")
    try:
        from prophet import Prophet
        import plotly.graph_objs as go
        # Data preparation
        ts = df.groupby(df['InvoiceDate'].dt.to_period('M'))['Revenue'].sum().reset_index()
        ts.columns = ['ds', 'y']
        ts['ds'] = ts['ds'].astype(str)
        # Model
        model = Prophet()
        model.fit(ts)
        future = model.make_future_dataframe(periods=6, freq='M')
        forecast = model.predict(future)
        # Display
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ts['ds'], y=ts['y'], mode='lines+markers', name='Historical'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'))
        fig.update_layout(title='Sales Forecast (next 6 months)', xaxis_title='Month', yaxis_title='Revenue (£)', height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
    <div class="insight-box">
        <strong>💡 Insight :</strong> This curve shows the sales forecast for the next 6 months according to Prophet.<br>
        Use this trend to anticipate peaks or drops in revenue and adjust your business actions accordingly.
    </div>
    """, unsafe_allow_html=True)
    except ImportError:
        st.info("To enable forecasting, install the prophet package: pip install prophet")

def generate_pdf_report_full(metrics, filtered_df):
    # Préparation des données pour le rapport
    kpis = {
        'Total Revenue': format_currency(metrics['revenue']['total_revenue']),
        'Total Customers': format_number(metrics['customers']['total_customers']),
        'YoY Growth': f"{metrics['revenue'].get('yoy_growth', 'N/A')}%",
        'Avg Order Value': format_currency(metrics['customers']['avg_aov']),
        'Repeat Rate': f"{metrics['customers']['repeat_rate']:.1f}%"
    }
    top_products = []
    if 'product_data' in metrics['products']:
        for _, row in metrics['products']['product_data'].head(5).iterrows():
            top_products.append((row['Description'], format_currency(row['Revenue'])))
    else:
        top_products = [('N/A', 'N/A')]
    top_countries = []
    if 'country_data' in metrics['geographic']:
        for _, row in metrics['geographic']['country_data'].head(5).iterrows():
            top_countries.append((row['Country'], format_currency(row['Revenue'])))
    else:
        top_countries = [('N/A', 'N/A')]
    # Forecast (extraction simple)
    forecast = []
    try:
        from prophet import Prophet
        ts = filtered_df.groupby(filtered_df['InvoiceDate'].dt.to_period('M'))['Revenue'].sum().reset_index()
        ts.columns = ['ds', 'y']
        ts['ds'] = ts['ds'].astype(str)
        model = Prophet()
        model.fit(ts)
        future = model.make_future_dataframe(periods=6, freq='M')
        pred = model.predict(future)
        for i in range(-6, 0):
            month = pred['ds'].iloc[i]
            value = format_currency(pred['yhat'].iloc[i])
            forecast.append((month, value))
    except Exception:
        forecast = [('N/A', 'N/A')]*6
    # Génération du PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Monthly Sales Executive Summary', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Key Metrics', 0, 1)
    pdf.set_font('Arial', '', 11)
    for kpi, value in kpis.items():
        pdf.cell(0, 8, f'{kpi}: {value}', 0, 1)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Top Products', 0, 1)
    pdf.set_font('Arial', '', 11)
    for desc, rev in top_products:
        pdf.cell(0, 8, f'{desc}: {rev}', 0, 1)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Top Countries', 0, 1)
    pdf.set_font('Arial', '', 11)
    for country, rev in top_countries:
        pdf.cell(0, 8, f'{country}: {rev}', 0, 1)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Sales Forecast (next 6 months)', 0, 1)
    pdf.set_font('Arial', '', 11)
    for month, value in forecast:
        pdf.cell(0, 8, f'{month}: {value}', 0, 1)
    pdf.ln(10)
    from datetime import datetime
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 8, f'Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'R')
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

def main():
        
    """Main application."""
    
    # Header
    st.title("🛒 E-commerce Sales Dashboard")
    st.markdown("*Analyzing UK Online Retail Performance (2009-2011)*")
    st.markdown("---")
    # Load data
    st.subheader("📄 Download Executive Summary Report (PDF)")
    # Chargement des données et filtres
    df = get_data()
    filtered_df = render_sidebar_filters(df)
    # Calcul des métriques
    metrics = {
        'revenue': calculate_revenue_metrics(filtered_df),
        'customers': calculate_customer_metrics(filtered_df),
        'geographic': calculate_geographic_metrics(filtered_df),
        'time': calculate_time_metrics(filtered_df),
        'products': {'product_data': filtered_df.groupby(['StockCode', 'Description'])['Revenue'].sum().reset_index()}
    }
    pdf_buffer = generate_pdf_report_full(metrics, filtered_df)
    st.download_button(
        label="Download PDF Report",
        data=pdf_buffer,
        file_name="executive_summary.pdf",
        mime="application/pdf"
    )

    # Affichage complet du dashboard
    st.markdown("---")
    render_kpi_cards(metrics)
    st.markdown("---")
    render_revenue_trend(filtered_df)
    st.markdown("---")
    render_geographic_analysis(filtered_df, metrics)
    st.markdown("---")
    render_customer_segments(filtered_df)
    st.markdown("---")
    render_time_patterns(filtered_df, metrics)
    st.markdown("---")
    render_top_products(filtered_df)
    st.markdown("---")
    render_specific_country_analysis(filtered_df)
    st.markdown("---")
    render_category_analysis(filtered_df)
    # st.markdown("---")
    # render_cohort_analysis(filtered_df)
    st.markdown("---")
    render_forecasting(filtered_df)


    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>📊 Data Source: UCI Machine Learning Repository - Online Retail II Dataset</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
