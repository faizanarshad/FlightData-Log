import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("🎨 CREATING ADVANCED VISUALIZATIONS")
print("="*60)

# Read the dataset
df = pd.read_csv('airlines_flights_data.csv')

# 1. ADVANCED PRICE ANALYSIS WITH DISTRIBUTION FITTING
print("📊 Creating Advanced Price Analysis...")

# Create a sophisticated price analysis with multiple distributions
fig_price_advanced = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Price Distribution with Normal Fit',
        'Price by Airline (Violin Plot)',
        'Price vs Duration (Hexbin)',
        'Price Percentiles by Class'
    ),
    specs=[[{"secondary_y": True}, {"type": "violin"}],
           [{"type": "scatter"}, {"type": "box"}]]
)

# Price distribution with normal fit
price_data = df['price']
mu, sigma = stats.norm.fit(price_data)
x = np.linspace(price_data.min(), price_data.max(), 100)
y = stats.norm.pdf(x, mu, sigma)

fig_price_advanced.add_trace(
    go.Histogram(x=price_data, nbinsx=50, name='Actual', opacity=0.7, marker_color='lightblue'),
    row=1, col=1
)
fig_price_advanced.add_trace(
    go.Scatter(x=x, y=y*len(price_data)*50, name='Normal Fit', line=dict(color='red')),
    row=1, col=1, secondary_y=True
)

# Violin plot by airline
for airline in df['airline'].unique():
    airline_data = df[df['airline'] == airline]['price']
    fig_price_advanced.add_trace(
        go.Violin(y=airline_data, name=airline, box_visible=True, meanline_visible=True),
        row=1, col=2
    )

# Hexbin scatter plot
fig_price_advanced.add_trace(
    go.Scatter(
        x=df['duration'], y=df['price'], mode='markers',
        marker=dict(size=3, opacity=0.3, color=df['days_left'], colorscale='Viridis'),
        name='Price vs Duration'
    ),
    row=2, col=1
)

# Price percentiles by class
for travel_class in df['class'].unique():
    class_data = df[df['class'] == travel_class]['price']
    fig_price_advanced.add_trace(
        go.Box(y=class_data, name=travel_class, boxpoints='outliers'),
        row=2, col=2
    )

fig_price_advanced.update_layout(
    height=800,
    title_text="Advanced Price Analysis Dashboard",
    template='plotly_white',
    showlegend=True
)
fig_price_advanced.write_html('advanced_price_analysis.html')

# 2. TIME SERIES AND TREND ANALYSIS
print("⏰ Creating Time Series Analysis...")

# Create time-based analysis
fig_time_advanced = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Price Trends by Days Left',
        'Departure Time Preferences',
        'Duration vs Days Left',
        'Price Volatility by Route'
    )
)

# Price trends by days left
days_price = df.groupby('days_left')['price'].agg(['mean', 'std', 'count']).reset_index()
fig_time_advanced.add_trace(
    go.Scatter(x=days_price['days_left'], y=days_price['mean'], 
               mode='lines+markers', name='Average Price',
               line=dict(color='blue', width=3)),
    row=1, col=1
)
fig_time_advanced.add_trace(
    go.Scatter(x=days_price['days_left'], y=days_price['mean'] + days_price['std'],
               mode='lines', name='+1 Std Dev', line=dict(color='lightblue', dash='dash')),
    row=1, col=1
)
fig_time_advanced.add_trace(
    go.Scatter(x=days_price['days_left'], y=days_price['mean'] - days_price['std'],
               mode='lines', name='-1 Std Dev', line=dict(color='lightblue', dash='dash'),
               fill='tonexty'),
    row=1, col=1
)

# Departure time preferences with price
time_analysis = df.groupby('departure_time').agg({
    'price': ['mean', 'count'],
    'duration': 'mean'
}).reset_index()
time_analysis.columns = ['departure_time', 'avg_price', 'count', 'avg_duration']

fig_time_advanced.add_trace(
    go.Bar(x=time_analysis['departure_time'], y=time_analysis['count'],
           name='Flight Count', marker_color='orange'),
    row=1, col=2
)

# Duration vs days left
fig_time_advanced.add_trace(
    go.Scatter(x=df['days_left'], y=df['duration'], mode='markers',
               marker=dict(size=2, opacity=0.5, color=df['price'], colorscale='Viridis'),
               name='Duration vs Days'),
    row=2, col=1
)

# Price volatility by route
route_volatility = df.groupby(['source_city', 'destination_city'])['price'].std().sort_values(ascending=False).head(10)
fig_time_advanced.add_trace(
    go.Bar(x=[f"{route[0]}→{route[1]}" for route in route_volatility.index], 
           y=route_volatility.values, name='Price Volatility'),
    row=2, col=2
)

fig_time_advanced.update_layout(
    height=800,
    title_text="Time Series and Trend Analysis",
    template='plotly_white'
)
fig_time_advanced.write_html('time_series_analysis.html')

# 3. ADVANCED STATISTICAL ANALYSIS
print("📈 Creating Advanced Statistical Analysis...")

# Create statistical analysis dashboard
fig_stats = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Correlation Matrix Heatmap',
        'Price Distribution by Stops',
        'Market Share Analysis',
        'Revenue Analysis by Airline'
    )
)

# Correlation matrix
numeric_cols = ['price', 'duration', 'days_left']
corr_matrix = df[numeric_cols].corr()
fig_stats.add_trace(
    go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.columns,
               colorscale='RdBu', zmid=0),
    row=1, col=1
)

