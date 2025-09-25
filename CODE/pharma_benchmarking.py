import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Set page configuration with enhanced theme
st.set_page_config(
    page_title="Pharmaceutical Price Benchmarking Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Changed to collapsed to hide sidebar
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .filter-section {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
        gap: 8px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    /* Hide the sidebar */
    section[data-testid="stSidebar"] {
        display: none;
    }
    .main .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Color scheme
COLOR_SCHEME = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'tertiary': '#2ca02c',
    'quaternary': '#d62728',
    'quinary': '#9467bd',
    'background': '#f8f9fa',
    'text': '#333333'
}

# Custom color sequences for charts
CUSTOM_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Load data
@st.cache_data
def load_data():
    # Read the Excel file
    data = pd.read_excel('pharma_price_benchmarking_completed_final.xlsx', sheet_name='in')
    
    # Clean and convert data
    # Convert price deviation if it's a string
    if data['Price_Deviation (%)'].dtype == 'object':
        data['Price_Deviation (%)'] = data['Price_Deviation (%)'].str.replace('%', '').astype(float)
    else:
        data['Price_Deviation (%)'] = data['Price_Deviation (%)'].astype(float)
    
    # Convert timestamp columns
    date_columns = ['Price_Source_Timestamp', 'Internal_Inventory_Date', 'Internal_Contract_Date']
    for col in date_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors='coerce')
    
    # Clean percentage columns
    percentage_cols = ['Portal_vs_Unit_Deviation (%)', 'Inventory_vs_Latest (%)', 'Contract_vs_Latest (%)']
    for col in percentage_cols:
        if col in data.columns and data[col].dtype == 'object':
            data[col] = data[col].str.replace('%', '').astype(float)
    
    return data

df = load_data()

# Main dashboard with enhanced header
st.markdown(f"""
<div style='background: linear-gradient(135deg, {COLOR_SCHEME["primary"]} 0%, {COLOR_SCHEME["quinary"]} 100%); 
            padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;'>
    <h1 style='margin: 0; font-size: 2.5rem;'>💊 Pharmaceutical Price Benchmarking Dashboard</h1>
    <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;'>
    Advanced analytics for pharmaceutical material pricing and vendor performance
    </p>
</div>
""", unsafe_allow_html=True)

# Filters section on main page
st.markdown("""
<div class='filter-section'>
    <h2 style='margin: 0; text-align: center;'>🔍 Filters</h2>
</div>
""", unsafe_allow_html=True)

# Create columns for filters
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    # Material type filter
    material_types = ['All'] + list(df['Material_Type'].unique())
    selected_material_type = st.selectbox("🧪 Material Type", material_types)
    
    # Vendor filter
    vendors = ['All'] + list(df['Vendor_Name'].unique())
    selected_vendor = st.selectbox("🏭 Vendor", vendors)

with filter_col2:
    # GMP compliance filter
    gmp_options = ['All', 'Yes', 'No']
    selected_gmp = st.selectbox("✅ GMP Compliance", gmp_options)
    
    # Price tier filter
    price_tiers = ['All'] + list(df['Price_Tier'].unique())
    selected_price_tier = st.selectbox("💰 Price Tier", price_tiers)

with filter_col3:
    # Currency filter
    currencies = ['All'] + list(df['Currency'].unique())
    selected_currency = st.selectbox("💵 Currency", currencies)
    
    # Internal vs External filter
    internal_external = ['All'] + list(df['Internal vs External'].dropna().unique())
    selected_internal_external = st.selectbox("🏢 Internal/External", internal_external)

with filter_col4:
    # Additional filters can be added here if needed
    st.info("💡 Use the filters above to refine your analysis")
    
    # Display filter summary
    active_filters = []
    if selected_material_type != 'All':
        active_filters.append(f"Material: {selected_material_type}")
    if selected_vendor != 'All':
        active_filters.append(f"Vendor: {selected_vendor}")
    if selected_gmp != 'All':
        active_filters.append(f"GMP: {selected_gmp}")
    if selected_price_tier != 'All':
        active_filters.append(f"Price Tier: {selected_price_tier}")
    if selected_currency != 'All':
        active_filters.append(f"Currency: {selected_currency}")
    if selected_internal_external != 'All':
        active_filters.append(f"Type: {selected_internal_external}")
    
    if active_filters:
        st.write("**Active Filters:**")
        for filter_text in active_filters:
            st.write(f"• {filter_text}")

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
if selected_internal_external != 'All':
    filtered_df = filtered_df[filtered_df['Internal vs External'] == selected_internal_external]

