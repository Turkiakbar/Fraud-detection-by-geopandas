# Create Python file in Colab
#%%writefile transactions_dashboard.py

# transactions_dashboard.py
# Importing required libraries
import streamlit as st                        # Streamlit for dashboard UI
import pandas as pd                           # Pandas for data manipulation
from pathlib import Path
import matplotlib.pyplot as plt               # Matplotlib for plotting charts
from matplotlib.ticker import StrMethodFormatter  # For formatting y-axis numbers
import plotly.express as px                   # Plotly Express for interactive charts
import numpy as np
import geopandas as gpd
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
from branca.colormap import linear



# Page settings
st.set_page_config(
    page_title="Credit Card Transactions Dashboard",
    layout="wide"
)

# Custom CSS styling for theme
st.markdown(
    """
    <style>
        body { background-color: #F9FAFB; color: #111827; }
        .sidebar .sidebar-content { background-color: #E5E7EB; color: #111827; }
    </style>
    """,
    unsafe_allow_html=True
)

# Load dataset (df_clean.csv located next to this script)
project_dir = Path(__file__).resolve().parent
data_path = project_dir / "df_clean.csv"
if not data_path.exists():
    # Fallback to current working directory if launched from elsewhere
    cwd_path = Path.cwd() / "df_clean.csv"
    if cwd_path.exists():
        data_path = cwd_path
    else:
        st.error(
            f"df_clean.csv not found. Expected at '{data_path}' or '{cwd_path}'.\n"
            "Export it from your notebook: df.to_csv('df_clean.csv', index=False)."
        )
        st.stop()

df = pd.read_csv("C:\\Users\\Razan\\OneDrive\\Desktop\\df_clean.csv")

# Ensure expected dtypes
if 'trans_datetime' in df.columns:
    df['trans_datetime'] = pd.to_datetime(df['trans_datetime'], errors='coerce')
elif 'trans_date_trans_time' in df.columns:
    df['trans_datetime'] = pd.to_datetime(df['trans_date_trans_time'], errors='coerce')
if 'age' in df.columns:
    df['age'] = pd.to_numeric(df['age'], errors='coerce')


# Sidebar info
st.sidebar.header("Dataset Info")
st.sidebar.markdown(
    """
    This dataset contains credit card transactions, 
    including information on amounts, times, 
    customers, merchants, and fraudulent transactions.
    """
)

with st.sidebar:
    st.header("Filters")

    # Gender filter
    selected_gender = st.multiselect(
        "Select Gender(s):",
        options=sorted(df['gender'].unique()),
        default=sorted(df['gender'].unique())
    )

    # Amount range filter
    amt_min, amt_max = int(df['amt'].min()), int(df['amt'].max())
    selected_amt = st.slider(
        "Transaction Amount Range:",
        min_value=amt_min,
        max_value=amt_max,
        value=(amt_min, amt_max)
    )

    # Age range filter
    age_min, age_max = int(df['age'].min()), int(df['age'].max())
    selected_age = st.slider(
        "Customer Age Range:",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max)
    )

    # State filter (Multiselect only, no checkbox)
    selected_states = st.multiselect(
        "Select State(s):",
        options=sorted(df['state'].unique())
    )


# Apply filters on dataframe
filtered_df = df.copy()

if selected_gender:
    filtered_df = filtered_df[filtered_df['gender'].isin(selected_gender)]

filtered_df = filtered_df[
    (filtered_df['amt'] >= selected_amt[0]) & 
    (filtered_df['amt'] <= selected_amt[1])
]

filtered_df = filtered_df[
    (filtered_df['age'] >= selected_age[0]) &
    (filtered_df['age'] <= selected_age[1])
]

if selected_states:
    filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]


# Page header
st.title("Credit Card Transactions Dashboard")

st.subheader("Key Performance Indicators (KPIs)")

# KPIs
total_txn = len(filtered_df)  # Total of transactions
total_amount = filtered_df['amt'].sum()  # Total of amount 
avg_amount = round(filtered_df['amt'].mean(), 2)  # average of amount
avg_age = filtered_df['age'].mean()  #  average of age 

# Show KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Transactions", f"{total_txn:,}")
col2.metric("Total Amount", f"${total_amount:,.0f}")
col3.metric("Average Transaction Amount", f"${avg_amount:,.2f}")
col4.metric("Average Age", f"{avg_age:.1f} yrs")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "HeatMap",
    "Merchants Map",
    "Fraud Choropleth",
    "Proportional Circles",
    "Facts"  # <- هذا الاسم سيظهر كعنوان التاب
])

