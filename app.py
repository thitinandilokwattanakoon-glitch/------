import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.loaders import load_data, get_data_dictionary
from modules.data_audit import run_audit
from modules.visualization import plot_trend, plot_distribution, plot_comparison, plot_scatter

# --- PAGE CONFIG ---
# (Line 9-48 preserved)
st.set_page_config(
    page_title="Crash Report Analytics | Senior Data Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1E88E5;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5, #1565C0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #546E7A;
        margin-bottom: 2rem;
    }
    .health-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        border-left: 5px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .status-valid { color: #2E7D32; font-weight: bold; }
    .status-warning { color: #F9A825; font-weight: bold; }
    .status-critical { color: #C62828; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'file_path' not in st.session_state:
    st.session_state.file_path = "c:/Users/thitinan/Downloads/แข่ง/อบโอ่ง/1_crash_reports.csv"
if 'cleaning_log' not in st.session_state:
    st.session_state.cleaning_log = []
if 'df_cleaned' not in st.session_state:
    st.session_state.df_cleaned = None

# --- APP LAYOUT ---
st.sidebar.markdown("# 🛠️ Senior Data Lab")
st.sidebar.markdown("---")
page = st.sidebar.selectbox("Navigate", ["Overview", "Data Quality Audit", "Cleaning Lab", "Visualizations", "Data Dictionary"])

# Load Data
raw_df = load_data(st.session_state.file_path)

if raw_df.empty:
    st.warning("⚠️ No data found. Please check the file path.")
    st.stop()

# Initialize cleaned df if not present
if st.session_state.df_cleaned is None:
    st.session_state.df_cleaned = raw_df.copy()

base_df = st.session_state.df_cleaned

# --- GLOBAL FILTERS ---
st.sidebar.markdown("### 🔍 Global Filters")
with st.sidebar.expander("Filter Options", expanded=False):
    agencies = sorted(base_df['Agency Name'].dropna().unique()) if 'Agency Name' in base_df.columns else []
    selected_agencies = st.multiselect("Agency Name", agencies, default=agencies)
    
    weather_options = sorted(base_df['Weather'].dropna().unique()) if 'Weather' in base_df.columns else []
    selected_weather = st.multiselect("Weather Condition", weather_options, default=weather_options)

# Apply Filters
df_filtered = base_df.copy()
if 'Agency Name' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['Agency Name'].isin(selected_agencies)]
if 'Weather' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['Weather'].isin(selected_weather)]

df_to_use = df_filtered

# Sidebar Log
st.sidebar.markdown("---")
st.sidebar.markdown("### 📜 Transformation Steps")
if not st.session_state.cleaning_log:
    st.sidebar.info("No steps recorded.")
else:
    for i, entry in enumerate(st.session_state.cleaning_log):
        st.sidebar.caption(f"{i+1}. {entry['Details']}")

# --- PAGES ---
if page == "Overview":
    st.markdown('<p class="main-header">Dataset Overview</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">High-Performance Crash Report Analysis Dashboard</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", f"{len(df_to_use):,}")
    col2.metric("Total Columns", len(df_to_use.columns))
    col3.metric("Memory Usage", f"{df_to_use.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Calculate health score dynamically
    with st.spinner("Calculating score..."):
        audit = run_audit(df_to_use)
    col4.metric("Health Score", f"{audit['health_score']}/100") 

    st.markdown("### Preview (First 100 Records)")
    st.dataframe(df_to_use.head(100), use_container_width=True)

    st.markdown("---")
    st.markdown("### 🤖 AI-Generative Insights")
    from modules.insights import generate_automated_insights
    
    with st.spinner("Generating insights..."):
        insights_list = generate_automated_insights(df_to_use, audit)
    
    if insights_list:
        for insight in insights_list:
            st.markdown(insight)
    else:
        st.info("No specific insights could be generated for the current filter selection.")

elif page == "Data Quality Audit":
    st.markdown('<p class="main-header">Data Quality Audit</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Audit based on Completeness, Consistency, Accuracy, and Timeliness</p>', unsafe_allow_html=True)

    with st.spinner("Analyzing Data Quality..."):
        audit = run_audit(df_to_use)

    # Health Score Dial
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = audit["health_score"],
        title = {'text': "Data Health Score"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#1E88E5"},
            'steps' : [
                {'range': [0, 50], 'color': "#FFEBEE"},
                {'range': [50, 80], 'color': "#FFF9C4"},
                {'range': [80, 100], 'color': "#E8F5E9"}],
            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}
        }
    ))
    fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Audit Summary")
    for msg in audit["summary"]:
        if "Critical" in msg:
            st.error(msg)
        elif "Warning" in msg:
            st.warning(msg)
        else:
            st.info(msg)

    st.markdown("### 📊 Completeness Table")
    def style_status(val):
        color = 'red' if val == 'Critical' else ('orange' if val == 'Warning' else 'green')
        return f'color: {color}'

    st.dataframe(audit["completeness_table"].style.applymap(style_status, subset=['Status']), use_container_width=True)

