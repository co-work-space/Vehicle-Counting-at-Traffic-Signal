import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Clean, professional page config
st.set_page_config(page_title="Traffic Command Center", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# VIBRANT PRIMARY COLOR PALETTE (Cars: Red, Trucks: Blue, Buses: Yellow, Motorcycles: Green)
THEME_COLORS = ['#FF4B4B', '#1E88E5', '#FFC107', '#00C853']
# DISTINCT COLOR FOR PEAK HOURS (Vibrant Teal)
PEAK_HOUR_COLOR = ['#00ACC1'] 

@st.cache_data
def generate_mock_data():
    times = [datetime(2023, 1, 1, 8, 0) + timedelta(minutes=15*i) for i in range(41)]
    
    data = []
    for t in times:
        multiplier = 2.5 if (8 <= t.hour <= 9) or (16 <= t.hour <= 17) else 1.0
        
        data.append({
            'Time': t.strftime('%H:%M'),
            'Cars': max(0, int(np.random.normal(50, 10) * multiplier)),
            'Trucks': max(0, int(np.random.normal(15, 5) * multiplier)),
            'Buses': max(0, int(np.random.normal(5, 2) * multiplier)),
            'Motorcycles': max(0, int(np.random.normal(20, 8) * multiplier)),
        })
    
    df = pd.DataFrame(data)
    df['Total'] = df['Cars'] + df['Trucks'] + df['Buses'] + df['Motorcycles']
    return df

df = generate_mock_data()

# Sleek Sidebar Design
with st.sidebar:
    st.title("Traffic Analytics")
    st.markdown("---")
    menu = st.radio("Navigation", ["Main Dashboard", "Search Logs", "Export Data"])
    st.markdown("---")
    st.info("System Status: ONLINE\n\nReady for YOLO Integration.")

if menu == "Main Dashboard":
    st.title("Live Traffic Command Center")
    st.markdown("Real-time monitoring and historical analytics of intersection traffic.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- ROW 1: KPIs ---
    st.markdown("### Live Metrics")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    current_total = df['Total'].iloc[-1]
    prev_total = df['Total'].iloc[-2]
    
    kpi1.metric("Total Vehicles Today", f"{df['Total'].sum():,}", "+15% vs Yesterday")
    kpi2.metric("Current Traffic Density", "High (0.85)", "+0.12")
    kpi3.metric("Average Speed Estimate", "42 km/h", "-3 km/h")
    kpi4.metric("Current Volume (Last 15m)", current_total, f"{current_total - prev_total} vs last 15m")

    st.markdown("---")

    # --- ROW 2: The Big Time Series ---
    st.markdown("### Traffic Volume Over Time")
    df_melted = df.melt(id_vars=['Time'], value_vars=['Cars', 'Trucks', 'Buses', 'Motorcycles'], 
                        var_name='Vehicle Type', value_name='Count')
    
    fig_line = px.line(df_melted, x='Time', y='Count', color='Vehicle Type', 
                       color_discrete_sequence=THEME_COLORS, markers=True)
    fig_line.update_layout(xaxis_title="Time of Day", yaxis_title="Number of Vehicles", hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20))
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # --- ROW 3: Split 50/50 for Pie and Bar Charts ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Vehicle Distribution")
        totals = df[['Cars', 'Trucks', 'Buses', 'Motorcycles']].sum()
        fig_pie = px.pie(values=totals.values, names=totals.index, hole=0.4, 
                         color_discrete_sequence=THEME_COLORS)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        st.markdown("#### Peak Hour Analysis")
        df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M').dt.hour
        hourly_df = df.groupby('Hour')['Total'].sum().reset_index()
        
        # UPGRADED: Using the new Teal color!
        fig_bar = px.bar(hourly_df, x='Hour', y='Total', text='Total', 
                         color_discrete_sequence=PEAK_HOUR_COLOR)
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Hour of Day", yaxis_title="Total Vehicles", margin=dict(t=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # --- ROW 4: Centered Congestion Meter ---
    st.markdown("#### Congestion Meter")
    # Using 3 columns to center the gauge so it doesn't stretch too wide
    g_col1, g_col2, g_col3 = st.columns([1, 2, 1])
    with g_col2:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 85,
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "#00ACC1"}, # Matched the Teal color
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': "#00C853"},  
                    {'range': [50, 80], 'color': "#FFC107"},  
                    {'range': [80, 100], 'color': "#FF4B4B"}], 
            }
        ))
        fig_gauge.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

elif menu == "Search Logs":
    st.title("Search Traffic History")
    st.write("Filter past detections by time lapse and vehicle type.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        start_time = st.time_input("Start Time")
    with col2:
        end_time = st.time_input("End Time")
    with col3:
        v_type = st.selectbox("Vehicle Type", ["All", "Cars", "Trucks", "Buses", "Motorcycles"])
        
    if st.button("Search Database", use_container_width=True):
        st.success(f"Query successful! Showing results for {v_type} between {start_time} and {end_time}.")
        
        st.write("### Raw Crossing Logs")
        if v_type == "All":
            st.dataframe(df, use_container_width=True)
        else:
            st.dataframe(df[['Time', v_type, 'Total']], use_container_width=True)

elif menu == "Export Data":
    st.title("Export Traffic Data")
    st.markdown("Download the raw analytics dataset for external reporting or auditing.")
    
    st.dataframe(df.head(10), use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full CSV Report",
        data=csv,
        file_name='traffic_analytics_report.csv',
        mime='text/csv',
    )