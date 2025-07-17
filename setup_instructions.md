# 🚀 Quick Setup Guide

Your Purple Air sensor project is ready to use! Follow these simple steps:

## ✅ What's Already Configured

- **Spreadsheet ID**: `1KLwB85EZK1WvCCh5iWtkl2gxd_4B__jRWsdDoU1fjs0`
- **Data columns mapped**: TimeStamp, Temperature, Humidity, PM2.5, etc.
- **White and blue theme**: Applied as per your preference

## 📋 Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Google Sheets Access
Since you mentioned you've added the JSON file:
- ✅ Make sure `credentials.json` is in the project root folder
- ✅ Ensure your spreadsheet is shared with the service account email

### 3. Test Your Setup
Run the example script to verify everything works:
```bash
python example_usage.py
```

This will:
- Connect to your Google Sheet
- Load and analyze your Purple Air data
- Show basic statistics and trends
- Create sample visualizations
- Save charts to the `charts/` folder

### 4. Launch the Dashboard
Start the interactive web dashboard:
```bash
streamlit run streamlit_dashboard.py
```

Then open your browser to: http://localhost:8501

## 🎯 What You'll See

### Example Output from `example_usage.py`:
```
🌬️ Purple Air Sensor Data Analysis
==================================================
📊 Loading data from Google Sheets...
Spreadsheet ID: 1KLwB85EZK1WvCCh5iWtkl2gxd_4B__jRWsdDoU1fjs0
✅ Successfully loaded 1440 data points
📅 Data range: 2024-01-01 00:00:00 to 2024-01-02 00:00:00

📋 Data Structure:
Columns: ['timestamp', 'temperature', 'humidity', 'dewpoint', 'pressure', 'pm1_0', 'pm2_5_atm', 'pm10_atm', 'pm2_5_aqi']

🎯 Current PM2.5: 15.2 μg/m³
✅ Air Quality: Good

📊 Analysis Results:
   • Trend: increasing
   • Time in unhealthy conditions: 2.1%
   • Pollution events detected: 0
```

### Dashboard Features:
- **Real-time status**: Current PM2.5 levels and air quality
- **Interactive charts**: Time series with AQI bands
- **Pattern analysis**: Hourly heatmaps showing daily patterns
- **Health metrics**: Time spent in unhealthy conditions
- **Data export**: Download reports and raw data

## 🔧 Troubleshooting

**If you get authentication errors:**
1. Check that `credentials.json` exists in the project folder
2. Verify the spreadsheet is shared with your service account
3. Make sure Google Sheets API is enabled in your Google Cloud project

**If no data loads:**
1. Verify your spreadsheet has data in the expected columns
2. Check that timestamps are in a recognizable format
3. Ensure the sheet name is "Sheet1" (or update `SHEET_RANGE` in config.py)

**If visualizations fail:**
- Some packages may need additional installation for image export
- The HTML files will always work even if PNG export fails

## 🌟 Next Steps

Once everything is working:

1. **Customize the analysis**: Modify thresholds in `config.py`
2. **Add your location**: Set sensor coordinates for mapping
3. **Schedule data collection**: Set up automated data pulls
4. **Create alerts**: Add email/SMS notifications for air quality alerts
5. **Extend analysis**: Add weather correlations, machine learning predictions

## 💡 Pro Tips

- The dashboard auto-refreshes data every 5 minutes when enabled
- You can analyze different time ranges (1 hour to 1 week)
- All charts are interactive - click, zoom, and hover for details
- Export any chart as PNG/PDF for reports
- Download raw data as CSV for external analysis

Happy monitoring! 🌬️📊 