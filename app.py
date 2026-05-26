import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.block-container {
    padding-top: 2rem;
}

div[data-testid="metric-container"] {
    background-color: #1E1E1E;
    border: 1px solid #2A2A2A;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
}

div[data-testid="metric-container"]:hover {
    transform: scale(1.02);
    transition: 0.3s;
}

h1, h2, h3, h4 {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TITLE SECTION
# ─────────────────────────────────────────────────────────────
st.title("📊 Sales & Revenue Dashboard")
st.markdown("### Interactive Business Analytics Platform")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    width=120
)

st.sidebar.title("Dashboard Controls")

# ─────────────────────────────────────────────────────────────
# FILE UPLOADER
# ─────────────────────────────────────────────────────────────
uploaded_file = st.sidebar.file_uploader(
    "📂 Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

# ─────────────────────────────────────────────────────────────
# SAMPLE DATASETS
# ─────────────────────────────────────────────────────────────
DATASETS = {
    "E-Commerce Sales": "ecommerce_sales.csv",
    "Restaurant Sales": "restaurant_sales.csv",
    "SaaS Revenue": "saas_revenue.csv",
    "Retail Store": "retail_store.csv"
}

selected_dataset = st.sidebar.selectbox(
    "📁 Select Sample Dataset",
    list(DATASETS.keys())
)

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
with st.spinner("Loading dataset..."):

    if uploaded_file is not None:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        else:
            df = pd.read_excel(uploaded_file)

        st.sidebar.success("Dataset Uploaded Successfully ✅")

    else:
        df = pd.read_csv(DATASETS[selected_dataset])

# ─────────────────────────────────────────────────────────────
# AUTO DETECT DATE COLUMN
# ─────────────────────────────────────────────────────────────
date_cols = [col for col in df.columns if 'date' in col.lower()]

if date_cols:

    date_col = date_cols[0]

    df[date_col] = pd.to_datetime(df[date_col])

    df['month'] = df[date_col].dt.strftime('%b %Y')
    df['month_num'] = df[date_col].dt.to_period('M').astype(str)

# ─────────────────────────────────────────────────────────────
# AUTO DETECT REVENUE COLUMN
# ─────────────────────────────────────────────────────────────
possible_revenue_cols = [
    'revenue',
    'sales',
    'total_sales',
    'total_revenue',
    'mrr',
    'daily_sales'
]

rev_col = None

for col in possible_revenue_cols:
    if col in df.columns:
        rev_col = col
        break

# Fallback
if rev_col is None:
    numeric_cols = df.select_dtypes(include='number').columns
    rev_col = numeric_cols[-1]

# ─────────────────────────────────────────────────────────────
# FIXED CATEGORICAL COLUMN DETECTION
# ─────────────────────────────────────────────────────────────
cat_cols = [
    col for col in df.columns
    if df[col].dtype == 'object'
    and 'name' not in col.lower()
]

# ─────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

for col in cat_cols[:3]:

    options = ['All'] + sorted(df[col].dropna().unique().tolist())

    selected = st.sidebar.selectbox(
        col.replace('_', ' ').title(),
        options
    )

    if selected != 'All':
        df = df[df[col] == selected]

# ─────────────────────────────────────────────────────────────
# EMPTY DATAFRAME CHECK
# ─────────────────────────────────────────────────────────────
if df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# ─────────────────────────────────────────────────────────────
# DATE FILTER
# ─────────────────────────────────────────────────────────────
if date_cols:

    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Date Range")

    min_date = df[date_col].min()
    max_date = df[date_col].max()

    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date]
    )

    df = df[
        (df[date_col] >= pd.to_datetime(start_date)) &
        (df[date_col] <= pd.to_datetime(end_date))
    ]

# ─────────────────────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────────────────────
total_revenue = df[rev_col].sum()
total_records = len(df)
avg_value = round(df[rev_col].mean(), 2)
highest_value = df[rev_col].max()

# Growth Rate
growth_rate = 0

if 'month_num' in df.columns:

    monthly_growth = (
        df.groupby('month_num')[rev_col]
        .sum()
        .reset_index()
    )

    if len(monthly_growth) >= 2:

        current_month = monthly_growth.iloc[-1][rev_col]
        previous_month = monthly_growth.iloc[-2][rev_col]

        if previous_month != 0:

            growth_rate = round(
                ((current_month - previous_month) / previous_month) * 100,
                2
            )

# ─────────────────────────────────────────────────────────────
# KPI SECTION
# ─────────────────────────────────────────────────────────────
st.subheader("📌 Key Performance Indicators")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
k2.metric("📦 Total Records", f"{total_records:,}")
k3.metric("📈 Average Value", f"${avg_value:,.2f}")
k4.metric("🔥 Highest Value", f"${highest_value:,.0f}")
k5.metric("🚀 Growth Rate", f"{growth_rate}%")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📊 Dashboard",
    "🧠 Insights",
    "📄 Raw Data"
])

