# @module dashboard
# @description A Streamlit-based dashboard for visualizing bike sharing demand data
# @addresses Business questions:
#  1. What factors contribute to the number of bike rentals, and how do they impact rental rates?
#  2. Based on demand patterns, when is the optimal time to increase the number of bikes?
# @author farismnrr
# @version 1.0.0

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# Set page configuration
st.set_page_config(page_title="Bike Sharing Analysis", page_icon="🚲", layout="wide")

@st.cache_data
def load_data():
    """
    @function load_data
    @description Loads and preprocesses the merged dataset
    @returns {DataFrame} Processed DataFrame ready for visualization
    """
    df = pd.read_csv("dashboards/merged_dataset.csv")
    
    # Convert date column
    df['dteday'] = pd.to_datetime(df['dteday'])
    
    # Create day name column if it doesn't exist
    if 'day_name' not in df.columns:
        df['day_name'] = df['dteday'].dt.day_name()
    
    # Create year-month column for trend analysis
    df['year_month'] = df['dteday'].dt.strftime('%Y-%m')
    
    return df

@st.cache_data
def load_hourly_data():
    """
    @function load_hourly_data
    @description Loads the original hourly dataset for hour-based visualizations
    @returns {DataFrame} Processed hourly DataFrame ready for visualization
    """
    df = pd.read_csv("data/hourly_data_cleaned.csv")
    
    # Convert date column
    df['dteday'] = pd.to_datetime(df['dteday'])
    
    return df

# @section Data Loading and Preparation
# Load data
df = load_data()
hourly_df = load_hourly_data()

# @section UI Sidebar Setup
# Add sidebar for filtering
st.sidebar.title("Filter Data")

# Date range filter
min_date = df['dteday'].min().date()
max_date = df['dteday'].max().date()

start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Filter data based on date selection
filtered_df = df[(df['dteday'].dt.date >= start_date) & (df['dteday'].dt.date <= end_date)]
filtered_hourly_df = hourly_df[(hourly_df['dteday'].dt.date >= start_date) & (hourly_df['dteday'].dt.date <= end_date)]

# @section Dashboard Header
# Main dashboard title
st.title("🚲 Bike Sharing Demand Analysis")
st.markdown(f"Data from {start_date} to {end_date}")

# @section Key Metrics Display
# Show basic statistics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Bike Rentals", f"{int(filtered_df['cnt_daily'].sum()):,}")
with col2:
    st.metric("Average Daily Rentals", f"{filtered_df['cnt_daily'].mean():.2f}")
with col3:
    st.metric("Max Daily Rentals", f"{filtered_df['cnt_daily'].max():.0f}")

# @section Tab Navigation
# Create tabs for each business question
q1, q2 = st.tabs(["Factors Impacting Bike Rentals", "Optimal Times for Bike Availability"])

