"""
Data Collection Module for Purple Air Sensor Data
Handles Google Sheets API integration and data retrieval
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, List, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{config.LOGS_DIR}/data_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PurpleAirDataCollector:
    """Handles data collection from Purple Air sensor via Google Sheets API"""
    
    def __init__(self, spreadsheet_id: str, credentials_file: str = None):
        """
        Initialize the data collector
        
        Args:
            spreadsheet_id (str): Google Sheets spreadsheet ID
            credentials_file (str): Path to Google Service Account credentials
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file or config.CREDENTIALS_FILE
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Define the scope
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            
            creds = None
            
            # Try to get credentials from Streamlit secrets first (for deployment)
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and 'google_credentials' in st.secrets:
                    import json
                    # Load credentials from Streamlit secrets
                    credentials_info = json.loads(st.secrets['google_credentials'])
                    creds = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
                    logger.info("Using credentials from Streamlit secrets")
            except Exception as e:
                logger.info(f"Streamlit secrets not available: {str(e)}")
            
            # Fall back to local credentials file if secrets didn't work
            if creds is None:
                import os
                if os.path.exists(self.credentials_file):
                    creds = Credentials.from_service_account_file(
                        self.credentials_file, scopes=SCOPES
                    )
                    logger.info("Using local credentials file")
                else:
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=creds)
            logger.info("Successfully authenticated with Google Sheets API")
            
        except Exception as e:
            logger.error(f"Failed to authenticate: {str(e)}")
            raise
    
    def fetch_data(self, range_name: str = None) -> pd.DataFrame:
        """
        Fetch data from Google Sheets
        
        Args:
            range_name (str): Sheet range to fetch (e.g., 'Sheet1!A:Z')
            
        Returns:
            pd.DataFrame: Retrieved sensor data
        """
        if not range_name:
            range_name = config.SHEET_RANGE
            
        try:
            # Call the Sheets API
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("No data found in spreadsheet")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])  # First row as header
            
            # Clean and process data
            df = self._clean_data(df)
            
            logger.info(f"Successfully fetched {len(df)} rows of data")
            return df
            
        except HttpError as error:
            logger.error(f"HTTP error occurred: {error}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and process the raw sensor data
        
        Args:
            df (pd.DataFrame): Raw data from spreadsheet
            
        Returns:
            pd.DataFrame: Cleaned data
        """
        if df.empty:
            return df
        
        # Map original column names to standardized names
        if config.COLUMN_MAPPING['timestamp'] in df.columns:
            df['timestamp'] = pd.to_datetime(df[config.COLUMN_MAPPING['timestamp']], errors='coerce')
        
        # Rename columns to standardized names for easier processing
        column_rename_map = {}
        for standard_name, original_name in config.COLUMN_MAPPING.items():
            if original_name in df.columns and standard_name != 'timestamp':
                column_rename_map[original_name] = standard_name
        
        if column_rename_map:
            df = df.rename(columns=column_rename_map)
        
        # Convert numeric columns (using standardized names)
        numeric_columns = ['pm2_5_atm', 'pm10_atm', 'pm1_0', 'temperature', 'humidity', 
                          'pressure', 'dewpoint', 'pm2_5_aqi', 'latitude', 'longitude']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with invalid timestamps
        if 'timestamp' in df.columns:
            df = df.dropna(subset=['timestamp'])
            df = df.sort_values('timestamp')
        
        # Add calculated fields
        df = self._add_calculated_fields(df)
        
        # Remove duplicates
        if 'timestamp' in df.columns:
            df = df.drop_duplicates(subset=['timestamp'], keep='last')
        
        logger.info(f"Data cleaned: {len(df)} valid rows remaining")
        return df
    
    def _add_calculated_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add calculated fields like AQI, categories, etc.
        
        Args:
            df (pd.DataFrame): Cleaned sensor data
            
        Returns:
            pd.DataFrame: Data with additional calculated fields
        """
        if 'pm2_5_atm' in df.columns:
            # Calculate AQI category based on PM2.5
            df['aqi_category'] = df['pm2_5_atm'].apply(self._get_aqi_category)
            
            # Add color coding for visualization
            df['aqi_color'] = df['aqi_category'].map({
                'Good': config.THEME_COLORS['success'],
                'Moderate': config.THEME_COLORS['warning'],
                'Unhealthy for Sensitive Groups': '#FF8C00',
                'Unhealthy': config.THEME_COLORS['danger'],
                'Very Unhealthy': '#8B0000',
                'Hazardous': '#7B0F7B'
            })
        
        # Add time-based features
        if 'timestamp' in df.columns:
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6])
        
        return df
    
    def _get_aqi_category(self, pm25_value: float) -> str:
        """
        Determine AQI category based on PM2.5 value
        
        Args:
            pm25_value (float): PM2.5 concentration
            
        Returns:
            str: AQI category
        """
        if pd.isna(pm25_value):
            return 'Unknown'
        
        thresholds = config.AQI_THRESHOLDS
        
        if pm25_value <= thresholds['good']:
            return 'Good'
        elif pm25_value <= thresholds['moderate']:
            return 'Moderate'
        elif pm25_value <= thresholds['unhealthy_sensitive']:
            return 'Unhealthy for Sensitive Groups'
        elif pm25_value <= thresholds['unhealthy']:
            return 'Unhealthy'
        elif pm25_value <= thresholds['very_unhealthy']:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'
    
    def get_recent_data(self, hours: int = 24) -> pd.DataFrame:
        """
        Get data from the last N hours
        
        Args:
            hours (int): Number of hours to look back
            
        Returns:
            pd.DataFrame: Recent sensor data
        """
        df = self.fetch_data()
        
        if df.empty or 'timestamp' not in df.columns:
            return df
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = df[df['timestamp'] >= cutoff_time]
        
        logger.info(f"Retrieved {len(recent_data)} records from last {hours} hours")
        return recent_data
    
    def save_data(self, df: pd.DataFrame, filename: str = None):
        """
        Save data to local file
        
        Args:
            df (pd.DataFrame): Data to save
            filename (str): Output filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{config.DATA_DIR}/purple_air_data_{timestamp}.csv"
        
        try:
            df.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")

# Utility function for quick data access
def get_sensor_data(spreadsheet_id: str, hours: int = 24) -> pd.DataFrame:
    """
    Quick function to get recent sensor data
    
    Args:
        spreadsheet_id (str): Google Sheets ID
        hours (int): Hours of data to retrieve
        
    Returns:
        pd.DataFrame: Recent sensor data
    """
    collector = PurpleAirDataCollector(spreadsheet_id)
    return collector.get_recent_data(hours) 