elif page == "Cleaning Lab":
    st.markdown('<p class="main-header">Cleaning Lab</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Execute repeatable cleaning steps and track history</p>', unsafe_allow_html=True)
    
    from modules.cleaning import remove_duplicates, drop_missing_values, impute_values, standardize_dates

    # --- BEFORE VS AFTER METRICS ---
    st.markdown("### 📊 Metrics Comparison (Before vs After)")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Original Rows", f"{len(raw_df):,}")
    m_col2.metric("Current Rows (Filtered)", f"{len(df_to_use):,}")
    dropped = len(raw_df) - len(st.session_state.df_cleaned)
    m_col3.metric("Rows Cleaned/Dropped", f"{dropped:,}", delta=-dropped if dropped > 0 else 0)

    st.markdown("---")
    
    # --- INTERACTIVE CLEANING ---
    st.markdown("### 🛠️ Data Imputation")
    target_col = st.selectbox("Select Column to Impute", base_df.columns)
    null_count = base_df[target_col].isna().sum()
    st.write(f"Missing values in '{target_col}': **{null_count}**")
    
    strategy = st.radio("Imputation Strategy", ["Mean", "Median", "Mode", "Drop"], horizontal=True)
    
    if st.button("Apply Imputation"):
        updated_df, details, affected = impute_values(base_df.copy(), target_col, strategy)
        if affected > 0:
            st.session_state.df_cleaned = updated_df
            st.session_state.cleaning_log.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Operation": "Imputation",
                "Details": details,
                "Rows Affected": affected
            })
            st.success(details)
            st.rerun()
        else:
            st.info("No changes needed.")

    st.markdown("---")
    st.markdown("### 📅 Standardization")
    date_col_options = [c for c in base_df.columns if 'Date' in c or 'Year' in c]
    date_col = st.selectbox("Select Date Column", date_col_options)
    if st.button("Fix Date Formats"):
        updated_df, details, affected = standardize_dates(base_df.copy(), date_col)
        st.session_state.df_cleaned = updated_df
        st.session_state.cleaning_log.append({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Operation": "Standardization",
            "Details": details,
            "Rows Affected": affected
        })
        st.success(details)
        st.rerun()

    st.markdown("---")
    if st.button("🚀 Remove Duplicate Report Numbers"):
        updated_df, details, affected = remove_duplicates(base_df.copy(), subset=['Report Number'])
        st.session_state.df_cleaned = updated_df
        st.session_state.cleaning_log.append({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Operation": "Remove Duplicates",
            "Details": details,
            "Rows Affected": affected
        })
        st.success(details)
        st.rerun()

    if st.button("🗑️ Reset All Changes"):
        st.session_state.df_cleaned = raw_df.copy()
        st.session_state.cleaning_log = []
        st.success("Dataset reset to original state.")
        st.rerun()