# Enhanced Key metrics with gradient cards
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 10px; color: white; text-align: center;'>
        <h3 style='margin: 0; font-size: 1.5rem;'>{len(filtered_df['Material_Name'].unique()):,}</h3>
        <p style='margin: 0; opacity: 0.9;'>Total Materials</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_price = filtered_df['Unit_Price_Latest'].mean()
    price_display = f"${avg_price:,.2f}" if pd.notna(avg_price) else "N/A"
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                padding: 1rem; border-radius: 10px; color: white; text-align: center;'>
        <h3 style='margin: 0; font-size: 1.5rem;'>{price_display}</h3>
        <p style='margin: 0; opacity: 0.9;'>Average Price</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_deviation = filtered_df['Price_Deviation (%)'].mean()
    deviation_display = f"{avg_deviation:.2f}%" if pd.notna(avg_deviation) else "N/A"
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                padding: 1rem; border-radius: 10px; color: white; text-align: center;'>
        <h3 style='margin: 0; font-size: 1.5rem;'>{deviation_display}</h3>
        <p style='margin: 0; opacity: 0.9;'>Avg Price Deviation</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    gmp_compliant = filtered_df[filtered_df['GMP_Compliance'] == 'Yes'].shape[0]
    total_materials = len(filtered_df)
    compliance_rate = (gmp_compliant/total_materials * 100) if total_materials > 0 else 0
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                padding: 1rem; border-radius: 10px; color: white; text-align: center;'>
        <h3 style='margin: 0; font-size: 1.5rem;'>{gmp_compliant}/{total_materials}</h3>
        <p style='margin: 0; opacity: 0.9;'>GMP Compliant ({compliance_rate:.1f}%)</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Tabs with custom styling
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Price Analysis", 
    "🏭 Vendor Analysis", 
    "🧪 Material Insights", 
    "📅 Temporal Analysis",
    "🌐 Currency & Portal Analysis",
    "🔍 Detailed Data"
])

# Custom chart template
chart_template = go.layout.Template(
    layout=go.Layout(
        plot_bgcolor='rgba(248,249,250,1)',
        paper_bgcolor='rgba(248,249,250,1)',
        font=dict(color=COLOR_SCHEME['text']),
        colorway=CUSTOM_COLORS
    )
)

