"""
Streamlit Dashboard for Purple Air Sensor Data Analysis
Real-time monitoring and analysis dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import config
from data_collector import PurpleAirDataCollector, get_sensor_data
from spatial_temporal_analyzer import SpatialTemporalAnalyzer, quick_analysis, detect_air_quality_alerts
from visualizer import PurpleAirVisualizer, quick_visualization, create_sensor_dashboard

# Configure Streamlit page
st.set_page_config(
    page_title="Purple Air Sensor Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for darker styling
st.markdown("""
<style>
.main > div {
    padding-top: 2rem;
    background-color: #0E1117;
}
.stApp {
    background-color: #0E1117;
}
.stAlert > div {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #1E1E1E;
    border: 1px solid #333;
}
.metric-card {
    background-color: #1E1E1E;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #4A90E2;
    color: #E1E1E1;
}
.status-good { color: #28a745; }
.status-moderate { color: #ffc107; }
.status-unhealthy { color: #dc3545; }
/* Make the sidebar darker */
.css-1d391kg {
    background-color: #0E1117;
}
/* Dark theme for metrics */
[data-testid="metric-container"] {
    background-color: #1E1E1E;
    border: 1px solid #333;
    padding: 1rem;
    border-radius: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_sensor_data(spreadsheet_id: str, hours: int = 24):
    """Load sensor data with caching"""
    try:
        if not spreadsheet_id:
            return pd.DataFrame()
        
        data = get_sensor_data(spreadsheet_id, hours)
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def main():
    # Header
    st.title("🌬️ Purple Air Sensor Dashboard")
    st.markdown("*Real-time Air Quality Monitoring & Analysis*")
    
    # Minimal top controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("📡 **AJLC Building Purple Air Sensor** (Ohio)")
    
    with col2:
        # Time range selection
        hours_options = [1, 6, 12, 24, 48, 72, 168]  # Up to 1 week
        selected_hours = st.selectbox(
            "Time Range:",
            options=hours_options,
            index=3,  # Default to 24 hours
            format_func=lambda x: f"Last {x}h" if x < 24 else f"Last {x//24}d"
        )
    
    with col3:
        # Auto-refresh option
        auto_refresh = st.checkbox("Auto-refresh", value=False)
        if auto_refresh:
            st.rerun()
    
    with col4:
        # Manual refresh button
        if st.button("🔄 Refresh", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    # Use pre-configured values
    spreadsheet_id = config.SPREADSHEET_ID
    sensor_lat = config.SENSOR_LOCATION['latitude']
    sensor_lon = config.SENSOR_LOCATION['longitude']
    sensor_name = config.SENSOR_LOCATION['name']
    
    # Add a separator line
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading sensor data..."):
        data = load_sensor_data(spreadsheet_id, selected_hours)
    
    if data.empty:
        st.error("No data found. Please check your Spreadsheet ID and ensure data is available.")
        return
    
    # Check for PM2.5 column (both mapped and original names)
    pm25_col = None
    if 'pm2_5_atm' in data.columns:
        pm25_col = 'pm2_5_atm'
    elif 'PM2.5 :cf_1( µg/m³)' in data.columns:
        pm25_col = 'PM2.5 :cf_1( µg/m³)'
    elif 'PM2.5_cf_1 (μg/m³)' in data.columns:
        pm25_col = 'PM2.5_cf_1 (μg/m³)'
    
    # Data quality check
    data_quality_issues = []
    if len(data) < 10:
        data_quality_issues.append("Limited data available (less than 10 records)")
    
    if not pm25_col:
        data_quality_issues.append("PM2.5 data column not found")
    
    if data_quality_issues:
        st.warning("⚠️ Data Quality Issues: " + "; ".join(data_quality_issues))
    
    # Current status row
    st.markdown("### 📊 Current Status")
    
    if pm25_col and len(data) > 0:
        latest_data = data.sort_values('timestamp').iloc[-1]
        latest_pm25 = latest_data[pm25_col]
        latest_time = latest_data['timestamp']
        
        # Get AQI category
        if latest_pm25 <= config.AQI_THRESHOLDS['good']:
            aqi_status = "Good"
            status_class = "status-good"
        elif latest_pm25 <= config.AQI_THRESHOLDS['moderate']:
            aqi_status = "Moderate"
            status_class = "status-moderate"
        else:
            aqi_status = "Unhealthy"
            status_class = "status-unhealthy"
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Current PM2.5",
                value=f"{latest_pm25:.1f} μg/m³",
                delta=None
            )
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <strong>Air Quality</strong><br>
                <span class="{status_class}"><strong>{aqi_status}</strong></span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.metric(
                label="Data Points",
                value=len(data),
                delta=None
            )
        
        with col4:
            time_ago = datetime.now() - latest_time
            if time_ago.total_seconds() < 3600:
                time_display = f"{int(time_ago.total_seconds() / 60)} min ago"
            else:
                time_display = f"{int(time_ago.total_seconds() / 3600)} hr ago"
            
            st.metric(
                label="Last Update",
                value=time_display,
                delta=None
            )
        
        # Check for alerts
        alerts = detect_air_quality_alerts(data)
        if alerts:
            for alert in alerts:
                st.error(f"🚨 **AIR QUALITY ALERT**: {alert['message']}")
    
    # Main visualizations
    st.markdown("### 📈 Data Analysis")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "⏰ Time Analysis", "📍 Spatial", "📋 Reports"])
    
    # Initialize visualizer once for all tabs
    visualizer = PurpleAirVisualizer(data)
    
    with tab1:
        if pm25_col:
            # Time series plot
            st.subheader("PM2.5 Time Series")
            time_series_fig = visualizer.create_time_series_plot(pm25_col)
            st.plotly_chart(time_series_fig, use_container_width=True)
            
            # Key statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Statistics (24h)")
                stats_data = {
                    "Average": f"{data[pm25_col].mean():.1f} μg/m³",
                    "Maximum": f"{data[pm25_col].max():.1f} μg/m³",
                    "Minimum": f"{data[pm25_col].min():.1f} μg/m³",
                    "Standard Deviation": f"{data[pm25_col].std():.1f} μg/m³"
                }
                
                for key, value in stats_data.items():
                    st.metric(key, value)
            
            with col2:
                if 'aqi_category' in data.columns:
                    st.subheader("AQI Distribution")
                    aqi_fig = visualizer._create_aqi_pie_chart()
                    st.plotly_chart(aqi_fig, use_container_width=True)
    
    with tab2:
        st.subheader("Temporal Patterns")
        
        if pm25_col:
            # Hourly heatmap
            st.write("**Hourly Patterns**")
            hourly_fig = visualizer.create_hourly_heatmap(pm25_col)
            st.plotly_chart(hourly_fig, use_container_width=True)
            
            # Distribution analysis
            st.write("**Distribution Analysis**")
            dist_fig = visualizer.create_distribution_plot(pm25_col)
            st.plotly_chart(dist_fig, use_container_width=True)
    
    with tab3:
        st.subheader("Spatial Information")
        
        # Sensor map
        st.write("**Sensor Location**")
        try:
            sensor_map = visualizer.create_sensor_map(include_data_points=True)
            st.components.v1.html(sensor_map._repr_html_(), height=400)
        except Exception as e:
            st.error(f"Error creating map: {str(e)}")
            st.info("Map requires valid sensor coordinates. Please check your data or configure location in sidebar.")
    
    with tab4:
        st.subheader("Analysis Reports")
        
        # Generate comprehensive analysis
        if pm25_col:
            with st.spinner("Generating analysis report..."):
                analyzer = SpatialTemporalAnalyzer(data)
                report = analyzer.generate_summary_report()
            
            # Display key findings
            st.write("**Key Findings:**")
            
            # Trend analysis
            if 'pm25_analysis' in report:
                trend_info = report['pm25_analysis'].get('trend', {})
                trend_direction = trend_info.get('trend_direction', 'stable')
                trend_strength = trend_info.get('trend_strength', 0)
                
                st.info(f"📈 **Trend**: PM2.5 levels are {trend_direction} with {trend_strength:.2f} correlation strength")
            
            # Air quality metrics
            if 'air_quality_metrics' in report:
                metrics = report['air_quality_metrics']
                if 'unhealthy_time_percentage' in metrics:
                    unhealthy_pct = metrics['unhealthy_time_percentage']
                    if unhealthy_pct > 10:
                        st.warning(f"⚠️ **Health Alert**: {unhealthy_pct:.1f}% of time in unhealthy conditions")
                    else:
                        st.success(f"✅ **Good News**: Only {unhealthy_pct:.1f}% of time in unhealthy conditions")
            
            # Pollution events
            if 'pollution_events' in report and len(report['pollution_events']) > 0:
                st.warning(f"🚨 **{len(report['pollution_events'])} pollution events detected**")
                
                events_df = pd.DataFrame(report['pollution_events'])
                st.dataframe(events_df, use_container_width=True)
            
            # Recommendations
            if 'recommendations' in report:
                st.write("**Recommendations:**")
                for i, rec in enumerate(report['recommendations'], 1):
                    st.write(f"{i}. {rec}")
            
            # Download report
            if st.button("📥 Download Full Report"):
                report_json = pd.Series(report).to_json(indent=2)
                st.download_button(
                    label="Download JSON Report",
                    data=report_json,
                    file_name=f"purple_air_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Raw data section (collapsible)
    with st.expander("🔍 Raw Data", expanded=False):
        st.dataframe(data, use_container_width=True)
        
        # Download data
        csv = data.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"purple_air_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        Purple Air Sensor Dashboard | Built with Streamlit | 
        Data updated every minute from Google Sheets
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 