import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Pharmaceutical Materials Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('external_data_final.xl.csv')
    
    # Clean data - check if Price_Deviation needs conversion
    if data['Price_Deviation (%)'].dtype == 'object':
        data['Price_Deviation (%)'] = data['Price_Deviation (%)'].str.replace('%', '').astype(float)
    else:
        # It's already numeric
        data['Price_Deviation (%)'] = data['Price_Deviation (%)'].astype(float)
    
    # Convert timestamp
    data['Price_Source_Timestamp'] = pd.to_datetime(data['Price_Source_Timestamp'], format='%d-%m-%Y', errors='coerce')
    return data

df = load_data()

# Sidebar filters
st.sidebar.title("🔍 Filters")

# Material type filter
material_types = ['All'] + list(df['Material_Type'].unique())
selected_material_type = st.sidebar.selectbox("Material Type", material_types)

# Vendor filter
vendors = ['All'] + list(df['Vendor_Name'].unique())
selected_vendor = st.sidebar.selectbox("Vendor", vendors)

# GMP compliance filter
gmp_options = ['All', 'Yes', 'No']
selected_gmp = st.sidebar.selectbox("GMP Compliance", gmp_options)

# Price tier filter
price_tiers = ['All'] + list(df['Price_Tier'].unique())
selected_price_tier = st.sidebar.selectbox("Price Tier", price_tiers)

# Currency filter
currencies = ['All'] + list(df['Currency'].unique())
selected_currency = st.sidebar.selectbox("Currency", currencies)

# Apply filters
filtered_df = df.copy()
if selected_material_type != 'All':
    filtered_df = filtered_df[filtered_df['Material_Type'] == selected_material_type]
if selected_vendor != 'All':
    filtered_df = filtered_df[filtered_df['Vendor_Name'] == selected_vendor]
if selected_gmp != 'All':
    filtered_df = filtered_df[filtered_df['GMP_Compliance'] == selected_gmp]
if selected_price_tier != 'All':
    filtered_df = filtered_df[filtered_df['Price_Tier'] == selected_price_tier]
if selected_currency != 'All':
    filtered_df = filtered_df[filtered_df['Currency'] == selected_currency]

# Main dashboard
st.title("💊 Pharmaceutical Materials Analysis Dashboard")
st.markdown("""
This interactive dashboard provides insights into pharmaceutical material pricing, vendor performance, 
and market trends. Use the filters in the sidebar to customize your view.
""")

# Key metrics
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Materials", len(filtered_df['Material_Name'].unique()))
with col2:
    st.metric("Average Price", f"${filtered_df['Unit_Price_Latest'].mean():.2f}")
with col3:
    st.metric("Average Price Deviation", f"{filtered_df['Price_Deviation (%)'].mean():.2f}%")
with col4:
    gmp_compliant = filtered_df[filtered_df['GMP_Compliance'] == 'Yes'].shape[0]
    st.metric("GMP Compliant Materials", f"{gmp_compliant}/{len(filtered_df)}")

# Tabs for different analyses
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Price Analysis", 
    "🏭 Vendor Analysis", 
    "🧪 Material Insights", 
    "📅 Temporal Analysis",
    "🌐 Currency & Portal Analysis",
    "🔍 Detailed Data"
])