with tab1:
    st.subheader("🎯 Price Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Enhanced Price distribution by material type
        fig = px.box(filtered_df, x='Material_Type', y='Unit_Price_Latest', 
                     title='📦 Price Distribution by Material Type',
                     color='Material_Type',
                     color_discrete_sequence=CUSTOM_COLORS)
        fig.update_layout(template=chart_template)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        💡 **Insight**: This chart shows the price distribution across different material types. 
        High-value materials show significant price variations, indicating market volatility.
        """)
    
    with col2:
        # Enhanced Price vs Benchmark comparison
        avg_prices = filtered_df.groupby('Material_Name').agg({
            'Unit_Price_Latest': 'mean',
            'Benchmark_Price': 'mean'
        }).reset_index().melt(id_vars='Material_Name', 
                              value_vars=['Unit_Price_Latest', 'Benchmark_Price'],
                              var_name='Price_Type', value_name='Price')
        
        fig = px.bar(avg_prices.head(20), x='Material_Name', y='Price', color='Price_Type',
                     barmode='group', 
                     title='⚖️ Average Price vs Benchmark Price (Top 20 Materials)',
                     color_discrete_sequence=[COLOR_SCHEME['primary'], COLOR_SCHEME['secondary']])
        fig.update_xaxes(tickangle=45)
        fig.update_layout(template=chart_template)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        💡 **Insight**: This comparison shows how current prices compare to benchmark prices. 
        Materials with current prices significantly above benchmarks may represent procurement opportunities.
        """)
    
    # Enhanced Price deviation analysis
    st.subheader("📊 Price Deviation Analysis")
    
    fig = px.scatter(filtered_df, x='Unit_Price_Latest', y='Price_Deviation (%)',
                     color='Material_Type', size='Unit_Price_Latest',
                     hover_data=['Material_Name', 'Vendor_Name'],
                     title='🎯 Price vs Deviation Analysis',
                     color_discrete_sequence=CUSTOM_COLORS)
    fig.update_layout(template=chart_template)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    💡 **Insight**: This scatter plot shows the relationship between price and deviation from benchmark. 
    Higher priced items don't necessarily have higher deviations, suggesting pricing strategies vary by material type.
    """)

with tab2:
    st.subheader("🏆 Vendor Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Enhanced Vendor count by material type
        vendor_counts = filtered_df.groupby(['Vendor_Name', 'Material_Type']).size().reset_index(name='Count')
        fig = px.bar(vendor_counts, x='Vendor_Name', y='Count', color='Material_Type',
                     title='📊 Vendor Offerings by Material Type',
                     color_discrete_sequence=CUSTOM_COLORS)
        fig.update_xaxes(tickangle=45)
        fig.update_layout(template=chart_template)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        💡 **Insight**: This chart shows which vendors specialize in certain material types. 
        Major vendors like Merck and Sigma Aldrich offer diverse product ranges.
        """)
    
    with col2:
        # Enhanced Average price by vendor
        vendor_prices = filtered_df.groupby('Vendor_Name')['Unit_Price_Latest'].mean().reset_index()
        vendor_prices = vendor_prices.sort_values('Unit_Price_Latest', ascending=False).head(15)
        
        fig = px.bar(vendor_prices, x='Unit_Price_Latest', y='Vendor_Name', 
                     title='💰 Average Price by Vendor (Top 15)',
                     orientation='h',
                     color='Unit_Price_Latest',
                     color_continuous_scale='Viridis')
        fig.update_layout(template=chart_template)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        💡 **Insight**: Vendors show significant variation in average pricing. 
        This could indicate differences in quality, branding, or market positioning strategies.
        """)
    
    # Enhanced Vendor GMP compliance
    st.subheader("✅ Vendor GMP Compliance Status")
    
    gmp_stats = filtered_df.groupby('Vendor_Name')['GMP_Compliance'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    ).reset_index(name='GMP_Compliance_Percentage')
    
    fig = px.bar(gmp_stats.head(15), x='Vendor_Name', y='GMP_Compliance_Percentage',
                 title='🛡️ GMP Compliance Rate by Vendor (Top 15)',
                 color='GMP_Compliance_Percentage',
                 color_continuous_scale='Greens')
    fig.update_xaxes(tickangle=45)
    fig.update_layout(template=chart_template)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    💡 **Insight**: GMP compliance varies significantly across vendors. 
    Some vendors maintain high compliance rates, which is crucial for pharmaceutical manufacturing quality standards.
    """)

with tab3:
    st.subheader("🔬 Material-Specific Insights")
    
    # Material selector with enhanced styling
    materials = ['All'] + list(df['Material_Name'].unique())
    selected_material = st.selectbox("🧪 Select Material", materials, key='material_select')
    
    if selected_material != 'All':
        material_df = filtered_df[filtered_df['Material_Name'] == selected_material]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced Price distribution for selected material
            fig = px.box(material_df, y='Unit_Price_Latest', 
                         title=f'📦 Price Distribution for {selected_material}',
                         color_discrete_sequence=[COLOR_SCHEME['primary']])
            fig.update_layout(template=chart_template)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"""
            💡 **Insight**: The price distribution for {selected_material} shows the range of prices offered by different vendors. 
            A wide range may indicate opportunities for cost savings through vendor selection.
            """)
        
        with col2:
            # Enhanced Vendor comparison for selected material
            fig = px.bar(material_df, x='Vendor_Name', y='Unit_Price_Latest',
                         title=f'🏭 Vendor Prices for {selected_material}',
                         color='Unit_Price_Latest',
                         color_continuous_scale='Blues')
            fig.update_layout(template=chart_template)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"""
            💡 **Insight**: Different vendors offer {selected_material} at varying price points. 
            This visualization helps identify the most cost-effective suppliers for this material.
            """)
        
        # Enhanced Specification and grade analysis
        st.subheader(f"📋 Specification and Grade Analysis for {selected_material}")
        
        spec_grade = material_df.groupby(['Specification', 'Material_Grade']).agg({
            'Unit_Price_Latest': 'mean',
            'Vendor_Name': 'count'
        }).reset_index().rename(columns={'Vendor_Name': 'Vendor_Count'})
        
        if len(spec_grade) > 0:
            fig = px.scatter(spec_grade, x='Specification', y='Material_Grade',
                             size='Unit_Price_Latest', color='Vendor_Count',
                             title='🎯 Specification vs Grade Analysis',
                             hover_data=['Unit_Price_Latest', 'Vendor_Count'],
                             color_continuous_scale='Viridis')
            fig.update_layout(template=chart_template)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"""
            💡 **Insight**: This chart shows how different specifications and grades of {selected_material} correlate with pricing and vendor availability. 
            Certain combinations may command premium prices or have limited supplier options.
            """)
        else:
            st.warning("⚠️ Insufficient data for specification and grade analysis.")
    else:
        st.info("ℹ️ Please select a specific material to see detailed analysis.")