# Tab 1 : Merchants HeatMap
with tab1:
    st.subheader("Merchants HeatMap")

    center_m = [df['merch_lat'].mean(), df['merch_long'].mean()]
    map_hm = folium.Map(location=center_m, zoom_start=5, tiles='CartoDB positron')

    heat_points_m = df[['merch_lat', 'merch_long']].values.tolist()
    HeatMap(heat_points_m, radius=8, blur=10, min_opacity=0.3).add_to(map_hm)
    
    # Show the Map in Streamlit
    st_folium(map_hm, width=1000, height=600)

    # Weighted HeatMap Section
    st.subheader("Weighted HeatMap by Transaction Amount")

    center_lat = df['merch_lat'].mean()
    center_lon = df['merch_long'].mean()
    m_w = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles='CartoDB positron')

    df_w = df[['merch_lat','merch_long','amt']].dropna().copy()

    w = df_w['amt'].clip(upper=df_w['amt'].quantile(0.99))  
    w = (w - w.min()) / (w.max() - w.min() + 1e-9)

    heat_weighted = list(zip(df_w['merch_lat'], df_w['merch_long'], w))
    HeatMap(heat_weighted, radius=8, blur=10, min_opacity=0.3, max_val=1.0).add_to(m_w)

    st_folium(m_w, width=1000, height=600)


# Tab 2: Merchants HeatMap
with tab2:
    st.subheader("Merchants Map")
    # Build GeoDataFrame (used later in Tab 4), but avoid .explore() to drop heavy deps
    gdf_merch = gpd.GeoDataFrame(
        filtered_df,
        geometry=gpd.points_from_xy(filtered_df['merch_long'], filtered_df['merch_lat']),
        crs="EPSG:4326",
    )

    center_m = [filtered_df['merch_lat'].mean(), filtered_df['merch_long'].mean()]
    merch_map = folium.Map(location=center_m, zoom_start=5, tiles='CartoDB positron')
    cluster = MarkerCluster().add_to(merch_map)

    points = filtered_df[['merch_lat', 'merch_long', 'category', 'amt']].dropna()
    if len(points) > 3000:
        points = points.sample(3000, random_state=42)
    for _, r in points.iterrows():
        folium.Marker(
            location=[r['merch_lat'], r['merch_long']],
            popup=f"{r['category']} ${r['amt']:.2f}",
        ).add_to(cluster)

    st_folium(merch_map, width=1050, height=600)


# Tab 3 : Choropleth Section
with tab3:
    #st.subheader("Fraud Count by State (Choropleth)")

    state_counts = df['state'].value_counts().rename_axis('state').reset_index(name='count')

    m_choro = folium.Map(location=[37.8, -96], zoom_start=4, tiles='CartoDB positron')

    geojson_url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json'

    folium.Choropleth(
        geo_data=geojson_url,
        name='choropleth',
        data=state_counts,
        columns=['state', 'count'],
        key_on='feature.id',  
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Fraud Count'
    ).add_to(m_choro)

    folium.LayerControl().add_to(m_choro)

    st_folium(m_choro, width=1000, height=600)



# Tab 4: Proportional Circles
with tab4:

    st.subheader("Proportional Circles by Transaction Amount")

    m_circ = folium.Map(
        location=[gdf_merch.geometry.y.mean(), gdf_merch.geometry.x.mean()],
        zoom_start=5,
        tiles='CartoDB positron'
    )

    sample = gdf_merch[['merch_lat','merch_long','amt','category']].dropna().sample(
        min(3000, len(gdf_merch)), random_state=42
    )

    v = sample['amt'].clip(upper=sample['amt'].quantile(0.99))
    colormap = linear.OrRd_09.scale(v.min(), v.max())

    for _, r in sample.iterrows():
        val = min(r['amt'], sample['amt'].quantile(0.99))
        radius = 2 + 8 * (val - v.min()) / (v.max() - v.min() + 1e-9)

        folium.CircleMarker(
            location=[r['merch_lat'], r['merch_long']],
            radius=radius,
            color=colormap(val),
            fill=True,
            fill_color=colormap(val),
            fill_opacity=0.6,
            popup=f"{r['category']} ${r['amt']:.2f}"
        ).add_to(m_circ)

    colormap.caption = 'Transaction Amount'
    colormap.add_to(m_circ)

    st_folium(m_circ, width=1000, height=600)