with tab1:
    st.subheader("Price Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution by material type
        fig = px.box(filtered_df, x='Material_Type', y='Unit_Price_Latest', 
                     title='Price Distribution by Material Type',
                     color='Material_Type')
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        *Insight*: This chart shows the price distribution across different material types. 
        Solvents tend to have a wider price range compared to other types, indicating more variability 
        in solvent pricing.
        """)
    
    with col2:
        # Price vs Benchmark comparison
        avg_prices = filtered_df.groupby('Material_Name').agg({
            'Unit_Price_Latest': 'mean',
            'Benchmark_Price': 'mean'
        }).reset_index().melt(id_vars='Material_Name', 
                              value_vars=['Unit_Price_Latest', 'Benchmark_Price'],
                              var_name='Price_Type', value_name='Price')
        
        fig = px.bar(avg_prices, x='Material_Name', y='Price', color='Price_Type',
                     barmode='group', title='Average Price vs Benchmark Price by Material')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        *Insight*: This comparison shows how current prices compare to benchmark prices. 
        Materials with current prices significantly above benchmarks may represent procurement opportunities.
        """)
    
    # Price deviation analysis
    st.subheader("Price Deviation Analysis")
    
    fig = px.scatter(filtered_df, x='Unit_Price_Latest', y='Price_Deviation (%)',
                     color='Material_Type', size='Unit_Price_Latest',
                     hover_data=['Material_Name', 'Vendor_Name'],
                     title='Price vs Deviation (%)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    *Insight*: This scatter plot shows the relationship between price and deviation from benchmark. 
    Higher priced items don't necessarily have higher deviations, suggesting pricing strategies vary by material type.
    """)

with tab2:
    st.subheader("Vendor Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Vendor count by material type
        vendor_counts = filtered_df.groupby(['Vendor_Name', 'Material_Type']).size().reset_index(name='Count')
        fig = px.bar(vendor_counts, x='Vendor_Name', y='Count', color='Material_Type',
                     title='Vendor Offerings by Material Type')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        *Insight*: This chart shows which vendors specialize in certain material types. 
        Some vendors offer a diverse range, while others focus on specific material categories.
        """)
    
    with col2:
        # Average price by vendor
        vendor_prices = filtered_df.groupby('Vendor_Name')['Unit_Price_Latest'].mean().reset_index()
        vendor_prices = vendor_prices.sort_values('Unit_Price_Latest', ascending=False)
        
        fig = px.bar(vendor_prices, x='Unit_Price_Latest', y='Vendor_Name', 
                     title='Average Price by Vendor', orientation='h')
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        *Insight*: Vendors show significant variation in average pricing. 
        This could indicate differences in quality, branding, or market positioning strategies.
        """)
    
    # Vendor GMP compliance
    st.subheader("Vendor GMP Compliance Status")
    
    gmp_stats = filtered_df.groupby('Vendor_Name')['GMP_Compliance'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    ).reset_index(name='GMP_Compliance_Percentage')
    
    fig = px.bar(gmp_stats, x='Vendor_Name', y='GMP_Compliance_Percentage',
                 title='Percentage of GMP Compliant Materials by Vendor')
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    *Insight*: GMP compliance varies significantly across vendors. 
    Some vendors maintain 100% compliance, which is crucial for pharmaceutical manufacturing quality standards.
    """)

with tab3:
    st.subheader("Material-Specific Insights")
    
    # Material selector
    materials = ['All'] + list(df['Material_Name'].unique())
    selected_material = st.selectbox("Select Material", materials, key='material_select')
    
    if selected_material != 'All':
        material_df = filtered_df[filtered_df['Material_Name'] == selected_material]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price distribution for selected material
            fig = px.box(material_df, y='Unit_Price_Latest', 
                         title=f'Price Distribution for {selected_material}')
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"""
            *Insight*: The price distribution for {selected_material} shows the range of prices offered by different vendors. 
            A wide range may indicate opportunities for cost savings through vendor selection.
            """)
        
        with col2:
            # Vendor comparison for selected material
            fig = px.bar(material_df, x='Vendor_Name', y='Unit_Price_Latest',
                         title=f'Vendor Prices for {selected_material}')
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"""
            *Insight*: Different vendors offer {selected_material} at varying price points. 
            This visualization helps identify the most cost-effective suppliers for this material.
            """)
        
        # Specification and grade analysis
        st.subheader(f"Specification and Grade Analysis for {selected_material}")
        
        spec_grade = material_df.groupby(['Specification', 'Material_Grade']).agg({
            'Unit_Price_Latest': 'mean',
            'Vendor_Name': 'count'
        }).reset_index().rename(columns={'Vendor_Name': 'Vendor_Count'})
        
        if len(spec_grade) > 0:
            fig = px.scatter(spec_grade, x='Specification', y='Material_Grade',
                             size='Unit_Price_Latest', color='Vendor_Count',
                             title='Specification vs Grade with Price and Vendor Count',
                             hover_data=['Unit_Price_Latest', 'Vendor_Count'])
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"""
            *Insight*: This chart shows how different specifications and grades of {selected_material} correlate with pricing and vendor availability. 
            Certain combinations may command premium prices or have limited supplier options.
            """)
        else:
            st.warning("Insufficient data for specification and grade analysis.")
    else:
        st.info("Please select a specific material to see detailed analysis.")