with tab4:
    st.subheader("📅 Temporal Analysis")
    
    # Enhanced Time-based analysis
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
                      name="Average Price", 
                      mode='lines+markers',
                      line=dict(color=COLOR_SCHEME['primary'], width=3)),
            secondary_y=False,
        )
        
        # Add count trace
        fig.add_trace(
            go.Bar(x=time_series['Price_Source_Timestamp'], 
                  y=time_series['Material_Count'], 
                  name="Material Count", 
                  opacity=0.7,
                  marker_color=COLOR_SCHEME['secondary']),
            secondary_y=True,
        )
        
        fig.update_layout(
            title_text="📈 Price Trends Over Time with Material Count",
            template=chart_template
        )
        
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Average Price", secondary_y=False)
        fig.update_yaxes(title_text="Material Count", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        💡 **Insight**: This chart shows how prices have evolved over time, along with the number of materials 
        recorded at each time point. Seasonal trends or price spikes may be visible in the data.
        """)
    else:
        st.warning("⚠️ Insufficient timestamp data for temporal analysis.")

with tab5:
    st.subheader("🌐 Currency & Portal Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Enhanced Price distribution by currency
        fig = px.box(filtered_df, x='Currency', y='Unit_Price_Latest', 
                     title='💵 Price Distribution by Currency',
                     color='Currency',
                     color_discrete_sequence=CUSTOM_COLORS)
        fig.update_layout(template=chart_template)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        💡 **Insight**: This chart shows how prices vary across different currencies. 
        Note that direct comparison should account for exchange rates.
        """)
    
    with col2:
        # Enhanced Portal validation status
        portal_status = filtered_df['Portal_Validation_Status'].value_counts().reset_index()
        portal_status.columns = ['Status', 'Count']
        
        fig = px.pie(portal_status, values='Count', names='Status',
                     title='✅ Portal Validation Status',
                     color_discrete_sequence=CUSTOM_COLORS)
        fig.update_layout(template=chart_template)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        💡 **Insight**: This pie chart shows the proportion of valid vs invalid portal validations. 
        A high percentage of invalid statuses might indicate data quality issues.
        """)
    
    # Enhanced Supplier portal analysis
    st.subheader("🖥️ Supplier Portal Analysis")
    
    portal_counts = filtered_df['Supplier_Portal_Name'].value_counts().reset_index()
    portal_counts.columns = ['Portal', 'Count']
    
    fig = px.bar(portal_counts, x='Portal', y='Count',
                 title='📊 Material Count by Supplier Portal',
                 color='Count',
                 color_continuous_scale='Purples')
    fig.update_layout(template=chart_template)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    💡 **Insight**: This chart shows which supplier portals are most commonly used for sourcing materials. 
    SAP Ariba and Pharmacompass appear to be dominant platforms in this dataset.
    """)