# ─────────────────────────────────────────────────────────────
# DASHBOARD TAB
# ─────────────────────────────────────────────────────────────
with tab1:

  

    COLORS = [
        '#378ADD',
        '#1D9E75',
        '#BA7517',
        '#D85A30',
        '#7F77DD',
        '#639922'
    ]

    # ─────────────────────────────────────────────
    # Revenue Trend
    # ─────────────────────────────────────────────
    st.subheader("📈 Revenue Trend")

    if 'month_num' in df.columns:

        trend_data = (
            df.groupby('month_num')[rev_col]
            .sum()
            .reset_index()
        )

        fig1 = px.line(
            trend_data,
            x='month_num',
            y=rev_col,
            markers=True,
            color_discrete_sequence=['#378ADD']
        )

        fig1.update_layout(
            template='plotly_dark',
            height=400
        )

        st.plotly_chart(fig1, use_container_width=True)

    # ─────────────────────────────────────────────
    # PIE + BAR CHARTS
    # ─────────────────────────────────────────────
    col1, col2 = st.columns(2)

    # PIE CHART
    with col1:

        st.subheader("🥧 Revenue Distribution")

        pie_col = None

        for col in cat_cols:
            if col.lower() not in ['month', 'month_num']:
                pie_col = col
                break

        if pie_col:

            pie_data = (
                df.groupby(pie_col)[rev_col]
                .sum()
                .reset_index()
            )

            fig2 = px.pie(
                pie_data,
                names=pie_col,
                values=rev_col,
                hole=0.4,
                color_discrete_sequence=COLORS
            )

            fig2.update_layout(
                template='plotly_dark',
                height=400
            )

            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.warning("No categorical data available for pie chart.")

    # BAR CHART
    with col2:

        st.subheader("📊 Revenue Comparison")

        bar_col = None

        for col in cat_cols:
            if col.lower() not in ['month', 'month_num']:
                bar_col = col
                break

        if bar_col:

            bar_data = (
                df.groupby(bar_col)[rev_col]
                .sum()
                .reset_index()
                .sort_values(rev_col, ascending=False)
            )

            fig3 = px.bar(
                bar_data,
                x=bar_col,
                y=rev_col,
                color_discrete_sequence=['#1D9E75']
            )

            fig3.update_layout(
                template='plotly_dark',
                height=400
            )

            st.plotly_chart(fig3, use_container_width=True)

        else:
            st.warning("No categorical data available for bar chart.")

    # ─────────────────────────────────────────────
    # MONTHLY BREAKDOWN
    # ─────────────────────────────────────────────
    st.subheader("📅 Monthly Breakdown")

    if 'month_num' in df.columns and len(cat_cols) > 0:

        breakdown_col = None

        for col in cat_cols:
            if col.lower() not in ['month', 'month_num']:
                breakdown_col = col
                break

        if breakdown_col:

            breakdown = (
                df.groupby(['month_num', breakdown_col])[rev_col]
                .sum()
                .reset_index()
            )

            fig4 = px.bar(
                breakdown,
                x='month_num',
                y=rev_col,
                color=breakdown_col,
                color_discrete_sequence=COLORS
            )

            fig4.update_layout(
                template='plotly_dark',
                height=500
            )

            st.plotly_chart(fig4, use_container_width=True)

        else:
            st.warning("No breakdown data available.")

# ─────────────────────────────────────────────────────────────
# INSIGHTS TAB
# ─────────────────────────────────────────────────────────────
with tab2:

    st.subheader("🧠 Automated Business Insights")

    if cat_cols:

        insight_col = cat_cols[0]

        top_category = (
            df.groupby(insight_col)[rev_col]
            .sum()
            .idxmax()
        )

        top_category_value = (
            df.groupby(insight_col)[rev_col]
            .sum()
            .max()
        )

        st.success(
            f"Top performing {insight_col} is "
            f"'{top_category}' generating "
            f"${top_category_value:,.0f} revenue."
        )

    if growth_rate > 0:

        st.info(
            f"Revenue increased by {growth_rate}% "
            f"compared to previous month."
        )

    elif growth_rate < 0:

        st.error(
            f"Revenue decreased by "
            f"{abs(growth_rate)}% compared to previous month."
        )

    else:

        st.warning("No major growth trend detected.")

# ─────────────────────────────────────────────────────────────
# RAW DATA TAB
# ─────────────────────────────────────────────────────────────
with tab3:

    st.subheader("📄 Dataset")

    search = st.text_input("🔍 Search")

    if search:

        filtered_df = df[
            df.astype(str)
            .apply(lambda x: x.str.contains(search, case=False))
            .any(axis=1)
        ]

        st.dataframe(filtered_df, use_container_width=True)

    else:
        st.dataframe(df, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# DOWNLOAD BUTTON
# ─────────────────────────────────────────────────────────────
st.markdown("---")

csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Download Filtered Dataset",
    data=csv,
    file_name='filtered_dashboard_data.csv',
    mime='text/csv'
)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")

st.caption(
    "Built using Streamlit, Pandas & Plotly | "
    "Interactive Business Analytics Dashboard"
)