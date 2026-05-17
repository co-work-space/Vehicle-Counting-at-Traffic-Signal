import plotly.express as px
import pandas as pd

def create_type_distribution_chart(type_counts):
    """Creates a pie chart for vehicle types."""
    if not type_counts or sum(type_counts.values()) == 0:
        return None
    
    df = pd.DataFrame(list(type_counts.items()), columns=['Vehicle Type', 'Count'])
    fig = px.pie(df, values='Count', names='Vehicle Type', title="Vehicle Type Distribution")
    return fig

def create_time_series_plot(history_data):
    """Creates a line chart showing traffic over time."""
    if not history_data:
        return None
        
    df = pd.DataFrame(history_data)
    # Group by minute for a cleaner chart
    df['minute'] = df['timestamp'].dt.floor('Min')
    counts_per_min = df.groupby('minute').size().reset_index(name='count')
    
    fig = px.line(counts_per_min, x='minute', y='count', title="Traffic Volume Over Time")
    return fig