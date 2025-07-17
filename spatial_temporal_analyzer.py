"""
Spatial Temporal Analysis Module for Purple Air Sensor Data
Handles time series analysis, trend detection, and pattern recognition
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.signal import find_peaks
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import logging
import config

logger = logging.getLogger(__name__)

class SpatialTemporalAnalyzer:
    """Performs spatial temporal analysis on Purple Air sensor data"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize analyzer with sensor data
        
        Args:
            data (pd.DataFrame): Purple Air sensor data
        """
        self.data = data.copy()
        self.analysis_results = {}
        
    def analyze_temporal_trends(self, metric: str = 'pm2_5_atm') -> Dict:
        """
        Analyze temporal trends in the data
        
        Args:
            metric (str): Column name to analyze
            
        Returns:
            Dict: Analysis results including trends, patterns, statistics
        """
        if metric not in self.data.columns:
            logger.warning(f"Metric '{metric}' not found in data")
            return {}
        
        # Remove null values
        clean_data = self.data.dropna(subset=[metric, 'timestamp'])
        
        if len(clean_data) < 2:
            logger.warning("Insufficient data for trend analysis")
            return {}
        
        # Calculate basic statistics
        stats_summary = {
            'mean': clean_data[metric].mean(),
            'median': clean_data[metric].median(),
            'std': clean_data[metric].std(),
            'min': clean_data[metric].min(),
            'max': clean_data[metric].max(),
            'count': len(clean_data)
        }
        
        # Trend analysis using linear regression
        x_numeric = pd.to_numeric(clean_data['timestamp']) / 10**9  # Convert to seconds
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, clean_data[metric])
        
        trend_analysis = {
            'slope': slope,
            'r_squared': r_value**2,
            'p_value': p_value,
            'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
            'trend_strength': abs(r_value)
        }
        
        # Hourly patterns
        hourly_stats = self._analyze_hourly_patterns(clean_data, metric)
        
        # Daily patterns
        daily_stats = self._analyze_daily_patterns(clean_data, metric)
        
        # Peak detection
        peaks_analysis = self._detect_peaks(clean_data, metric)
        
        results = {
            'metric': metric,
            'statistics': stats_summary,
            'trend': trend_analysis,
            'hourly_patterns': hourly_stats,
            'daily_patterns': daily_stats,
            'peaks': peaks_analysis,
            'data_quality': self._assess_data_quality(clean_data)
        }
        
        self.analysis_results[f'temporal_{metric}'] = results
        return results
    
    def _analyze_hourly_patterns(self, data: pd.DataFrame, metric: str) -> Dict:
        """Analyze patterns by hour of day"""
        if 'hour' not in data.columns:
            data['hour'] = data['timestamp'].dt.hour
        
        hourly_stats = data.groupby('hour')[metric].agg([
            'mean', 'median', 'std', 'count'
        ]).round(2)
        
        # Find peak hours
        peak_hour = hourly_stats['mean'].idxmax()
        low_hour = hourly_stats['mean'].idxmin()
        
        return {
            'hourly_averages': hourly_stats.to_dict(),
            'peak_hour': int(peak_hour),
            'peak_value': float(hourly_stats.loc[peak_hour, 'mean']),
            'low_hour': int(low_hour),
            'low_value': float(hourly_stats.loc[low_hour, 'mean']),
            'hour_variation': float(hourly_stats['mean'].std())
        }
    
    def _analyze_daily_patterns(self, data: pd.DataFrame, metric: str) -> Dict:
        """Analyze patterns by day of week"""
        if 'day_of_week' not in data.columns:
            data['day_of_week'] = data['timestamp'].dt.dayofweek
        
        daily_stats = data.groupby('day_of_week')[metric].agg([
            'mean', 'median', 'std', 'count'
        ]).round(2)
        
        # Compare weekday vs weekend
        if 'is_weekend' not in data.columns:
            data['is_weekend'] = data['day_of_week'].isin([5, 6])
        
        weekend_avg = data[data['is_weekend']][metric].mean()
        weekday_avg = data[~data['is_weekend']][metric].mean()
        
        return {
            'daily_averages': daily_stats.to_dict(),
            'weekend_average': float(weekend_avg) if not pd.isna(weekend_avg) else None,
            'weekday_average': float(weekday_avg) if not pd.isna(weekday_avg) else None,
            'weekend_vs_weekday_ratio': float(weekend_avg / weekday_avg) if weekday_avg != 0 and not pd.isna(weekend_avg) else None
        }
    
    def _detect_peaks(self, data: pd.DataFrame, metric: str) -> Dict:
        """Detect peaks and anomalies in the data"""
        values = data[metric].values
        
        # Find peaks
        peaks, properties = find_peaks(values, height=np.percentile(values, 75))
        
        # Find valleys (inverted peaks)
        valleys, _ = find_peaks(-values, height=-np.percentile(values, 25))
        
        # Calculate anomaly threshold (values beyond 2 standard deviations)
        mean_val = np.mean(values)
        std_val = np.std(values)
        anomaly_threshold = mean_val + 2 * std_val
        anomalies = data[data[metric] > anomaly_threshold]
        
        return {
            'num_peaks': len(peaks),
            'num_valleys': len(valleys),
            'highest_peak': float(np.max(values[peaks])) if len(peaks) > 0 else None,
            'lowest_valley': float(np.min(values[valleys])) if len(valleys) > 0 else None,
            'anomaly_threshold': float(anomaly_threshold),
            'num_anomalies': len(anomalies),
            'anomaly_timestamps': anomalies['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist() if len(anomalies) > 0 else []
        }
    
    def _assess_data_quality(self, data: pd.DataFrame) -> Dict:
        """Assess the quality of the data"""
        total_expected = None
        if len(data) > 1:
            time_diff = (data['timestamp'].max() - data['timestamp'].min()).total_seconds()
            total_expected = int(time_diff / 60)  # Expected records (1 per minute)
        
        return {
            'total_records': len(data),
            'expected_records': total_expected,
            'completeness_ratio': len(data) / total_expected if total_expected else None,
            'time_span_hours': float((data['timestamp'].max() - data['timestamp'].min()).total_seconds() / 3600) if len(data) > 1 else 0,
            'missing_data_gaps': self._find_data_gaps(data)
        }
    
    def _find_data_gaps(self, data: pd.DataFrame) -> List[Dict]:
        """Find significant gaps in data collection"""
        if len(data) < 2:
            return []
        
        # Sort by timestamp
        data_sorted = data.sort_values('timestamp')
        
        # Calculate time differences between consecutive records
        time_diffs = data_sorted['timestamp'].diff()
        
        # Find gaps larger than 5 minutes (indicating missing data)
        large_gaps = time_diffs[time_diffs > timedelta(minutes=5)]
        
        gaps = []
        for idx, gap in large_gaps.items():
            start_time = data_sorted.loc[idx-1, 'timestamp'] if idx > 0 else None
            end_time = data_sorted.loc[idx, 'timestamp']
            gaps.append({
                'start': start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else None,
                'end': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration_minutes': int(gap.total_seconds() / 60)
            })
        
        return gaps
    
    def calculate_air_quality_metrics(self) -> Dict:
        """Calculate comprehensive air quality metrics"""
        metrics = {}
        
        if 'pm2_5_atm' in self.data.columns:
            pm25_data = self.data.dropna(subset=['pm2_5_atm'])
            
            # AQI distribution
            if 'aqi_category' in pm25_data.columns:
                aqi_distribution = pm25_data['aqi_category'].value_counts().to_dict()
                metrics['aqi_distribution'] = aqi_distribution
                
                # Time in unhealthy conditions
                unhealthy_conditions = ['Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous']
                unhealthy_count = pm25_data[pm25_data['aqi_category'].isin(unhealthy_conditions)].shape[0]
                metrics['unhealthy_time_percentage'] = (unhealthy_count / len(pm25_data)) * 100 if len(pm25_data) > 0 else 0
            
            # PM2.5 exposure metrics
            metrics['pm25_exposure'] = {
                'average': float(pm25_data['pm2_5_atm'].mean()),
                'max_1hour': float(pm25_data['pm2_5_atm'].max()),
                'percentile_95': float(pm25_data['pm2_5_atm'].quantile(0.95)),
                'exceedances_who_guideline': int((pm25_data['pm2_5_atm'] > 15).sum()),  # WHO guideline
                'exceedances_epa_standard': int((pm25_data['pm2_5_atm'] > 35).sum())  # EPA standard
            }
        
        return metrics
    
    def detect_pollution_events(self, threshold_multiplier: float = 2.0) -> List[Dict]:
        """
        Detect pollution events (sudden spikes in PM2.5)
        
        Args:
            threshold_multiplier (float): Multiplier for standard deviation threshold
            
        Returns:
            List[Dict]: Detected pollution events
        """
        if 'pm2_5_atm' not in self.data.columns:
            return []
        
        pm25_data = self.data.dropna(subset=['pm2_5_atm', 'timestamp']).sort_values('timestamp')
        
        if len(pm25_data) < 10:
            return []
        
        # Calculate rolling mean and std
        window_size = min(60, len(pm25_data) // 4)  # 1 hour window or 1/4 of data
        pm25_data['rolling_mean'] = pm25_data['pm2_5_atm'].rolling(window=window_size, center=True).mean()
        pm25_data['rolling_std'] = pm25_data['pm2_5_atm'].rolling(window=window_size, center=True).std()
        
        # Define threshold for events
        pm25_data['threshold'] = pm25_data['rolling_mean'] + (threshold_multiplier * pm25_data['rolling_std'])
        
        # Find events
        events = pm25_data[pm25_data['pm2_5_atm'] > pm25_data['threshold']].copy()
        
        # Group consecutive events
        event_groups = []
        current_group = []
        
        for _, event in events.iterrows():
            if not current_group:
                current_group.append(event)
            else:
                # Check if event is within 30 minutes of last event
                time_diff = (event['timestamp'] - current_group[-1]['timestamp']).total_seconds()
                if time_diff <= 1800:  # 30 minutes
                    current_group.append(event)
                else:
                    # Process current group and start new one
                    if len(current_group) >= 3:  # Minimum 3 consecutive readings
                        event_groups.append(current_group)
                    current_group = [event]
        
        # Don't forget the last group
        if len(current_group) >= 3:
            event_groups.append(current_group)
        
        # Format results
        pollution_events = []
        for i, group in enumerate(event_groups):
            group_df = pd.DataFrame(group)
            pollution_events.append({
                'event_id': i + 1,
                'start_time': group_df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': group_df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S'),
                'duration_minutes': int((group_df['timestamp'].max() - group_df['timestamp'].min()).total_seconds() / 60),
                'peak_pm25': float(group_df['pm2_5_atm'].max()),
                'average_pm25': float(group_df['pm2_5_atm'].mean()),
                'severity': self._classify_event_severity(group_df['pm2_5_atm'].max())
            })
        
        return pollution_events
    
    def _classify_event_severity(self, peak_pm25: float) -> str:
        """Classify pollution event severity"""
        if peak_pm25 <= 35:
            return 'Moderate'
        elif peak_pm25 <= 55:
            return 'Unhealthy for Sensitive'
        elif peak_pm25 <= 150:
            return 'Unhealthy'
        elif peak_pm25 <= 250:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'
    
    def generate_summary_report(self) -> Dict:
        """Generate a comprehensive summary report"""
        report = {
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_period': {
                'start': self.data['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S') if len(self.data) > 0 else None,
                'end': self.data['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S') if len(self.data) > 0 else None,
                'total_hours': float((self.data['timestamp'].max() - self.data['timestamp'].min()).total_seconds() / 3600) if len(self.data) > 1 else 0
            }
        }
        
        # Add temporal analysis for PM2.5
        if 'pm2_5_atm' in self.data.columns:
            report['pm25_analysis'] = self.analyze_temporal_trends('pm2_5_atm')
        
        # Add air quality metrics
        report['air_quality_metrics'] = self.calculate_air_quality_metrics()
        
        # Add pollution events
        report['pollution_events'] = self.detect_pollution_events()
        
        # Add recommendations
        report['recommendations'] = self._generate_recommendations()
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        if 'pm2_5_atm' in self.data.columns:
            pm25_avg = self.data['pm2_5_atm'].mean()
            
            if pm25_avg > 35:
                recommendations.append("Average PM2.5 levels exceed EPA standards. Consider air filtration systems.")
            elif pm25_avg > 15:
                recommendations.append("PM2.5 levels above WHO guidelines. Monitor sensitive individuals.")
            
            # Check for high variability
            pm25_std = self.data['pm2_5_atm'].std()
            if pm25_std > pm25_avg * 0.5:
                recommendations.append("High variability in PM2.5 levels detected. Investigate pollution sources.")
        
        # Check data quality
        if len(self.data) > 0:
            data_quality = self._assess_data_quality(self.data)
            if data_quality.get('completeness_ratio', 1) < 0.9:
                recommendations.append("Data collection completeness below 90%. Check sensor connectivity.")
        
        if not recommendations:
            recommendations.append("Air quality levels are within acceptable ranges. Continue monitoring.")
        
        return recommendations

# Utility functions for quick analysis
def quick_analysis(data: pd.DataFrame) -> Dict:
    """
    Perform quick analysis on Purple Air sensor data
    
    Args:
        data (pd.DataFrame): Sensor data
        
    Returns:
        Dict: Analysis summary
    """
    analyzer = SpatialTemporalAnalyzer(data)
    return analyzer.generate_summary_report()

def detect_air_quality_alerts(data: pd.DataFrame, alert_threshold: float = 35.0) -> List[Dict]:
    """
    Detect current air quality alerts
    
    Args:
        data (pd.DataFrame): Recent sensor data
        alert_threshold (float): PM2.5 threshold for alerts
        
    Returns:
        List[Dict]: Current alerts
    """
    if 'pm2_5_atm' not in data.columns or len(data) == 0:
        return []
    
    # Get latest reading
    latest_data = data.sort_values('timestamp').iloc[-1]
    
    alerts = []
    if latest_data['pm2_5_atm'] > alert_threshold:
        alerts.append({
            'timestamp': latest_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'pm25_value': float(latest_data['pm2_5_atm']),
            'alert_level': 'HIGH' if latest_data['pm2_5_atm'] > 55 else 'MODERATE',
            'message': f"PM2.5 level of {latest_data['pm2_5_atm']:.1f} μg/m³ exceeds threshold of {alert_threshold} μg/m³"
        })
    
    return alerts 