with tab6:
    st.subheader("🔍 Detailed Data View")
    
    # Additional filters for the data table
    col1, col2 = st.columns(2)
    with col1:
        show_columns = st.multiselect(
            "📋 Select columns to display",
            options=filtered_df.columns.tolist(),
            default=['Material_Name', 'Material_Type', 'Vendor_Name', 'Unit_Price_Latest', 
                    'Benchmark_Price', 'Price_Deviation (%)', 'Currency', 'GMP_Compliance']
        )
    
    with col2:
        rows_to_show = st.slider("📊 Number of rows to display", 5, 100, 20)
    
    # Enhanced Data table with better styling
    st.dataframe(
        filtered_df[show_columns].head(rows_to_show),
        column_config={
            "Portal_Link": st.column_config.LinkColumn("🔗 Portal Link"),
            "Unit_Price_Latest": st.column_config.NumberColumn("💰 Unit Price", format="$%.2f"),
            "Benchmark_Price": st.column_config.NumberColumn("⚖️ Benchmark Price", format="$%.2f"),
            "Price_Deviation (%)": st.column_config.NumberColumn("📊 Price Deviation %", format="%.2f%%"),
            "Portal_Price": st.column_config.NumberColumn("🖥️ Portal Price", format="$%.2f"),
            "Internal_Inventory_Price": st.column_config.NumberColumn("📦 Inventory Price", format="$%.2f"),
            "Internal_Contract_Price": st.column_config.NumberColumn("📝 Contract Price", format="$%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Enhanced Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv,
        file_name="filtered_pharma_benchmarking_data.csv",
        mime="text/csv",
        use_container_width=True
    )

# Enhanced Additional Analysis Section
st.markdown("---")
st.subheader("📋 Additional Benchmarking Analysis")

col1, col2 = st.columns(2)

with col1:
    # Enhanced Internal vs External pricing comparison
    if 'Internal vs External' in filtered_df.columns:
        internal_comparison = filtered_df.groupby('Internal vs External').agg({
            'Unit_Price_Latest': 'mean',
            'Benchmark_Price': 'mean'
        }).reset_index()
        
        if len(internal_comparison) > 1:
            fig = px.bar(internal_comparison, x='Internal vs External', 
                        y=['Unit_Price_Latest', 'Benchmark_Price'],
                        title='🏢 Internal vs External Price Comparison',
                        barmode='group',
                        color_discrete_sequence=[COLOR_SCHEME['primary'], COLOR_SCHEME['secondary']])
            fig.update_layout(template=chart_template)
            st.plotly_chart(fig, use_container_width=True)

with col2:
    # Enhanced Form analysis
    if 'Form' in filtered_df.columns:
        form_prices = filtered_df.groupby('Form')['Unit_Price_Latest'].mean().reset_index()
        fig = px.pie(form_prices, values='Unit_Price_Latest', names='Form',
                    title='🧪 Price Distribution by Material Form',
                    color_discrete_sequence=CUSTOM_COLORS)
        fig.update_layout(template=chart_template)
        st.plotly_chart(fig, use_container_width=True)

# Enhanced Footer with gradient
st.markdown("---")
st.markdown(f"""
<div style='background: linear-gradient(135deg, {COLOR_SCHEME["primary"]} 0%, {COLOR_SCHEME["quinary"]} 100%); 
            padding: 1.5rem; border-radius: 10px; color: white;'>
    <h3 style='margin: 0; text-align: center;'>💡 Summary Insights</h3>
</div>
""", unsafe_allow_html=True)

st.success("""
**Based on the current data and filters:**

🎯 **Pricing Strategy**: Significant price variations exist across vendors for the same materials, suggesting opportunities for cost optimization.

✅ **GMP Compliance**: Not all vendors maintain GMP compliance, which is critical for pharmaceutical applications.

📈 **Market Dynamics**: High-value materials show the widest price range, indicating a more competitive or segmented market.

⚖️ **Benchmark Comparison**: Several materials show substantial deviations from benchmark prices, warranting further investigation.

💵 **Currency Impact**: Prices vary across currencies, which should be considered in global procurement strategies.

🖥️ **Portal Performance**: Supplier portals show varying validation statuses, indicating potential data quality considerations.
""")

# Enhanced timestamp with styling
st.markdown(f"""
<div style='background-color: {COLOR_SCHEME["background"]}; padding: 1rem; border-radius: 5px; text-align: center;'>
    <small>📅 Dashboard last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</small>
</div>
""", unsafe_allow_html=True)