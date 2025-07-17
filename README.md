# 🌬️ Purple Air Sensor Analysis Project

A comprehensive spatial temporal data analysis platform for Purple Air sensor data, featuring real-time monitoring, data visualization, and interactive dashboards.

## 🎯 Features

### Core Capabilities
- **Real-time Data Collection**: Automatic fetching from Google Sheets API
- **Spatial Temporal Analysis**: Trend detection, pattern recognition, pollution event detection
- **Interactive Visualizations**: Time series plots, heatmaps, distribution analysis, maps
- **Web Dashboard**: Beautiful Streamlit interface with real-time monitoring
- **Data Quality Assessment**: Automated data validation and quality reporting
- **Alert System**: Configurable air quality alerts and notifications

### Analysis Features
- Time series trend analysis with statistical significance testing
- Hourly and daily pattern recognition
- Pollution event detection and classification
- AQI category distribution and health impact assessment
- Data gap detection and completeness reporting
- Automated recommendations based on air quality patterns

## 🚀 Quick Start

### 1. Installation
```bash
# Clone or download the project
# Navigate to project directory
cd ML_Spatial_data

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Sheets API Setup
1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Sheets API**
   - Navigate to APIs & Services > Library
   - Search for "Google Sheets API" and enable it

3. **Create Service Account**
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "Service Account"
   - Download the JSON credentials file
   - Rename it to `credentials.json` and place in project root

4. **Share Your Spreadsheet**
   - Open your Google Sheet with Purple Air data
   - Share it with the service account email (found in credentials.json)
   - Give "Viewer" permissions

### 3. Configuration
Create a `.env` file with your settings:
```env
SPREADSHEET_ID=your_google_sheets_id_here
SHEET_RANGE=Sheet1!A:Z
CREDENTIALS_FILE=credentials.json
SENSOR_LAT=37.7749
SENSOR_LON=-122.4194
SENSOR_NAME=My Purple Air Sensor
```

### 4. Run the Dashboard
```bash
streamlit run streamlit_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📊 Data Format

Your Google Sheet should contain columns like:
- `timestamp`: Date and time of measurement
- `pm2_5_atm`: PM2.5 concentration (μg/m³)
- `pm10_atm`: PM10 concentration (μg/m³) [optional]
- `temperature`: Temperature (°C) [optional]
- `humidity`: Relative humidity (%) [optional]
- `pressure`: Atmospheric pressure [optional]
- `latitude`: Sensor latitude [optional]
- `longitude`: Sensor longitude [optional]

## 🔧 Usage Examples

### Basic Data Analysis
```python
from data_collector import get_sensor_data
from spatial_temporal_analyzer import quick_analysis

# Load recent data
data = get_sensor_data("your_spreadsheet_id", hours=24)

# Perform quick analysis
report = quick_analysis(data)
print(report)
```

### Create Visualizations
```python
from visualizer import PurpleAirVisualizer

# Initialize visualizer
viz = PurpleAirVisualizer(data)

# Create time series plot
fig = viz.create_time_series_plot('pm2_5_atm')
fig.show()

# Create hourly heatmap
heatmap = viz.create_hourly_heatmap('pm2_5_atm')
heatmap.show()
```

### Custom Analysis
```python
from spatial_temporal_analyzer import SpatialTemporalAnalyzer

# Initialize analyzer
analyzer = SpatialTemporalAnalyzer(data)

# Analyze temporal trends
trends = analyzer.analyze_temporal_trends('pm2_5_atm')

# Detect pollution events
events = analyzer.detect_pollution_events()

# Generate comprehensive report
report = analyzer.generate_summary_report()
```

## 🎨 Dashboard Features

### Overview Tab
- Real-time current air quality status
- Interactive time series with AQI bands
- Key statistics and metrics
- AQI category distribution

### Time Analysis Tab
- Hourly pattern heatmap
- Distribution analysis with multiple plots
- Statistical summaries

### Spatial Tab
- Interactive map with sensor location
- Data point visualization on map
- Geographic context

### Reports Tab
- Comprehensive analysis reports
- Trend analysis and significance testing
- Pollution event detection
- Health recommendations
- Downloadable reports in JSON format

## 📈 Analysis Capabilities

### Temporal Analysis
- **Trend Detection**: Linear regression analysis with statistical significance
- **Seasonal Patterns**: Hour-of-day and day-of-week pattern analysis
- **Peak Detection**: Automated identification of pollution spikes
- **Data Quality**: Gap detection and completeness assessment

### Air Quality Assessment
- **AQI Categorization**: EPA standard classification
- **Health Impact**: Time spent in unhealthy conditions
- **Event Detection**: Pollution episode identification
- **Threshold Exceedances**: WHO and EPA guideline violations

### Visualization Options
- **Interactive Plots**: Plotly-based interactive charts
- **Static Plots**: High-quality matplotlib figures
- **Maps**: Folium-based geographic visualization
- **Dashboards**: Multi-panel Streamlit interface

## 🎯 Use Cases

### Environmental Monitoring
- Track air quality trends over time
- Identify pollution sources and patterns
- Monitor compliance with air quality standards
- Generate reports for regulatory agencies

### Health Applications
- Personal exposure assessment
- Health risk evaluation
- Activity planning based on air quality
- Sensitive group alerts

### Research and Analysis
- Environmental data science projects
- Pollution source identification
- Temporal pattern analysis
- Spatial air quality mapping

## 🔧 Configuration Options

### Data Collection
- `UPDATE_INTERVAL_MINUTES`: Data collection frequency
- `DATA_RETENTION_DAYS`: How long to keep historical data
- `SHEET_RANGE`: Google Sheets range to read

### Analysis Settings
- `AQI_THRESHOLDS`: Customizable air quality thresholds
- Alert thresholds for notifications
- Analysis window sizes

### Visualization
- `THEME_COLORS`: Customizable color scheme
- Plot styling options
- Map tile sources

## 🛠️ Troubleshooting

### Common Issues

**Authentication Errors**
- Verify credentials.json is in the correct location
- Check that the service account has access to your spreadsheet
- Ensure Google Sheets API is enabled

**Data Loading Issues**
- Verify spreadsheet ID is correct
- Check that data columns match expected format
- Ensure timestamp format is parseable

**Dashboard Problems**
- Install all required dependencies
- Check Python version compatibility (3.8+)
- Verify port 8501 is available

### Performance Tips
- Limit data range for large datasets
- Use caching for repeated analysis
- Consider data sampling for very high-frequency data

## 📋 Dependencies

Key packages:
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive visualizations
- `folium`: Geographic mapping
- `streamlit`: Web dashboard framework
- `google-api-python-client`: Google Sheets API
- `scipy`: Statistical analysis
- `scikit-learn`: Machine learning utilities

## 🤝 Contributing

This project provides a solid foundation for Purple Air sensor data analysis. Feel free to extend it with:
- Additional sensor types and data sources
- Advanced machine learning models
- Mobile-responsive dashboard improvements
- Real-time alerting systems
- Data export and reporting features

## 📄 License

This project is provided as-is for educational and research purposes. Please ensure compliance with relevant data privacy and usage policies when working with sensor data.

## 🆘 Support

For questions about:
- **Setup**: Check configuration files and API credentials
- **Data Issues**: Verify Google Sheets format and permissions
- **Analysis**: Review documentation and example usage
- **Visualization**: Check plotly and streamlit documentation

---

*Built with ❤️ for environmental monitoring and data science* 