with tab4:
    st.subheader("Temporal Analysis")
    
    # Time-based analysis
    if not filtered_df['Price_Source_Timestamp'].isnull().all():
        time_series = filtered_df.groupby('Price_Source_Timestamp').agg({
            'Unit_Price_Latest': 'mean',
            'Material_Name': 'count'
        }).reset_index().rename(columns={'Material_Name': 'Material_Count'})
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add price trace
        fig.add_trace(
            go.Scatter(x=time_series['Price_Source_Timestamp'], 
                      y=time_series['Unit_Price_Latest'], 
                      name="Average Price", mode='lines+markers'),
            secondary_y=False,
        )
        
        # Add count trace
        fig.add_trace(
            go.Bar(x=time_series['Price_Source_Timestamp'], 
                  y=time_series['Material_Count'], 
                  name="Material Count", opacity=0.5),
            secondary_y=True,
        )
        
        fig.update_layout(
            title_text="Price Trends Over Time with Material Count"
        )
        
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Average Price", secondary_y=False)
        fig.update_yaxes(title_text="Material Count", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        *Insight*: This chart shows how prices have evolved over time, along with the number of materials 
        recorded at each time point. Seasonal trends or price spikes may be visible in the data.
        """)
    else:
        st.warning("Insufficient timestamp data for temporal analysis.")

with tab5:
    st.subheader("Currency & Portal Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution by currency
        fig = px.box(filtered_df, x='Currency', y='Unit_Price_Latest', 
                     title='Price Distribution by Currency',
                     color='Currency')
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        *Insight*: This chart shows how prices vary across different currencies. 
        Note that direct comparison should account for exchange rates.
        """)
    
    with col2:
        # Portal validation status
        portal_status = filtered_df['Portal_Validation_Status'].value_counts().reset_index()
        portal_status.columns = ['Status', 'Count']
        
        fig = px.pie(portal_status, values='Count', names='Status',
                     title='Portal Validation Status Distribution')
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        *Insight*: This pie chart shows the proportion of valid vs invalid portal validations. 
        A high percentage of invalid statuses might indicate data quality issues.
        """)
    
    # Supplier portal analysis
    st.subheader("Supplier Portal Analysis")
    
    portal_counts = filtered_df['Supplier_Portal_Name'].value_counts().reset_index()
    portal_counts.columns = ['Portal', 'Count']
    
    fig = px.bar(portal_counts, x='Portal', y='Count',
                 title='Material Count by Supplier Portal')
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    *Insight*: This chart shows which supplier portals are most commonly used for sourcing materials. 
    SAP Ariba appears to be a dominant platform in this dataset.
    """)

with tab6:
    st.subheader("Detailed Data View")
    
    # Additional filters for the data table
    col1, col2 = st.columns(2)
    with col1:
        show_columns = st.multiselect(
            "Select columns to display",
            options=filtered_df.columns.tolist(),
            default=filtered_df.columns.tolist()
        )
    
    with col2:
        rows_to_show = st.slider("Number of rows to display", 5, 100, 20)
    
    # Data table with filters
    st.dataframe(
        filtered_df[show_columns].head(rows_to_show),
        column_config={
            "Portal_Link": st.column_config.LinkColumn("Portal Link"),
            "Unit_Price_Latest": st.column_config.NumberColumn("Unit Price", format="$%.2f"),
            "Benchmark_Price": st.column_config.NumberColumn("Benchmark Price", format="$%.2f"),
            "Price_Deviation (%)": st.column_config.NumberColumn("Price Deviation %", format="%.2f%%"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="filtered_pharma_data.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("### 💡 Summary Insights")
st.success("""
Based on the current data and filters:
- *Pricing Strategy*: Significant price variations exist across vendors for the same materials, suggesting opportunities for cost optimization.
- *GMP Compliance*: Not all vendors maintain GMP compliance, which is critical for pharmaceutical applications.
- *Market Dynamics*: Solvents show the widest price range, indicating a more competitive or segmented market.
- *Benchmark Comparison*: Several materials show substantial deviations from benchmark prices, warranting further investigation.
- *Currency Impact*: Prices vary across currencies, which should be considered in global procurement strategies.
""")

st.caption("Dashboard last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))