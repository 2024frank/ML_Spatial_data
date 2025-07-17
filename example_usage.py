"""
Example Usage Script for Purple Air Sensor Data Analysis
Run this script to test your setup and see basic analysis
"""
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import config

# Import our modules
from data_collector import PurpleAirDataCollector, get_sensor_data
from spatial_temporal_analyzer import SpatialTemporalAnalyzer, quick_analysis
from visualizer import PurpleAirVisualizer

def main():
    print("🌬️ Purple Air Sensor Data Analysis")
    print("=" * 50)
    
    # Step 1: Load data from your Google Sheet
    print("📊 Loading data from Google Sheets...")
    
    try:
        # Use your spreadsheet ID from config
        spreadsheet_id = config.SPREADSHEET_ID
        print(f"Spreadsheet ID: {spreadsheet_id}")
        
        # Load last 24 hours of data
        data = get_sensor_data(spreadsheet_id, hours=24)
        
        if data.empty:
            print("❌ No data found. Please check:")
            print("   - Your credentials.json file is in the project folder")
            print("   - You've shared the spreadsheet with your service account")
            print("   - Your spreadsheet has data")
            return
        
        print(f"✅ Successfully loaded {len(data)} data points")
        print(f"📅 Data range: {data['timestamp'].min()} to {data['timestamp'].max()}")
        print()
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        print("Please check your credentials.json file and spreadsheet permissions.")
        return
    
    # Step 2: Show data structure
    print("📋 Data Structure:")
    print(f"Columns: {list(data.columns)}")
    print(f"Shape: {data.shape}")
    print()
    print("Sample data:")
    print(data.head())
    print()
    
    # Step 3: Basic statistics
    if 'pm2_5_atm' in data.columns:
        print("📈 PM2.5 Statistics (last 24 hours):")
        pm25_stats = data['pm2_5_atm'].describe()
        print(pm25_stats)
        print()
        
        # Current air quality status
        latest_pm25 = data['pm2_5_atm'].iloc[-1]
        print(f"🎯 Current PM2.5: {latest_pm25:.1f} μg/m³")
        
        if latest_pm25 <= config.AQI_THRESHOLDS['good']:
            print("✅ Air Quality: Good")
        elif latest_pm25 <= config.AQI_THRESHOLDS['moderate']:
            print("⚠️ Air Quality: Moderate")
        else:
            print("🚨 Air Quality: Unhealthy")
        print()
    
    # Step 4: Quick analysis
    print("🔍 Performing spatial temporal analysis...")
    try:
        analyzer = SpatialTemporalAnalyzer(data)
        report = analyzer.generate_summary_report()
        
        print("📊 Analysis Results:")
        if 'pm25_analysis' in report:
            trend_info = report['pm25_analysis'].get('trend', {})
            print(f"   • Trend: {trend_info.get('trend_direction', 'unknown')}")
            print(f"   • Correlation strength: {trend_info.get('trend_strength', 0):.3f}")
        
        if 'air_quality_metrics' in report:
            metrics = report['air_quality_metrics']
            if 'unhealthy_time_percentage' in metrics:
                print(f"   • Time in unhealthy conditions: {metrics['unhealthy_time_percentage']:.1f}%")
        
        if 'pollution_events' in report:
            print(f"   • Pollution events detected: {len(report['pollution_events'])}")
        
        print()
        
    except Exception as e:
        print(f"⚠️ Analysis error: {str(e)}")
        print()
    
    # Step 5: Create visualizations
    print("📊 Creating visualizations...")
    try:
        visualizer = PurpleAirVisualizer(data)
        
        # Time series plot
        if 'pm2_5_atm' in data.columns:
            print("   • Time series plot...")
            fig = visualizer.create_time_series_plot('pm2_5_atm', interactive=False)
            plt.savefig(f'{config.CHARTS_DIR}/pm25_timeseries.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # Distribution plot
            print("   • Distribution analysis...")
            dist_fig = visualizer.create_distribution_plot('pm2_5_atm')
            dist_fig.write_html(f'{config.CHARTS_DIR}/pm25_distribution.html')
            
            print(f"✅ Charts saved to {config.CHARTS_DIR}/")
        
    except Exception as e:
        print(f"⚠️ Visualization error: {str(e)}")
    
    print()
    
    # Step 6: Show available columns for further analysis
    print("🔧 Available data for analysis:")
    for col in data.columns:
        if col != 'timestamp':
            non_null_count = data[col].notna().sum()
            print(f"   • {col}: {non_null_count}/{len(data)} values")
    
    print()
    print("✨ Analysis complete!")
    print("💡 Next steps:")
    print("   1. Run: streamlit run streamlit_dashboard.py")
    print("   2. Open your browser to http://localhost:8501")
    print("   3. Enter your spreadsheet ID in the sidebar")
    print("   4. Explore the interactive dashboard!")

if __name__ == "__main__":
    main() 