# Price by stops
for stop_type in df['stops'].unique():
    stop_data = df[df['stops'] == stop_type]['price']
    fig_stats.add_trace(
        go.Box(y=stop_data, name=stop_type, boxpoints='outliers'),
        row=1, col=2
    )

# Market share pie chart
market_share = df['airline'].value_counts()
fig_stats.add_trace(
    go.Pie(labels=market_share.index, values=market_share.values,
           hole=0.4, textinfo='label+percent'),
    row=2, col=1
)

# Revenue analysis
revenue_by_airline = df.groupby('airline').agg({
    'price': ['sum', 'mean', 'count']
}).round(0)
revenue_by_airline.columns = ['total_revenue', 'avg_price', 'flight_count']

fig_stats.add_trace(
    go.Bar(x=revenue_by_airline.index, y=revenue_by_airline['total_revenue'],
           name='Total Revenue', marker_color='green'),
    row=2, col=2
)

fig_stats.update_layout(
    height=800,
    title_text="Advanced Statistical Analysis",
    template='plotly_white'
)
fig_stats.write_html('statistical_analysis.html')

# 4. INTERACTIVE FILTERING DASHBOARD
print("🔍 Creating Interactive Filtering Dashboard...")

# Create an interactive dashboard with filters
fig_interactive = go.Figure()

# Add multiple traces for different airlines
for airline in df['airline'].unique():
    airline_data = df[df['airline'] == airline]
    fig_interactive.add_trace(
        go.Scatter(
            x=airline_data['duration'],
            y=airline_data['price'],
            mode='markers',
            name=airline,
            marker=dict(size=5, opacity=0.6),
            hovertemplate=f'<b>{airline}</b><br>' +
                         'Duration: %{x:.1f} hours<br>' +
                         'Price: $%{y:,.0f}<br>' +
                         '<extra></extra>'
        )
    )

fig_interactive.update_layout(
    title='Interactive Flight Analysis - Click legend to filter',
    xaxis_title='Duration (hours)',
    yaxis_title='Price ($)',
    template='plotly_white',
    height=600
)
fig_interactive.write_html('interactive_filtering.html')

# 5. ADVANCED ANIMATION
print("🎬 Creating Advanced Animation...")

# Create animated bubble chart
fig_animated = px.scatter(
    df.sample(5000),
    x='price',
    y='duration',
    size='days_left',
    color='airline',
    hover_name='flight',
    animation_frame='stops',
    title='Animated Flight Analysis by Stops',
    labels={'price': 'Price ($)', 'duration': 'Duration (hours)', 'days_left': 'Days Left'},
    size_max=20
)
fig_animated.update_layout(
    template='plotly_white',
    title_font_size=20
)
fig_animated.write_html('animated_bubble_chart.html')

# 6. ADVANCED HEATMAPS
print("🔥 Creating Advanced Heatmaps...")

# Create multiple heatmaps
fig_heatmaps = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Price Heatmap by Route',
        'Duration Heatmap by Route',
        'Flight Count Heatmap by Route',
        'Days Left Heatmap by Route'
    )
)

# Price heatmap
price_pivot = df.pivot_table(values='price', index='source_city', columns='destination_city', aggfunc='mean')
fig_heatmaps.add_trace(
    go.Heatmap(z=price_pivot.values, x=price_pivot.columns, y=price_pivot.index,
               colorscale='Viridis', name='Price'),
    row=1, col=1
)

# Duration heatmap
duration_pivot = df.pivot_table(values='duration', index='source_city', columns='destination_city', aggfunc='mean')
fig_heatmaps.add_trace(
    go.Heatmap(z=duration_pivot.values, x=duration_pivot.columns, y=duration_pivot.index,
               colorscale='Plasma', name='Duration'),
    row=1, col=2
)

# Flight count heatmap
count_pivot = df.pivot_table(values='price', index='source_city', columns='destination_city', aggfunc='count')
fig_heatmaps.add_trace(
    go.Heatmap(z=count_pivot.values, x=count_pivot.columns, y=count_pivot.index,
               colorscale='Blues', name='Flight Count'),
    row=2, col=1
)

# Days left heatmap
days_pivot = df.pivot_table(values='days_left', index='source_city', columns='destination_city', aggfunc='mean')
fig_heatmaps.add_trace(
    go.Heatmap(z=days_pivot.values, x=days_pivot.columns, y=days_pivot.index,
               colorscale='Reds', name='Days Left'),
    row=2, col=2
)

fig_heatmaps.update_layout(
    height=800,
    title_text="Advanced Route Analysis Heatmaps",
    template='plotly_white'
)
fig_heatmaps.write_html('advanced_heatmaps.html')

print("\n" + "="*60)
print("🎉 ADVANCED VISUALIZATIONS COMPLETE!")
print("="*60)
print("\n📁 Additional Generated Files:")
print("1. advanced_price_analysis.html - Sophisticated price analysis")
print("2. time_series_analysis.html - Time-based trends")
print("3. statistical_analysis.html - Statistical insights")
print("4. interactive_filtering.html - Interactive filtering")
print("5. animated_bubble_chart.html - Animated bubble chart")
print("6. advanced_heatmaps.html - Multiple heatmap analysis")

print("\n🚀 All visualizations are ready! Open any .html file in your browser!")
print("💡 These visualizations include advanced statistical analysis, animations, and interactive features!") 