# @section Question 1 Analysis
# QUESTION 1: What factors contribute to the number of bike rentals?
with q1:
    st.header("What factors contribute to the number of bike rentals?")
    
    # @subsection Distribution Analysis
    st.subheader("1. Distribution of Bike Rentals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall distribution using color discrete sequence for gradient effect
        fig = px.histogram(
            filtered_df, x="cnt_daily", nbins=30,
            title="Distribution of Total Bike Rentals",
            labels={"cnt_daily": "Total Rentals", "count": "Frequency"},
            color_discrete_sequence=px.colors.sequential.Viridis,
            opacity=0.8
        )
        fig.update_layout(xaxis_title="Total Rentals", yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: The distribution of bike rentals shows a slight positive skew, with most days experiencing moderate rental rates 
        between 1,000-4,000 bikes. The long tail to the right represents days with exceptionally high demand, 
        which could be influenced by favorable weather conditions or special events.
        """)
    
    with col2:
        # @visualization Year-based distribution comparison
        fig = px.histogram(
            filtered_df, x="cnt_daily", color="yr",
            title="Distribution of Bike Rentals by Year",
            labels={"cnt_daily": "Total Rentals", "count": "Frequency", "yr": "Year"},
            color_discrete_map={0: "#FF9933", 1: "#339933"},
            barmode="overlay", opacity=0.7, nbins=30
        )
        fig.update_layout(xaxis_title="Total Rentals", yaxis_title="Frequency", 
                          legend_title="Year", legend=dict(orientation="h", y=1.1))
        fig.update_layout(legend=dict(
            title="Year",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            traceorder="normal",
            itemsizing="constant"
        ))
        # Replace legend labels with actual years
        newnames = {'0': '2011', '1': '2012'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: There's a noticeable difference in rental patterns between 2011 and 2012. 
        In 2012, the distribution shifted towards higher rental counts, showing an overall increase in bike usage. 
        This suggests growing popularity of the bike sharing service over time and potentially improved operational efficiency.
        """)

    # @subsection Temporal Factor Analysis
    st.subheader("2. Impact of Temporal Factors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # @visualization Day of week impact
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_stats = filtered_df.groupby('day_name')['cnt_daily'].mean().reindex(days_order).reset_index()
        
        fig = px.box(
            filtered_df, x="day_name", y="cnt_daily",
            title="Bike Rentals by Day of Week",
            labels={"day_name": "Day of Week", "cnt_daily": "Total Rentals"},
            category_orders={"day_name": days_order},
            color="day_name", color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(showlegend=False, xaxis_title="Day of Week", yaxis_title="Total Rentals")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: Weekdays (particularly midweek: Tuesday to Thursday) show higher and more consistent rental patterns 
        compared to weekends. This suggests that many users rely on bikes for regular commuting. Friday and Saturday show 
        wider variability, likely due to the influence of weather conditions on leisure rides.
        """)
    
    with col2:
        # @visualization Hour of day impact
        hourly_stats = filtered_hourly_df.groupby('hr')['cnt'].mean().reset_index()
        
        fig = px.line(
            hourly_stats, x="hr", y="cnt",
            title="Average Bike Rentals by Hour of Day",
            labels={"hr": "Hour of Day", "cnt": "Average Rentals"},
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#FF6666"]
        )
        fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                         xaxis_title="Hour of Day", yaxis_title="Average Rentals")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: The hourly distribution reveals two distinct peaks at 8 AM and 5-6 PM, corresponding to typical commuting hours. 
        This bimodal pattern strongly indicates that a significant portion of bike rentals serve commuting purposes. 
        The evening peak is higher than the morning peak, suggesting that bikes are also used for post-work activities.
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # @visualization Seasonal impact
        season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
        filtered_df['season_name'] = filtered_df['season'].map(season_mapping)
        
        fig = px.box(
            filtered_df, x="season_name", y="cnt_daily",
            title="Bike Rentals by Season",
            labels={"season_name": "Season", "cnt_daily": "Total Rentals"},
            category_orders={"season_name": ["Spring", "Summer", "Fall", "Winter"]},
            color="season_name", color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False, xaxis_title="Season", yaxis_title="Total Rentals")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: Fall shows the highest median rental rates, followed closely by summer. 
        Spring and winter have lower rental counts, which aligns with expected weather constraints. 
        Summer shows the widest variability, likely due to fluctuating weather conditions and vacation patterns.
        """)
    
    with col2:
        # @visualization Weather impact
        weather_mapping = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Ice"}
        filtered_df['weather_name'] = filtered_df['weathersit'].map(weather_mapping)
        
        fig = px.box(
            filtered_df, x="weather_name", y="cnt_daily",
            title="Bike Rentals by Weather Condition",
            labels={"weather_name": "Weather Condition", "cnt_daily": "Total Rentals"},
            color="weather_name", color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig.update_layout(showlegend=False, xaxis_title="Weather Condition", yaxis_title="Total Rentals")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: Weather conditions significantly impact bike rentals. Clear weather shows the highest rental rates, 
        while rentals progressively decrease with deteriorating weather conditions. Light rain/snow causes a substantial 
        drop in rentals, and heavy precipitation shows the lowest demand, confirming weather as a critical factor in bike usage.
        """)

    # @subsection Calendar Impact Analysis
    st.subheader("3. Impact of Holidays and Working Days")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # @visualization Holiday vs non-holiday comparison
        holiday_mapping = {0: "Non-Holiday", 1: "Holiday"}
        filtered_df['holiday_name'] = filtered_df['holiday'].map(holiday_mapping)
        
        fig = px.box(
            filtered_df, x="holiday_name", y="cnt_daily",
            title="Bike Rentals on Holidays vs. Non-Holidays",
            labels={"holiday_name": "Holiday Status", "cnt_daily": "Total Rentals"},
            color="holiday_name", color_discrete_sequence=["#3CB371", "#FF6347"]
        )
        fig.update_layout(showlegend=False, xaxis_title="Holiday Status", yaxis_title="Total Rentals")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: Non-holiday periods consistently show higher rental rates compared to holidays. 
        This reinforces the observation that commuting is a primary driver of bike rentals, with reduced demand during holiday periods when regular commuting decreases.
        """)
    
    with col2:
        # @visualization Working days vs weekends comparison
        workday_mapping = {0: "Weekend/Holiday", 1: "Working Day"}
        filtered_df['workday_name'] = filtered_df['workingday'].map(workday_mapping)
        
        fig = px.box(
            filtered_df, x="workday_name", y="cnt_daily",
            title="Bike Rentals on Working Days vs. Weekends/Holidays",
            labels={"workday_name": "Day Type", "cnt_daily": "Total Rentals"},
            color="workday_name", color_discrete_sequence=["#6495ED", "#FFA07A"]
        )
        fig.update_layout(showlegend=False, xaxis_title="Day Type", yaxis_title="Total Rentals")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: Working days show higher average rentals than weekends/holidays. 
        However, weekends display higher variability, suggesting that leisure rides on weekends are more influenced by other factors like weather and seasonal events.
        """)
    
    # @subsection Environmental Factor Analysis
    st.subheader("4. Relationship with Environmental Factors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # @visualization Temperature correlation
        fig = px.scatter(
            filtered_df, x="temp_daily", y="cnt_daily",
            title="Temperature vs. Bike Rentals",
            labels={"temp_daily": "Normalized Temperature", "cnt_daily": "Total Rentals"},
            color="season_name", trendline="ols",
            hover_data=["dteday", "season_name"]
        )
        fig.update_layout(xaxis_title="Normalized Temperature", yaxis_title="Total Rentals")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: Temperature shows a strong positive correlation with bike rentals. 
        As temperature increases, rental counts tend to rise, especially in summer and fall. 
        The relationship appears to be linear up to a certain point, after which extremely high temperatures 
        may slightly reduce rental activity.
        """)
    
    with col2:
        # @visualization Humidity correlation
        fig = px.scatter(
            filtered_df, x="hum_daily", y="cnt_daily",
            title="Humidity vs. Bike Rentals",
            labels={"hum_daily": "Normalized Humidity", "cnt_daily": "Total Rentals"},
            color="season_name", trendline="ols",
            hover_data=["dteday", "season_name"]
        )
        fig.update_layout(xaxis_title="Normalized Humidity", yaxis_title="Total Rentals")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: Humidity demonstrates a negative correlation with bike rentals. 
        Higher humidity levels are associated with fewer rentals across all seasons. 
        This trend is particularly evident in summer and fall, suggesting that comfort factors 
        significantly influence biking decisions.
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # @visualization Wind speed correlation
        fig = px.scatter(
            filtered_df, x="windspeed_daily", y="cnt_daily",
            title="Wind Speed vs. Bike Rentals",
            labels={"windspeed_daily": "Normalized Wind Speed", "cnt_daily": "Total Rentals"},
            color="season_name", trendline="ols",
            hover_data=["dteday", "season_name"]
        )
        fig.update_layout(xaxis_title="Normalized Wind Speed", yaxis_title="Total Rentals")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: Wind speed shows a weak positive correlation with bike rentals. 
        While strong winds might be expected to discourage cycling, this dataset suggests the relationship is not straightforward. 
        The effect of wind speed appears to be less significant than other environmental factors like temperature and humidity.
        """)
    
    with col2:
        # @visualization Overall feature correlation
        numeric_cols = ['temp_daily', 'atemp_daily', 'hum_daily', 'windspeed_daily', 'cnt_daily']
        corr_df = filtered_df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_df, text_auto=True,
            title="Correlation Between Environmental Factors and Bike Rentals",
            labels=dict(x="Features", y="Features", color="Correlation"),
            color_continuous_scale="RdBu_r"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: The correlation matrix confirms that temperature (both 'temp' and 'atemp') has the 
        strongest positive relationship with bike rentals. Humidity shows a moderate negative correlation, 
        while wind speed has a weak correlation. Temperature and apparent temperature are highly correlated, 
        suggesting that perceived temperature is as important as actual temperature in influencing biking decisions.
        """)

