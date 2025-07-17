"""
Visualization Module for Purple Air Sensor Data
Creates interactive plots, maps, and dashboards
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from folium.plugins import HeatMapWithTime
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import config

# Set style for matplotlib
plt.style.use('default')
sns.set_palette("husl")

class PurpleAirVisualizer:
    """Creates visualizations for Purple Air sensor data"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize visualizer with sensor data
        
        Args:
            data (pd.DataFrame): Purple Air sensor data
        """
        self.data = data.copy()
        self.colors = config.THEME_COLORS
        
    def create_time_series_plot(self, metric: str = 'pm2_5_atm', 
                               interactive: bool = True, 
                               show_aqi_bands: bool = True) -> Union[go.Figure, plt.Figure]:
        """
        Create time series plot for a specific metric
        
        Args:
            metric (str): Column to plot
            interactive (bool): Whether to create interactive plot
            show_aqi_bands (bool): Whether to show AQI threshold bands
            
        Returns:
            Plotly figure or matplotlib figure
        """
        if metric not in self.data.columns:
            raise ValueError(f"Metric '{metric}' not found in data")
        
        clean_data = self.data.dropna(subset=[metric, 'timestamp']).sort_values('timestamp')
        
        if interactive:
            return self._create_interactive_time_series(clean_data, metric, show_aqi_bands)
        else:
            return self._create_static_time_series(clean_data, metric, show_aqi_bands)
    
    def _create_interactive_time_series(self, data: pd.DataFrame, metric: str, show_aqi_bands: bool) -> go.Figure:
        """Create interactive time series plot using Plotly"""
        fig = go.Figure()
        
        # Add main time series
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data[metric],
            mode='lines+markers',
            name=f'{metric.replace("_", " ").title()}',
            line=dict(color=self.colors['primary'], width=2),
            marker=dict(size=4),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Time: %{x}<br>' +
                         'Value: %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        # Add AQI bands for PM2.5
        if show_aqi_bands and metric == 'pm2_5_atm':
            self._add_aqi_bands(fig, data['timestamp'].min(), data['timestamp'].max())
        
        # Update layout with dark theme
        fig.update_layout(
            title=f'{metric.replace("_", " ").title()} Over Time',
            xaxis_title='Time',
            yaxis_title=f'{metric.replace("_", " ").title()} (μg/m³)' if 'pm' in metric else metric.replace("_", " ").title(),
            hovermode='x unified',
            showlegend=True,
            plot_bgcolor='#1E1E1E',
            paper_bgcolor='#1E1E1E',
            font=dict(family="Arial", size=12, color='#E1E1E1'),
            margin=dict(l=60, r=60, t=80, b=60)
        )
        
        # Style axes for dark theme
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#444', linecolor='#666')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#444', linecolor='#666')
        
        return fig
    
    def _add_aqi_bands(self, fig: go.Figure, start_time: datetime, end_time: datetime):
        """Add AQI threshold bands to the plot"""
        aqi_bands = [
            (0, config.AQI_THRESHOLDS['good'], 'Good', '#00E400'),
            (config.AQI_THRESHOLDS['good'], config.AQI_THRESHOLDS['moderate'], 'Moderate', '#FFFF00'),
            (config.AQI_THRESHOLDS['moderate'], config.AQI_THRESHOLDS['unhealthy_sensitive'], 'Unhealthy for Sensitive', '#FF7E00'),
            (config.AQI_THRESHOLDS['unhealthy_sensitive'], config.AQI_THRESHOLDS['unhealthy'], 'Unhealthy', '#FF0000'),
            (config.AQI_THRESHOLDS['unhealthy'], config.AQI_THRESHOLDS['very_unhealthy'], 'Very Unhealthy', '#8F3F97'),
            (config.AQI_THRESHOLDS['very_unhealthy'], 500, 'Hazardous', '#7E0023')
        ]
        
        for i, (y0, y1, name, color) in enumerate(aqi_bands):
            fig.add_shape(
                type="rect",
                x0=start_time, x1=end_time,
                y0=y0, y1=y1,
                fillcolor=color,
                opacity=0.1,
                layer="below",
                line_width=0
            )
            
            # Add label
            fig.add_annotation(
                x=start_time + (end_time - start_time) * 0.02,
                y=(y0 + y1) / 2,
                text=name,
                showarrow=False,
                font=dict(size=10, color=color),
                bgcolor="white",
                bordercolor=color,
                borderwidth=1
            )
    
    def _create_static_time_series(self, data: pd.DataFrame, metric: str, show_aqi_bands: bool) -> plt.Figure:
        """Create static time series plot using matplotlib"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot main line
        ax.plot(data['timestamp'], data[metric], 
                color=self.colors['primary'], linewidth=2, alpha=0.8)
        
        # Add AQI bands for PM2.5
        if show_aqi_bands and metric == 'pm2_5_atm':
            self._add_static_aqi_bands(ax)
        
        # Formatting
        ax.set_xlabel('Time')
        ax.set_ylabel(f'{metric.replace("_", " ").title()} (μg/m³)' if 'pm' in metric else metric.replace("_", " ").title())
        ax.set_title(f'{metric.replace("_", " ").title()} Over Time')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig
    
    def _add_static_aqi_bands(self, ax):
        """Add AQI bands to static plot"""
        aqi_bands = [
            (0, config.AQI_THRESHOLDS['good'], 'Good', '#00E400'),
            (config.AQI_THRESHOLDS['good'], config.AQI_THRESHOLDS['moderate'], 'Moderate', '#FFFF00'),
            (config.AQI_THRESHOLDS['moderate'], config.AQI_THRESHOLDS['unhealthy_sensitive'], 'Unhealthy for Sensitive', '#FF7E00'),
            (config.AQI_THRESHOLDS['unhealthy_sensitive'], config.AQI_THRESHOLDS['unhealthy'], 'Unhealthy', '#FF0000'),
            (config.AQI_THRESHOLDS['unhealthy'], config.AQI_THRESHOLDS['very_unhealthy'], 'Very Unhealthy', '#8F3F97'),
            (config.AQI_THRESHOLDS['very_unhealthy'], 500, 'Hazardous', '#7E0023')
        ]
        
        for y0, y1, name, color in aqi_bands:
            ax.axhspan(y0, y1, alpha=0.1, color=color, label=name)
    
    def create_hourly_heatmap(self, metric: str = 'pm2_5_atm') -> go.Figure:
        """
        Create hourly heatmap showing patterns by day and hour
        
        Args:
            metric (str): Column to analyze
            
        Returns:
            Plotly heatmap figure
        """
        clean_data = self.data.dropna(subset=[metric, 'timestamp'])
        
        if len(clean_data) == 0:
            return go.Figure()
        
        # Create hour and date columns
        clean_data['hour'] = clean_data['timestamp'].dt.hour
        clean_data['date'] = clean_data['timestamp'].dt.date
        
        # Create pivot table for heatmap
        heatmap_data = clean_data.pivot_table(
            values=metric, 
            index='date', 
            columns='hour', 
            aggfunc='mean'
        )
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=[f'{h:02d}:00' for h in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale='RdYlBu_r',
            hoverongaps=False,
            hovertemplate='Hour: %{x}<br>Date: %{y}<br>Value: %{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Hourly {metric.replace("_", " ").title()} Patterns',
            xaxis_title='Hour of Day',
            yaxis_title='Date',
            font=dict(family="Arial", size=12, color='#E1E1E1'),
            plot_bgcolor='#1E1E1E',
            paper_bgcolor='#1E1E1E'
        )
        
        return fig
    
    def create_distribution_plot(self, metric: str = 'pm2_5_atm') -> go.Figure:
        """
        Create distribution plot with statistics
        
        Args:
            metric (str): Column to analyze
            
        Returns:
            Plotly distribution figure
        """
        clean_data = self.data.dropna(subset=[metric])
        
        if len(clean_data) == 0:
            return go.Figure()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Histogram', 'Box Plot', 'Time Series', 'QQ Plot'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(x=clean_data[metric], nbinsx=30, name='Distribution'),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=clean_data[metric], name='Box Plot'),
            row=1, col=2
        )
        
        # Time series (if timestamp available)
        if 'timestamp' in clean_data.columns:
            fig.add_trace(
                go.Scatter(x=clean_data['timestamp'], y=clean_data[metric], 
                          mode='lines', name='Time Series'),
                row=2, col=1
            )
        
        # QQ plot
        from scipy import stats as scipy_stats
        qq_data = scipy_stats.probplot(clean_data[metric], dist="norm")
        fig.add_trace(
            go.Scatter(x=qq_data[0][0], y=qq_data[0][1], 
                      mode='markers', name='QQ Plot'),
            row=2, col=2
        )
        
        fig.update_layout(
            title=f'{metric.replace("_", " ").title()} Distribution Analysis',
            showlegend=False,
            height=600,
            font=dict(family="Arial", size=12, color='#E1E1E1'),
            plot_bgcolor='#1E1E1E',
            paper_bgcolor='#1E1E1E'
        )
        
        return fig
    
    def create_sensor_map(self, include_data_points: bool = False) -> folium.Map:
        """
        Create interactive map with sensor location
        
        Args:
            include_data_points (bool): Whether to include data points on map
            
        Returns:
            Folium map object
        """
        # Get sensor location
        if 'latitude' in self.data.columns and 'longitude' in self.data.columns:
            # Use actual sensor coordinates from data
            lat = self.data['latitude'].iloc[0] if not self.data['latitude'].isna().all() else config.SENSOR_LOCATION['latitude']
            lon = self.data['longitude'].iloc[0] if not self.data['longitude'].isna().all() else config.SENSOR_LOCATION['longitude']
        else:
            # Use configured location
            lat = config.SENSOR_LOCATION['latitude']
            lon = config.SENSOR_LOCATION['longitude']
        
        # Create base map
        m = folium.Map(
            location=[lat, lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Add sensor marker
        folium.Marker(
            [lat, lon],
            popup=f"<b>{config.SENSOR_LOCATION['name']}</b><br>Purple Air Sensor",
            tooltip="Click for details",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
        
        # Add data points if requested and available
        if include_data_points and 'pm2_5_atm' in self.data.columns:
            self._add_data_points_to_map(m)
        
        return m
    
    def _add_data_points_to_map(self, map_obj: folium.Map):
        """Add air quality data points to map"""
        recent_data = self.data.dropna(subset=['pm2_5_atm']).tail(100)  # Last 100 points
        
        for _, row in recent_data.iterrows():
            # Get color based on AQI category
            color = self._get_aqi_color(row.get('pm2_5_atm', 0))
            
            # Add circle marker
            folium.CircleMarker(
                location=[row.get('latitude', config.SENSOR_LOCATION['latitude']),
                         row.get('longitude', config.SENSOR_LOCATION['longitude'])],
                radius=8,
                popup=f"PM2.5: {row.get('pm2_5_atm', 0):.1f} μg/m³<br>Time: {row.get('timestamp', '')}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(map_obj)
    
    def _get_aqi_color(self, pm25_value: float) -> str:
        """Get color based on PM2.5 value"""
        if pm25_value <= config.AQI_THRESHOLDS['good']:
            return 'green'
        elif pm25_value <= config.AQI_THRESHOLDS['moderate']:
            return 'yellow'
        elif pm25_value <= config.AQI_THRESHOLDS['unhealthy_sensitive']:
            return 'orange'
        elif pm25_value <= config.AQI_THRESHOLDS['unhealthy']:
            return 'red'
        elif pm25_value <= config.AQI_THRESHOLDS['very_unhealthy']:
            return 'purple'
        else:
            return 'darkred'
    
    def create_dashboard_summary(self) -> Dict[str, go.Figure]:
        """
        Create a comprehensive dashboard with multiple visualizations
        
        Returns:
            Dictionary of Plotly figures for dashboard
        """
        dashboard = {}
        
        # Time series plot
        if 'pm2_5_atm' in self.data.columns:
            dashboard['time_series'] = self.create_time_series_plot('pm2_5_atm')
        
        # Hourly patterns
        if 'pm2_5_atm' in self.data.columns:
            dashboard['hourly_heatmap'] = self.create_hourly_heatmap('pm2_5_atm')
        
        # Distribution analysis
        if 'pm2_5_atm' in self.data.columns:
            dashboard['distribution'] = self.create_distribution_plot('pm2_5_atm')
        
        # AQI pie chart
        if 'aqi_category' in self.data.columns:
            dashboard['aqi_distribution'] = self._create_aqi_pie_chart()
        
        return dashboard
    
    def _create_aqi_pie_chart(self) -> go.Figure:
        """Create AQI category distribution pie chart"""
        aqi_counts = self.data['aqi_category'].value_counts()
        
        colors_map = {
            'Good': '#00E400',
            'Moderate': '#FFFF00',
            'Unhealthy for Sensitive Groups': '#FF7E00',
            'Unhealthy': '#FF0000',
            'Very Unhealthy': '#8F3F97',
            'Hazardous': '#7E0023'
        }
        
        colors = [colors_map.get(cat, '#CCCCCC') for cat in aqi_counts.index]
        
        fig = go.Figure(data=[go.Pie(
            labels=aqi_counts.index,
            values=aqi_counts.values,
            marker_colors=colors,
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='Air Quality Index Distribution',
            font=dict(family="Arial", size=12, color='#E1E1E1'),
            plot_bgcolor='#1E1E1E',
            paper_bgcolor='#1E1E1E'
        )
        
        return fig
    
    def save_plot(self, fig: Union[go.Figure, plt.Figure], filename: str, format: str = 'html'):
        """
        Save plot to file
        
        Args:
            fig: Plotly or matplotlib figure
            filename (str): Output filename
            format (str): Output format ('html', 'png', 'pdf')
        """
        filepath = f"{config.CHARTS_DIR}/{filename}"
        
        if isinstance(fig, go.Figure):
            if format == 'html':
                fig.write_html(f"{filepath}.html")
            elif format == 'png':
                fig.write_image(f"{filepath}.png")
            elif format == 'pdf':
                fig.write_image(f"{filepath}.pdf")
        else:  # matplotlib figure
            if format == 'png':
                fig.savefig(f"{filepath}.png", dpi=300, bbox_inches='tight')
            elif format == 'pdf':
                fig.savefig(f"{filepath}.pdf", bbox_inches='tight')

# Utility functions
def quick_visualization(data: pd.DataFrame, metric: str = 'pm2_5_atm') -> go.Figure:
    """
    Quick function to create a time series visualization
    
    Args:
        data (pd.DataFrame): Sensor data
        metric (str): Column to plot
        
    Returns:
        Plotly figure
    """
    visualizer = PurpleAirVisualizer(data)
    return visualizer.create_time_series_plot(metric)

def create_sensor_dashboard(data: pd.DataFrame) -> Dict[str, go.Figure]:
    """
    Create complete dashboard for sensor data
    
    Args:
        data (pd.DataFrame): Sensor data
        
    Returns:
        Dictionary of dashboard figures
    """
    visualizer = PurpleAirVisualizer(data)
    return visualizer.create_dashboard_summary() 