# Tab 5: Facts
with tab5:
    st.subheader("Facts")
    custom_colors = [
        '#C2D5D7', '#859D9B', '#5B868A', '#3B848D',
        '#317178', '#32666C', '#24575D', '#133639', '#1E484D'
    ]

    # Gender pie chart
    if 'gender' in filtered_df.columns:
        counts = filtered_df['gender'].value_counts(dropna=False).rename_axis('gender').reset_index(name='count')
        fig = px.pie(
            counts,
            names='gender',
            values='count',
            title='Gender Distribution',
            hole=0.3,
            color_discrete_sequence=custom_colors  
        )
        st.plotly_chart(fig, use_container_width=True)

    # Fraud by state (top N)
    if 'state' in filtered_df.columns:
        top_n = st.slider('Top N states by fraud count', min_value=5, max_value=50, value=20, step=5)
        sc = filtered_df['state'].value_counts().head(top_n).rename_axis('state').reset_index(name='count')
        sc['count_norm'] = sc['count'] / sc['count'].max()  
        fig = px.bar(
            sc,
            x='state',
            y='count',
            title=f'Fraud Count by State (Top {top_n})',
            color='count_norm',
            color_continuous_scale=custom_colors
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # Age group counts
    if 'age' in filtered_df.columns:
        bins = [0, 18, 25, 35, 45, 55, 65, 75, 120]
        labels = ['0-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75+']
        ages = filtered_df['age'].dropna()
        age_groups = pd.cut(ages.astype(float), bins=bins, labels=labels, right=True, include_lowest=True)
        ac = age_groups.value_counts().reindex(labels, fill_value=0).rename_axis('age_group').reset_index(name='count')
        ac['count_norm'] = ac['count'] / ac['count'].max()
        fig = px.bar(
            ac,
            x='age_group',
            y='count',
            title='Transactions by Age Group',
            color='count_norm',
            color_continuous_scale=custom_colors
        )
        st.plotly_chart(fig, use_container_width=True)

    # Category counts
    if 'category' in filtered_df.columns:
        cc = filtered_df['category'].value_counts().rename_axis('category').reset_index(name='count')
        cc['count_norm'] = cc['count'] / cc['count'].max()
        fig = px.bar(
            cc,
            x='category',
            y='count',
            title='Fraud Count by Category',
            color='count_norm',
            color_continuous_scale=custom_colors
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # Amount by ranges
    if 'amt' in filtered_df.columns:
        amt = filtered_df['amt'].dropna()
        bins = [0, 10, 25, 50, 100, 200, 500, 1000, float('inf')]
        labels = ['0-10', '10-25', '25-50', '50-100', '100-200', '200-500', '500-1000', '1000+']
        groups = pd.cut(amt, bins=bins, labels=labels, right=False)
        gc = groups.value_counts().reindex(labels, fill_value=0).rename_axis('amount_range').reset_index(name='count')
        gc['count_norm'] = gc['count'] / gc['count'].max()
        fig = px.bar(
            gc,
            x='amount_range',
            y='count',
            title='Transactions by Amount Range',
            color='count_norm',
            color_continuous_scale=custom_colors
        )
        st.plotly_chart(fig, use_container_width=True)

    # Fraud by hour and weekday
    if 'trans_datetime' in filtered_df.columns:
        # Hour
        hours = filtered_df['trans_datetime'].dt.hour
        min_hour = int(hours.min())
        max_hour = int(hours.max())
        hour_range = list(range(min_hour, max_hour + 1))
        hc = hours.value_counts().reindex(hour_range, fill_value=0).sort_index().rename_axis('hour').reset_index(name='count')
        hc['count_norm'] = hc['count'] / hc['count'].max()
        fig = px.bar(
            hc,
            x='hour',
            y='count',
            title=f'Fraud Count by Hour of Day ({min_hour}:00 to {max_hour}:00)',
            color='count_norm',
            color_continuous_scale=custom_colors
        )
        st.plotly_chart(fig, use_container_width=True)

        # Weekday
        weekday = filtered_df['trans_datetime'].dt.day_name()
        order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        wc = weekday.value_counts().reindex(order).rename_axis('weekday').reset_index(name='count')
        wc['count_norm'] = wc['count'] / wc['count'].max()
        fig = px.bar(
            wc,
            x='weekday',
            y='count',
            title='Fraud Count by Weekday',
            color='count_norm',
            color_continuous_scale=custom_colors
        )
        st.plotly_chart(fig, use_container_width=True)


