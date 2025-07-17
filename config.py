"""
Configuration file for Purple Air Sensor Analysis Project
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Try to get from Streamlit secrets first, then environment variables, then defaults
def get_config(key, default=None):
    """Get configuration value from Streamlit secrets, env vars, or default"""
    try:
        # Try Streamlit secrets first (for deployment)
        import streamlit as st_check
        if hasattr(st_check, 'secrets') and key in st_check.secrets:
            return st_check.secrets[key]
    except ImportError:
        # Streamlit not available (e.g., running scripts outside Streamlit)
        pass
    except Exception:
        # Other errors accessing secrets
        pass
    
    # Fall back to environment variables (for local development)
    return os.getenv(key, default)

# Google Sheets Configuration
SPREADSHEET_ID = get_config('SPREADSHEET_ID', '1KLwB85EZK1WvCCh5iWtkl2gxd_4B__jRWsdDoU1fjs0')
SHEET_RANGE = get_config('SHEET_RANGE', 'PurpleAir002_AJLC Building!A:Z')

# For deployment, credentials will come from Streamlit secrets
# For local development, use credentials.json file
CREDENTIALS_FILE = get_config('CREDENTIALS_FILE', 'credentials.json')

# Purple Air Sensor Configuration
SENSOR_LOCATION = {
    'latitude': float(get_config('SENSOR_LAT', '41.29075599398253')),
    'longitude': float(get_config('SENSOR_LON', '-82.22151197237143')),
    'name': get_config('SENSOR_NAME', 'AJLC Building Purple Air Sensor')
}

# Data Collection Settings
UPDATE_INTERVAL_MINUTES = int(get_config('UPDATE_INTERVAL', '1'))
DATA_RETENTION_DAYS = int(get_config('DATA_RETENTION_DAYS', '30'))

# Column mapping for the user's specific data format
COLUMN_MAPPING = {
    'timestamp': 'TimeStamp',
    'temperature': 'Temperature (°F)',
    'humidity': 'Humidity (%)',
    'dewpoint': 'Dewpoint (°F)',
    'pressure': 'Pressure (hPa)',
    'pm1_0': 'PM1.0 :cf_1( µg/m³)',
    'pm2_5_atm': 'PM2.5 :cf_1( µg/m³)',  # Main PM2.5 column
    'pm10_atm': 'PM10.0 :cf_1( µg/m³)',
    'pm2_5_aqi': 'PM2.5 AQI'
}

# Analysis Settings
AQI_THRESHOLDS = {
    'good': 12,
    'moderate': 35.4,
    'unhealthy_sensitive': 55.4,
    'unhealthy': 150.4,
    'very_unhealthy': 250.4,
    'hazardous': 500.4
}

# Visualization Settings using darker blue theme
THEME_COLORS = {
    'primary': '#4A90E2',    # Lighter blue for dark theme
    'secondary': '#A23B72',  # Purple  
    'background': '#1E1E1E', # Dark background
    'text': '#E1E1E1',       # Light gray text
    'success': '#28A745',    # Green
    'warning': '#FFC107',    # Yellow
    'danger': '#DC3545'      # Red
}

# File Paths
DATA_DIR = 'data'
LOGS_DIR = 'logs'
CHARTS_DIR = 'charts'

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, CHARTS_DIR]:
    os.makedirs(directory, exist_ok=True) 