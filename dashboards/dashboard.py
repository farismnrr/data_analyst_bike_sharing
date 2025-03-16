"""
Bike Sharing Demand Dashboard

This Streamlit application visualizes bike sharing demand data with interactive filters,
KPIs, and various charts for data analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime


@st.cache_data
def load_data():
    """
    Load and preprocess the bike sharing dataset.
    
    Returns:
        DataFrame: Cleaned and preprocessed bike sharing data
    """
    df = pd.read_csv("merged_dataset.csv")
    
    # Convert date columns
    date_cols = ['dteday', 'year_month']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convert numeric columns
    numeric_cols = ['temp', 'atemp', 'hum', 'windspeed', 'casual', 'registered', 'cnt',
                   'daily_temp', 'daily_atemp', 'daily_hum', 'daily_windspeed',
                   'daily_casual', 'daily_registered', 'daily_cnt']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df


def apply_date_filter(df, start_date, end_date):
    """
    Filter dataframe based on date range.
    
    Args:
        df: Source dataframe
        start_date: Beginning of date range
        end_date: End of date range
        
    Returns:
        DataFrame: Filtered dataframe
    """
    filtered_df = df[(df['dteday'].dt.date >= start_date) & (df['dteday'].dt.date <= end_date)]
    return filtered_df.fillna(0)


def create_daily_trend_chart(df_filtered):
    """
    Create a line chart showing daily bike rental trends.
    
    Args:
        df_filtered: Filtered dataframe
        
    Returns:
        Plotly figure object
    """
    fig = px.line(df_filtered, x='dteday', y=['daily_casual', 'daily_registered', 'daily_cnt'],
                 labels={'value': 'Number of Users', 'dteday': 'Date'},
                 color_discrete_sequence=px.colors.qualitative.Set1,
                 hover_data={'dteday': "|%Y-%m-%d",'variable': True, 'value': ':,'})
    
    fig.update_layout(legend_title_text='User Type')
    fig.update_xaxes(gridcolor='lightgrey', gridwidth=0.5)
    fig.update_yaxes(gridcolor='lightgrey', gridwidth=0.5)
    
    return fig


def create_weekday_chart(df_filtered):
    """
    Create a bar chart showing average rentals by day of week.
    
    Args:
        df_filtered: Filtered dataframe
        
    Returns:
        Plotly figure object
    """
    df_weekday_avg = df_filtered.groupby('day_name', as_index=False)[['daily_cnt']].mean()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_weekday_avg = df_weekday_avg.set_index('day_name').loc[weekday_order].reset_index()

    day_colors = {
        'Monday': '#FF9999', 'Tuesday': '#66B2FF', 'Wednesday': '#99FF99',
        'Thursday': '#FFCC99', 'Friday': '#FF99FF', 'Saturday': '#99FFFF',
        'Sunday': '#FFE5CC'
    }

    fig = px.bar(df_weekday_avg, x='day_name', y='daily_cnt',
                labels={'daily_cnt': 'Average Daily Rentals', 'day_name': 'Day of Week'},
                color='day_name', color_discrete_map=day_colors)
    
    fig.update_layout(showlegend=False)
    fig.update_xaxes(gridcolor='lightgrey', gridwidth=0.5)
    fig.update_yaxes(gridcolor='lightgrey', gridwidth=0.5)
    
    return fig


def create_temperature_scatter(df_filtered):
    """
    Create a scatter plot of temperature vs bike rentals.
    
    Args:
        df_filtered: Filtered dataframe
        
    Returns:
        Plotly figure object
    """
    weather_colors = {
        1: '#2ECC71', 2: '#F1C40F', 3: '#E74C3C', 4: '#8E44AD'
    }
    
    fig = px.scatter(df_filtered, x='daily_temp', y='daily_cnt',
                    labels={'daily_cnt': 'Daily Rentals', 'daily_temp': 'Normalized Temperature'},
                    color='daily_weathersit', color_discrete_map=weather_colors,
                    trendline="ols", trendline_color_override="#2C3E50")

    fig.update_layout(legend_title="Weather Situation", showlegend=True)
    fig.update_xaxes(gridcolor='lightgrey', gridwidth=0.5)
    fig.update_yaxes(gridcolor='lightgrey', gridwidth=0.5)
    
    return fig


def create_humidity_histogram(df_filtered):
    """
    Create a histogram showing humidity distribution.
    
    Args:
        df_filtered: Filtered dataframe
        
    Returns:
        Plotly figure object
    """
    df_filtered['humidity_range'] = pd.qcut(
        df_filtered['daily_hum'], q=5, 
        labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
    )

    fig = px.histogram(df_filtered, x='daily_hum', nbins=20,
                      labels={'daily_hum': 'Normalized Humidity',
                            'count': 'Number of Days',
                            'humidity_range': 'Humidity Level'},
                      color='humidity_range', color_discrete_sequence=px.colors.qualitative.Set3)

    fig.update_layout(
        bargap=0.1,
        coloraxis_showscale=True,
        coloraxis_colorbar_title="Humidity Level",
        xaxis_title="Normalized Humidity",
        yaxis_title="Number of Days",
        showlegend=True,
        legend_title="Humidity Level",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(gridcolor='lightgrey', gridwidth=0.5)
    fig.update_yaxes(gridcolor='lightgrey', gridwidth=0.5)
    
    return fig


def create_weather_pie_chart(df_filtered):
    """
    Create a pie chart showing rentals by weather situation.
    
    Args:
        df_filtered: Filtered dataframe
        
    Returns:
        Plotly figure object
    """
    df_weathersit = df_filtered.groupby('daily_weathersit', as_index=False)[['daily_cnt']].sum()
    weather_mapping = {
        1: "Clear/Few clouds", 
        2: "Mist/Cloudy", 
        3: "Light Snow/Rain", 
        4: "Heavy Rain/Snow"
    }
    df_weathersit['daily_weathersit'] = df_weathersit['daily_weathersit'].map(weather_mapping)

    fig = px.pie(df_weathersit, values='daily_cnt', names='daily_weathersit', hole=0.4)
    fig.update_layout(legend_title_text='Weather Situation')
    
    return fig


def setup_dashboard():
    """
    Set up the dashboard structure and custom styling.
    """
    st.markdown("""
    <style>
    .main-title {
        color: #4682B4;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .section-title {
        color: #2E8B57;
        font-size: 2em;
        border-bottom: 2px solid #2E8B57;
        padding-bottom: 0.2em;
        margin-top: 1.5em;
    }
    </style>
    """, unsafe_allow_html=True)


def display_kpis(df_filtered):
    """
    Display KPI metrics in the dashboard.
    
    Args:
        df_filtered: Filtered dataframe
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_count = int(df_filtered['daily_cnt'].sum())
        st.metric(label="Total Bike Rentals", value=f"{total_count:,}")

    with col2:
        avg_registered = df_filtered['daily_registered'].mean()
        st.metric(label="Avg. Registered Users", value=f"{avg_registered:.2f}")

    with col3:
        avg_casual = df_filtered['daily_casual'].mean()
        st.metric(label="Avg. Casual Users", value=f"{avg_casual:.2f}")