# @section Question 2 Analysis
# QUESTION 2: When is the optimal time to increase the number of bikes?
with q2:
    st.header("When is the optimal time to increase the number of bikes?")
    
    # @subsection Hourly Demand Analysis
    st.subheader("1. Hourly Demand Patterns")
    
    # @visualization Hourly demand by user type
    hourly_data = filtered_hourly_df.groupby('hr')[['cnt', 'casual', 'registered']].mean().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hourly_data['hr'], y=hourly_data['cnt'],
        mode='lines+markers', name='Total Users',
        line=dict(color='royalblue', width=3),
        marker=dict(size=8),
    ))
    fig.add_trace(go.Scatter(
        x=hourly_data['hr'], y=hourly_data['registered'],
        mode='lines+markers', name='Registered Users',
        line=dict(color='firebrick', width=2, dash='dot'),
        marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=hourly_data['hr'], y=hourly_data['casual'],
        mode='lines+markers', name='Casual Users',
        line=dict(color='green', width=2, dash='dot'),
        marker=dict(size=6),
    ))
    
    # @visualization Peak time highlighting
    fig.add_vrect(
        x0=7, x1=9,
        fillcolor="yellow", opacity=0.2,
        layer="below", line_width=0,
        annotation_text="Morning Peak",
        annotation_position="top left"
    )
    fig.add_vrect(
        x0=16, x1=19,
        fillcolor="orange", opacity=0.2,
        layer="below", line_width=0,
        annotation_text="Evening Peak",
        annotation_position="top left"
    )
    
    fig.update_layout(
        title="Average Bike Rentals by Hour of Day",
        xaxis=dict(title="Hour of Day", tickmode='linear', tick0=0, dtick=1),
        yaxis=dict(title="Average Number of Rentals"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add insight from notebook
    st.markdown("""
    **Insight**: The hourly demand pattern reveals two critical peak periods: 7-9 AM and 4-7 PM, coinciding with typical commute times.
    Registered users drive these peaks, suggesting they are regular commuters. The morning peak is slightly lower (peaking at 8 AM) 
    than the evening peak (peaking at 5-6 PM), which could reflect more diverse post-work activities. Casual users show a different pattern, 
    with a single peak around midday, suggesting leisure or tourism usage. The optimal times to increase bike availability are 
    immediately before these peak periods to ensure sufficient supply during high demand.
    """)
    
    # @subsection Daily Demand Analysis
    st.subheader("2. Daily Demand Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # @visualization Day of week demand patterns
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        daily_avg = filtered_df.groupby('day_name')[['cnt_daily', 'casual_daily', 'registered_daily']].mean()
        daily_avg = daily_avg.reindex(days_order).reset_index()
        
        fig = px.bar(
            daily_avg, x="day_name", y=["registered_daily", "casual_daily"],
            title="Average Bike Rentals by Day of Week",
            labels={"day_name": "Day of Week", "value": "Average Rentals", "variable": "User Type"},
            barmode="stack",
            color_discrete_map={"registered_daily": "#1F77B4", "casual_daily": "#FF7F0E"}
        )
        fig.update_layout(
            xaxis=dict(categoryorder='array', categoryarray=days_order),
            xaxis_title="Day of Week",
            yaxis_title="Average Daily Rentals",
            legend_title="User Type",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Rename legend items
        newnames = {'registered_daily': 'Registered Users', 'casual_daily': 'Casual Users'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: The daily patterns show that weekdays (particularly Tuesday through Friday) have the highest total rental demand, 
        primarily driven by registered users who likely use bikes for commuting. Weekend days show a different pattern with increased 
        casual ridership and decreased registered users. Notably, Saturday has the highest casual user numbers, suggesting leisure 
        and recreational use. For optimal bike distribution, weekdays need more bikes in commuter routes, while weekends require 
        more bikes near recreational areas and tourist attractions.
        """)
    
    with col2:
        # @visualization Working day vs weekend comparison
        workday_avg = filtered_df.groupby('workday_name')[['cnt_daily', 'casual_daily', 'registered_daily']].mean().reset_index()
        
        fig = px.bar(
            workday_avg, x="workday_name", y=["registered_daily", "casual_daily"],
            title="Average Bike Rentals by Working Day Status",
            labels={"workday_name": "Day Type", "value": "Average Rentals", "variable": "User Type"},
            barmode="stack",
            color_discrete_map={"registered_daily": "#1F77B4", "casual_daily": "#FF7F0E"}
        )
        fig.update_layout(
            xaxis_title="Day Type",
            yaxis_title="Average Daily Rentals",
            legend_title="User Type",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Rename legend items
        newnames = {'registered_daily': 'Registered Users', 'casual_daily': 'Casual Users'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: Working days show higher overall demand than non-working days. However, the user composition differs significantly. 
        Working days are dominated by registered users (likely commuters), while non-working days see a much higher proportion of casual users. 
        This suggests different bike allocation strategies are needed: focusing on commuter routes on working days and tourist/recreational 
        areas on non-working days.
        """)
    
    # @subsection Seasonal Demand Analysis
    st.subheader("3. Monthly and Seasonal Demand Patterns")
    
    # @visualization Monthly trend analysis
    monthly_data = filtered_df.groupby('year_month')['cnt_daily'].sum().reset_index()
    monthly_data['date'] = pd.to_datetime(monthly_data['year_month'] + '-01')
    monthly_data = monthly_data.sort_values('date')
    
    # Add year and month columns for coloring
    monthly_data['year'] = monthly_data['date'].dt.year
    monthly_data['month'] = monthly_data['date'].dt.month
    
    fig = px.line(
        monthly_data, x="date", y="cnt_daily",
        title="Monthly Bike Rental Trends",
        labels={"date": "Month", "cnt_daily": "Total Monthly Rentals", "year": "Year"},
        color="year", markers=True,
        color_discrete_map={2011: "#1F77B4", 2012: "#FF7F0E"}
    )
    
    # @visualization Season overlay on monthly trend
    seasons_2011 = [
        {"season": "Spring", "start": "2011-03-01", "end": "2011-05-31"},
        {"season": "Summer", "start": "2011-06-01", "end": "2011-08-31"},
        {"season": "Fall", "start": "2011-09-01", "end": "2011-11-30"},
        {"season": "Winter", "start": "2011-12-01", "end": "2012-02-29"}
    ]
    
    seasons_2012 = [
        {"season": "Spring", "start": "2012-03-01", "end": "2012-05-31"},
        {"season": "Summer", "start": "2012-06-01", "end": "2012-08-31"},
        {"season": "Fall", "start": "2012-09-01", "end": "2012-11-30"},
        {"season": "Winter", "start": "2012-12-01", "end": "2013-02-28"}
    ]
    
    seasons = seasons_2011 + seasons_2012
    
    for season in seasons:
        start_date = pd.to_datetime(season["start"])
        end_date = pd.to_datetime(season["end"])
        
        if (start_date >= monthly_data['date'].min()) and (start_date <= monthly_data['date'].max()):
            fig.add_vrect(
                x0=start_date, x1=end_date,
                annotation_text=season["season"],
                annotation_position="top left",
                fillcolor="green" if season["season"] == "Summer" else 
                         "orange" if season["season"] == "Fall" else
                         "blue" if season["season"] == "Winter" else "lightgreen",
                opacity=0.15,
                layer="below", line_width=0
            )
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Monthly Rentals",
        legend_title="Year",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add insight from notebook
    st.markdown("""
    **Insight**: The monthly trend reveals strong seasonality in bike rentals, with peaks during summer and early fall, 
    and troughs during winter. There's also a clear year-over-year growth pattern, with 2012 showing consistently higher 
    rental numbers than the same months in 2011. The trend suggests both organic growth of the service and seasonal factors 
    at play. For optimal fleet management, bike availability should be increased during summer and fall months, with particular 
    attention to the high-demand months of June through October. Fleet size can be reduced during winter months for maintenance.
    """)
    
    # @visualization Seasonal demand analysis
    season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    filtered_df['season_name'] = filtered_df['season'].map(season_mapping)

    # @diagnostic Season distribution verification
    st.write("Season distribution in the dataset:", filtered_df['season_name'].value_counts())

    # @visualization Seasonal demand by user type
    season_avg = filtered_df.groupby('season_name')[['cnt_daily', 'casual_daily', 'registered_daily']].mean().reset_index()

    season_order = ["Spring", "Summer", "Fall", "Winter"]
    fig = px.bar(
        season_avg, x="season_name", y=["registered_daily", "casual_daily"],
        title="Average Daily Bike Rentals by Season",
        labels={"season_name": "Season", "value": "Average Rentals", "variable": "User Type"},
        barmode="stack",
        category_orders={"season_name": season_order},
        color_discrete_map={"registered_daily": "#1F77B4", "casual_daily": "#FF7F0E"}
    )
    fig.update_layout(
        xaxis_title="Season",
        yaxis_title="Average Daily Rentals",
        legend_title="User Type",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Rename legend items
    newnames = {'registered_daily': 'Registered Users', 'casual_daily': 'Casual Users'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add insight from notebook
    st.markdown("""
    **Insight**: Seasonal analysis reveals that fall has the highest average daily rentals, closely followed by summer. 
    Winter shows the lowest demand. The composition of users also varies significantly by season - casual users show much higher 
    variability across seasons, with their numbers more than doubling from winter to summer. Registered users show less seasonal 
    variation, suggesting they are more committed to bike usage year-round. Fleet size should be adjusted seasonally, with more 
    bikes made available in summer and fall, and a particular focus on areas frequented by casual users during warmer seasons.
    """)
    
    # @subsection Recommendations
    st.subheader("Recommended Times to Increase Bike Availability")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Daily Peak Hours**\n\n"
                "- Morning: 7-9 AM\n"
                "- Evening: 4-7 PM\n\n"
                "Increase bike availability during these commuting hours.")
    
    with col2:
        st.info("**Weekly Patterns**\n\n"
                "- Weekdays: Higher demand on working days\n"
                "- Peak days: Tuesday-Thursday\n\n"
                "Ensure maximum availability on weekdays.")
    
    with col3:
        st.info("**Seasonal Patterns**\n\n"
                "- Summer and Fall: Highest demand\n"
                "- Spring: Moderate demand\n"
                "- Winter: Lowest demand\n\n"
                "Adjust fleet size seasonally.")
    
    # @subsection Advanced Daily Analysis
    st.subheader("4. Advanced Daily Pattern Analysis")
    
    # Create tabs for different analysis views
    daily_tabs = st.tabs(["Workday vs. Non-workday", "Hourly Heatmap"])
    
    with daily_tabs[0]:
        # Working day vs Non-working day detailed comparison (like in notebook)
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate average rentals by hour for working days
            workday_hourly = filtered_hourly_df[filtered_hourly_df['workingday'] == 1].groupby('hr')['cnt'].mean().reset_index()
            workday_hourly['Day Type'] = 'Working Day'
            
            # Calculate average rentals by hour for non-working days
            non_workday_hourly = filtered_hourly_df[filtered_hourly_df['workingday'] == 0].groupby('hr')['cnt'].mean().reset_index()
            non_workday_hourly['Day Type'] = 'Non-Working Day'
            
            # Combine the data
            combined_hourly = pd.concat([workday_hourly, non_workday_hourly])
            
            # Create the line chart
            fig = px.line(
                combined_hourly, 
                x='hr', 
                y='cnt',
                color='Day Type',
                title="Hourly Rental Patterns: Working Days vs. Non-Working Days",
                labels={'hr': 'Hour of Day', 'cnt': 'Average Rentals', 'Day Type': 'Day Type'},
                color_discrete_map={
                    'Working Day': '#FF9933',
                    'Non-Working Day': '#339933'
                },
                markers=True
            )
            fig.update_layout(
                xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Add insight from notebook
            st.markdown("""
            **Insight**: The hourly patterns differ dramatically between working and non-working days:
            
            - **Working days** show a distinct bimodal pattern with peaks at 8 AM and 5-6 PM, strongly suggesting commuting behavior.
            - **Non-working days** display a single, broader peak around midday (10 AM - 4 PM), indicating leisure activity.
            
            This clear distinction requires different bike distribution strategies. On working days, bikes should be concentrated 
            at commuter hubs before peak times. On non-working days, a more even distribution focused on recreational areas is optimal.
            """)
        
        with col2:
            # Calculate overall averages
            avg_workday = filtered_df[filtered_df['workingday'] == 1]['cnt_daily'].mean()
            avg_non_workday = filtered_df[filtered_df['workingday'] == 0]['cnt_daily'].mean()
            
            # Create a comparison bar chart
            workday_comparison = pd.DataFrame({
                'Day Type': ['Working Day', 'Non-Working Day'],
                'Average Rentals': [avg_workday, avg_non_workday]
            })
            
            fig = px.bar(
                workday_comparison,
                x='Day Type',
                y='Average Rentals',
                color='Day Type',
                title="Average Daily Rentals by Day Type",
                color_discrete_map={
                    'Working Day': '#FF9933',
                    'Non-Working Day': '#339933'
                }
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Add insight from notebook
            st.markdown(f"""
            **Insight**: Working days average {avg_workday:.2f} rentals compared to {avg_non_workday:.2f} for non-working days. 
            This difference of {(avg_workday - avg_non_workday):.2f} rentals (or {((avg_workday - avg_non_workday)/avg_non_workday*100):.1f}%) 
            confirms the importance of commuting to the bike-sharing service. However, the substantial usage on non-working days 
            indicates the service also effectively serves recreational purposes.
            """)
    
    with daily_tabs[1]:
        # Create hour by day heatmap
        # Prepare data
        hour_day_data = filtered_hourly_df.copy()
        hour_day_data['day_name'] = pd.Categorical(
            hour_day_data['day_name'], 
            categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            ordered=True
        )
        
        # Create pivot table
        hour_day_pivot = pd.pivot_table(
            hour_day_data,
            values='cnt',
            index='day_name',
            columns='hr',
            aggfunc='mean'
        )
        
        # Create heatmap
        fig = px.imshow(
            hour_day_pivot,
            labels=dict(x="Hour of Day", y="Day of Week", color="Average Rentals"),
            x=[str(h) for h in range(24)],  # Hour labels
            y=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            color_continuous_scale="Viridis",
            title="Average Bike Rentals by Hour and Day"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: The heatmap reveals distinct temporal patterns throughout the week:
        
        - **Weekdays (Mon-Fri)** show concentrated high demand during morning (8 AM) and evening (5-6 PM) commute hours
        - **Weekends (Sat-Sun)** display a different pattern with a single, extended period of moderate demand from late morning to evening
        - **Late night hours (12 AM - 5 AM)** consistently show minimal demand across all days
        - **Fridays** have a unique pattern with an earlier afternoon increase and extended evening usage compared to other weekdays
        
        This detailed view enables precise scheduling of bike deployment and maintenance across both time of day and day of week.
        """)
    
    # @subsection User Type Analysis 
    st.subheader("5. User Type Analysis")
    
    # Calculate ratio of casual vs registered users by season
    user_type_by_season = filtered_df.groupby('season_name')[['casual_daily', 'registered_daily']].sum().reset_index()
    user_type_by_season['total'] = user_type_by_season['casual_daily'] + user_type_by_season['registered_daily']
    user_type_by_season['casual_ratio'] = user_type_by_season['casual_daily'] / user_type_by_season['total'] * 100
    user_type_by_season['registered_ratio'] = user_type_by_season['registered_daily'] / user_type_by_season['total'] * 100
    
    # Sort by season
    season_order = ["Spring", "Summer", "Fall", "Winter"]
    user_type_by_season['season_name'] = pd.Categorical(
        user_type_by_season['season_name'], 
        categories=season_order,
        ordered=True
    )
    user_type_by_season = user_type_by_season.sort_values('season_name')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create stacked bar chart showing proportions
        fig = px.bar(
            user_type_by_season,
            x='season_name',
            y=['registered_ratio', 'casual_ratio'],
            title="User Type Distribution by Season (%)",
            labels={'value': 'Percentage', 'season_name': 'Season', 'variable': 'User Type'},
            color_discrete_map={
                'registered_ratio': '#1F77B4',
                'casual_ratio': '#FF7F0E'
            },
            barmode='stack'
        )
        fig.update_layout(
            legend_title="User Type",
            xaxis_title="Season",
            yaxis_title="Percentage of Users",
            yaxis=dict(ticksuffix="%")
        )
        
        # Rename legend items
        newnames = {'registered_ratio': 'Registered Users', 'casual_ratio': 'Casual Users'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: The proportion of user types varies significantly by season. Registered users dominate across all seasons but 
        their share is highest in winter (nearly 85%) and lowest in summer (about 70%). Casual users show the opposite pattern, 
        with their highest proportion in summer. This suggests that seasonal users (tourists, occasional riders) contribute heavily 
        during warmer months, while committed users maintain their ridership year-round. Marketing campaigns to convert casual users 
        to registered users should be targeted during summer when there's the largest pool of potential conversions.
        """)
    
    with col2:
        # Create absolute numbers chart
        fig = px.bar(
            user_type_by_season,
            x='season_name',
            y=['registered_daily', 'casual_daily'],
            title="Total Rentals by User Type and Season",
            labels={'value': 'Total Rentals', 'season_name': 'Season', 'variable': 'User Type'},
            color_discrete_map={
                'registered_daily': '#1F77B4',
                'casual_daily': '#FF7F0E'
            },
            barmode='group'
        )
        fig.update_layout(
            legend_title="User Type",
            xaxis_title="Season",
            yaxis_title="Total Rentals"
        )
        
        # Rename legend items
        newnames = {'registered_daily': 'Registered Users', 'casual_daily': 'Casual Users'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight from notebook
        st.markdown("""
        **Insight**: In absolute terms, both user types follow similar seasonal patterns, with peaks in fall and summer and 
        troughs in winter. However, the amplitude of change is much more dramatic for casual users, whose numbers can quadruple from 
        winter to summer. Registered users show more stability across seasons, particularly from spring through fall. 
        This emphasizes the need for dynamic bike allocation that accounts for both the changing total demand and 
        the shifting user type composition across seasons.
        """)

    # Add insight box
    st.info("""
    **User Type Insights:**
    
    - **Registered Users:** Form the majority across all seasons, but the proportion varies
    - **Casual Users:** Represent a higher proportion in summer and fall
    - **Seasonal Impact:** Winter shows the highest proportion of registered users, likely because casual users are more affected by adverse weather
    
    These patterns suggest:
    1. Target casual users for conversion to registered users in summer/fall
    2. Focus on registered user retention during winter
    3. Adjust bike availability for different user types based on season
    """)

# @section Footer
st.markdown("---")
st.markdown("Bike Sharing Analysis Dashboard | Created with farismnrr")