elif page == "Visualizations":
    st.markdown('<p class="main-header">Interactive Visualizations</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data Insights and Trend Analysis</p>', unsafe_allow_html=True)
    
    if df_to_use.empty:
        st.warning("⚠️ No data available for selected filters. Please adjust your search.")
        st.stop()
        
    tab1, tab2, tab3, tab4 = st.tabs(["🕒 Trend Analysis", "📊 Distribution", "🗺️ Comparison", "📈 Correlation"])
    
    with tab1:
        st.markdown("### Time-based Trends")
        if 'Crash Date/Time' in df_to_use.columns:
            rolling = st.slider("Rolling Mean Window (Days)", 0, 30, 7)
            fig = plot_trend(df_to_use, 'Crash Date/Time', rolling_window=rolling)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No datetime column found for trend analysis.")
            
    with tab2:
        st.markdown("### Numerical Distributions")
        num_cols = df_to_use.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            col_to_plot = st.selectbox("Select Numeric Column", num_cols)
            show_out = st.toggle("Show Outliers in Plot", value=True)
            p_type = st.radio("Plot Type", ["Histogram", "Boxplot"], horizontal=True)
            fig = plot_distribution(df_to_use, col_to_plot, show_outliers=show_out, plot_type=p_type)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numerical columns available.")
            
    with tab3:
        st.markdown("### Categorical Comparisons")
        cat_cols = df_to_use.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            cat_to_comp = st.selectbox("Select Categorical Column", cat_cols)
            top_n = st.slider("Show Top N", 5, 20, 10)
            fig = plot_comparison(df_to_use, cat_to_comp, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorical columns available.")
            
    with tab4:
        st.markdown("### Numerical Relationships")
        from modules.visualization import plot_heatmap
        fig_heat = plot_heatmap(df_to_use)
        if fig_heat:
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Insufficient numerical data for correlation matrix.")
            
        st.markdown("---")
        st.markdown("### Variable Correlation (Scatter)")
        num_cols = df_to_use.select_dtypes(include=[np.number]).columns.tolist()
        if len(num_cols) >= 2:
            x_ax = st.selectbox("X Axis", num_cols, index=0)
            y_ax = st.selectbox("Y Axis", num_cols, index=1 if len(num_cols) > 1 else 0)
            fig_scatter = plot_scatter(df_to_use, x_ax, y_ax)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Need at least two numerical columns for correlation analysis.")

elif page == "Data Dictionary":
    st.markdown('<p class="main-header">Data Dictionary</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Metadata and field descriptions for traceability</p>', unsafe_allow_html=True)
    
    dict_df = get_data_dictionary(df_to_use)
    st.dataframe(dict_df, use_container_width=True)
    
    st.markdown("### 🛠️ Technical Manual (Architecture Evidence)")
    with st.expander("System Architecture Details", expanded=False):
        st.code("""
        - Framework: Streamlit 1.54.0
        - Data Engine: Pandas (Optimized types: categorical for high cardinality)
        - Visuals: Plotly Express (Sampling enabled for n > 50k)
        - DQA Module: 4D Audit (IQR Outlier detection, Consistency checks)
        - Cache: @st.cache_data for CSV ingestion (Fast initial load)
        """)
        st.info("This application follows modular Python patterns (Separation of Concerns). ทุกขั้นตอนการประมวลผลเป็นแบบระบุชนิดตัวแปร (Type Hinted) เพื่อความปลอดภัยของข้อมูล")

# Empty State Guidance (Global)
if df_to_use.empty and not raw_df.empty:
    st.sidebar.warning("⚠️ No data matches current filters.")
    if st.sidebar.button("Reset Filters Now"):
        st.rerun()

# Footer
st.markdown("---")
st.caption("National Vocational Competition | Senior Data Engineer Role | Performance-First Design")