def main():
    """
    Main function to run the Streamlit dashboard application.
    """
    # Load data
    df = load_data()
    
    # Setup dashboard styling
    setup_dashboard()
    
    # Sidebar filters
    st.sidebar.header("Filter Data")
    start_date = st.sidebar.date_input(
        "Start Date",
        value=df['dteday'].min().to_pydatetime(),
        min_value=df['dteday'].min().to_pydatetime(),
        max_value=df['dteday'].max().to_pydatetime()
    )
    end_date = st.sidebar.date_input(
        "End Date",
        value=df['dteday'].max().to_pydatetime(),
        min_value=df['dteday'].min().to_pydatetime(),
        max_value=df['dteday'].max().to_pydatetime()
    )
    
    # Validate dates
    if start_date > end_date:
        st.sidebar.error("Error: End date must fall after start date.")
        st.stop()
    
    # Filter data based on date range
    df_filtered = apply_date_filter(df, start_date, end_date)
    
    # Main dashboard title
    st.markdown("<h1 class='main-title'>Bike Sharing Demand Dashboard</h1>", unsafe_allow_html=True)
    st.write(f"Data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Display KPIs
    display_kpis(df_filtered)
    
    # Create and display visualizations
    st.markdown("<h2 class='section-title'>Daily Bike Rental Trends</h2>", unsafe_allow_html=True)
    st.plotly_chart(create_daily_trend_chart(df_filtered), use_container_width=True)
    
    st.markdown("<h2 class='section-title'>Average Daily Rentals by Day of Week</h2>", unsafe_allow_html=True)
    st.plotly_chart(create_weekday_chart(df_filtered), use_container_width=True)
    
    st.markdown("<h2 class='section-title'>Temperature vs. Bike Rentals</h2>", unsafe_allow_html=True)
    st.plotly_chart(create_temperature_scatter(df_filtered), use_container_width=True)
    
    st.markdown("<h2 class='section-title'>Humidity Distribution</h2>", unsafe_allow_html=True)
    st.plotly_chart(create_humidity_histogram(df_filtered), use_container_width=True)
    
    st.markdown("<h2 class='section-title'>Rentals by Weather Situation</h2>", unsafe_allow_html=True)
    st.plotly_chart(create_weather_pie_chart(df_filtered), use_container_width=True)
    
    # Display data table
    st.subheader("Filtered Data Table")
    st.dataframe(df_filtered[['dteday', 'day_name', 'daily_cnt', 'daily_registered', 
                             'daily_casual','daily_temp', 'daily_hum', 'daily_weathersit']])


if __name__ == "__main__":
    main()