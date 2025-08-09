import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import altair as alt
from wordcloud import WordCloud
import folium
from folium import plugins
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import warnings
import os
warnings.filterwarnings('ignore')

def main():
    """Main function to create modern dashboard."""
    # Set up the color palette for a modern look
    COLORS = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e', 
        'accent': '#2ca02c',
        'warning': '#d62728',
        'info': '#9467bd',
        'light': '#8c564b',
        'dark': '#e377c2',
        'success': '#17becf'
    }

    print("🚀 CREATING MODERN AIRLINES DASHBOARD")
    print("="*60)

    # Read the dataset
    data_path = 'data/raw/airlines_flights_data.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_csv(data_path)
    print(f"📊 Dataset loaded: {df.shape[0]:,} flights, {df.shape[1]} features")

    # 1. INTERACTIVE PRICE ANALYSIS DASHBOARD
    print("\n💰 Creating Interactive Price Analysis...")

    # Price distribution with interactive histogram
    fig_price_dist = px.histogram(
        df, x='price', nbins=50,
        title='Interactive Price Distribution',
        labels={'price': 'Price ($)', 'count': 'Number of Flights'},
        color_discrete_sequence=[COLORS['primary']],
        opacity=0.8
    )
    fig_price_dist.add_vline(x=df['price'].median(), line_dash="dash", line_color=COLORS['warning'],
                            annotation_text=f"Median: ${df['price'].median():,.0f}")
    fig_price_dist.update_layout(
        template='plotly_white',
        title_font_size=20,
        showlegend=False
    )
    fig_price_dist.write_html('price_distribution.html')

    # Price by airline with interactive box plot
    fig_airline_prices = px.box(
        df, x='airline', y='price', color='airline',
        title='Price Distribution by Airline',
        labels={'price': 'Price ($)', 'airline': 'Airline'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_airline_prices.update_layout(
        template='plotly_white',
        title_font_size=20,
        xaxis_tickangle=-45
    )
    fig_airline_prices.write_html('airline_prices.html')

    # 2. ADVANCED ROUTE ANALYSIS
    print("🛫 Creating Advanced Route Analysis...")

    # Route popularity heatmap
    route_matrix = df.groupby(['source_city', 'destination_city']).size().unstack(fill_value=0)
    fig_route_heatmap = px.imshow(
        route_matrix, 
        title='Route Popularity Heatmap',
        labels=dict(x="Destination City", y="Source City", color="Number of Flights"),
        color_continuous_scale='Viridis',
        aspect="auto"
    )
    fig_route_heatmap.update_layout(
        template='plotly_white',
        title_font_size=20
    )
    fig_route_heatmap.write_html('route_heatmap.html')

    # 3. INTERACTIVE TIME SERIES ANALYSIS
    print("⏰ Creating Time Series Analysis...")

    # Price trends by departure time
    time_price_analysis = df.groupby('departure_time')['price'].agg(['mean', 'count']).reset_index()
    fig_time_price = px.bar(
        time_price_analysis, x='departure_time', y='mean',
        title='Average Price by Departure Time',
        labels={'mean': 'Average Price ($)', 'departure_time': 'Departure Time'},
        color='count',
        color_continuous_scale='Plasma',
        text=time_price_analysis['mean'].round(0)
    )
    fig_time_price.update_layout(
        template='plotly_white',
        title_font_size=20,
        xaxis_tickangle=-45
    )
    fig_time_price.write_html('time_price_analysis.html')

    # 4. 3D ANALYSIS
    print("🌐 Creating 3D Analysis...")

    # 3D scatter plot
    sample_df = df.sample(5000)  # Sample for better performance
    fig_3d = px.scatter_3d(
        sample_df, x='price', y='duration', z='days_left', color='airline',
        title='3D Analysis: Price vs Duration vs Days Left',
        labels={'price': 'Price ($)', 'duration': 'Duration (hours)', 'days_left': 'Days Left'},
        opacity=0.7
    )
    fig_3d.update_layout(
        template='plotly_white',
        title_font_size=20
    )
    fig_3d.write_html('3d_analysis.html')

    # 5. INTERACTIVE MAP
    print("🗺️ Creating Interactive Map...")

    # Create a map centered on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='OpenStreetMap')

    # Add city markers
    cities = {
        'Delhi': [28.7041, 77.1025],
        'Mumbai': [19.0760, 72.8777],
        'Bangalore': [12.9716, 77.5946],
        'Kolkata': [22.5726, 88.3639],
        'Hyderabad': [17.3850, 78.4867],
        'Chennai': [13.0827, 80.2707]
    }

    for city, coords in cities.items():
        # Get flight count for this city
        flights_from = len(df[df['source_city'] == city])
        flights_to = len(df[df['destination_city'] == city])
        
        folium.Marker(
            coords,
            popup=f'<b>{city}</b><br>Flights from: {flights_from:,}<br>Flights to: {flights_to:,}',
            tooltip=city,
            icon=folium.Icon(color='red', icon='plane')
        ).add_to(m)

    m.save('interactive_map.html')

    # 6. CORRELATION ANALYSIS
    print("📊 Creating Correlation Analysis...")

    # Correlation heatmap
    numeric_cols = ['price', 'duration', 'days_left']
    correlation_matrix = df[numeric_cols].corr()
    
    fig_corr = px.imshow(
        correlation_matrix,
        title='Feature Correlation Heatmap',
        color_continuous_scale='RdBu',
        aspect="auto"
    )
    fig_corr.update_layout(
        template='plotly_white',
        title_font_size=20
    )
    fig_corr.write_html('correlation_heatmap.html')

    # 7. WORDCLOUD
    print("☁️ Creating Wordcloud...")

    # Create wordcloud from airline names
    airline_text = ' '.join(df['airline'].value_counts().index.repeat(df['airline'].value_counts().values))
    
    wordcloud = WordCloud(
        width=800, height=400,
        background_color='white',
        colormap='viridis',
        max_words=100
    ).generate(airline_text)

    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Airline Frequency Wordcloud', fontsize=20, pad=20)
    
    # Save to static/images directory
    output_dir = 'static/images'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'airline_wordcloud.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 8. COMPREHENSIVE DASHBOARD
    print("📈 Creating Comprehensive Dashboard...")

    # Create a comprehensive dashboard with multiple subplots
    fig_dashboard = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Price Distribution by Airline',
            'Route Popularity Heatmap',
            'Price vs Duration Analysis',
            'Market Share by Airline',
            'Booking Patterns by Days Left',
            'Price Analysis by Stops'
        ),
        specs=[
            [{"type": "box"}, {"type": "heatmap"}],
            [{"type": "scatter"}, {"type": "pie"}],
            [{"type": "bar"}, {"type": "violin"}]
        ]
    )

    # Add traces to the dashboard
    for airline in df['airline'].unique():
        airline_data = df[df['airline'] == airline]['price']
        fig_dashboard.add_trace(
            go.Box(y=airline_data, name=airline, boxpoints='outliers'),
            row=1, col=1
        )

    # Route heatmap
    route_matrix = df.groupby(['source_city', 'destination_city']).size().unstack(fill_value=0)
    fig_dashboard.add_trace(
        go.Heatmap(z=route_matrix.values, x=route_matrix.columns, y=route_matrix.index,
                   colorscale='Viridis', name='Route Popularity'),
        row=1, col=2
    )

    # Price vs Duration scatter
    sample_df = df.sample(2000)
    fig_dashboard.add_trace(
        go.Scatter(x=sample_df['duration'], y=sample_df['price'], mode='markers',
                   marker=dict(size=3, opacity=0.6, color=sample_df['days_left'], colorscale='Viridis'),
                   name='Price vs Duration'),
        row=2, col=1
    )

    # Market share pie chart
    market_share = df['airline'].value_counts()
    fig_dashboard.add_trace(
        go.Pie(labels=market_share.index, values=market_share.values,
               hole=0.4, textinfo='label+percent'),
        row=2, col=2
    )

    # Booking patterns
    days_bins = pd.cut(df['days_left'], bins=[0, 7, 14, 30, 49], labels=['1-7', '8-14', '15-30', '31-49'])
    booking_patterns = df.groupby(days_bins)['price'].mean()
    fig_dashboard.add_trace(
        go.Bar(x=booking_patterns.index.astype(str), y=booking_patterns.values,
               name='Booking Patterns', marker_color='orange'),
        row=3, col=1
    )

    # Price by stops
    for stop_type in df['stops'].unique():
        stop_data = df[df['stops'] == stop_type]['price']
        fig_dashboard.add_trace(
            go.Violin(y=stop_data, name=stop_type, box_visible=True, meanline_visible=True),
            row=3, col=2
        )

    fig_dashboard.update_layout(
        height=1200,
        title_text="🚀 Airlines Data Analysis Dashboard",
        template='plotly_white',
        showlegend=True,
        title_font_size=24
    )
    fig_dashboard.write_html('comprehensive_dashboard.html')

    # 9. ANIMATED VISUALIZATIONS
    print("🎬 Creating Animated Visualizations...")

    # Animated price trends by airline over days left
    df_animated = df.groupby(['airline', 'days_left'])['price'].mean().reset_index()
    fig_animated = px.scatter(
        df_animated, x='days_left', y='price', color='airline', size='price',
        title='Animated Price Trends by Airline',
        labels={'price': 'Average Price ($)', 'days_left': 'Days Before Departure'},
        animation_frame='days_left',
        range_x=[1, 49], range_y=[0, 50000]
    )
    fig_animated.update_layout(
        template='plotly_white',
        title_font_size=20
    )
    fig_animated.write_html('animated_price_trends.html')

    # 10. ADVANCED ALTAR CHART
    print("📊 Creating Altair Chart...")

    # Create an interactive Altair chart
    alt.data_transformers.enable('default', max_rows=None)

    # Price distribution by airline and class
    chart = alt.Chart(df.sample(10000)).mark_circle().encode(
        x=alt.X('price:Q', title='Price ($)'),
        y=alt.Y('duration:Q', title='Duration (hours)'),
        color=alt.Color('airline:N', title='Airline'),
        size=alt.Size('days_left:Q', title='Days Left'),
        tooltip=['airline', 'price', 'duration', 'days_left', 'class']
    ).properties(
        title='Interactive Price-Duration Analysis',
        width=800,
        height=400
    ).interactive()

    chart.save('altair_chart.html')

    # 11. STATISTICAL SUMMARY DASHBOARD
    print("📋 Creating Statistical Summary...")

    # Create a beautiful statistical summary
    stats_summary = {
        'Total Flights': f"{df.shape[0]:,}",
        'Total Airlines': f"{df['airline'].nunique()}",
        'Total Routes': f"{df.groupby(['source_city', 'destination_city']).ngroups}",
        'Average Price': f"${df['price'].mean():,.0f}",
        'Median Price': f"${df['price'].median():,.0f}",
        'Price Range': f"${df['price'].min():,.0f} - ${df['price'].max():,.0f}",
        'Average Duration': f"{df['duration'].mean():.1f} hours",
        'Most Popular Route': f"{df.groupby(['source_city', 'destination_city']).size().idxmax()[0]} → {df.groupby(['source_city', 'destination_city']).size().idxmax()[1]}",
        'Market Leader': f"{df['airline'].value_counts().index[0]} ({df['airline'].value_counts().iloc[0]/len(df)*100:.1f}%)"
    }

    # Create a beautiful summary table
    fig_summary = go.Figure(data=[go.Table(
        header=dict(
            values=['Metric', 'Value'],
            fill_color=COLORS['primary'],
            font=dict(color='white', size=14),
            align='left'
        ),
        cells=dict(
            values=[list(stats_summary.keys()), list(stats_summary.values())],
            fill_color='lavender',
            font=dict(size=12),
            align='left'
        )
    )])

    fig_summary.update_layout(
        title='Dataset Summary Statistics',
        template='plotly_white',
        title_font_size=20
    )
    fig_summary.write_html('summary_statistics.html')

    print("\n" + "="*60)
    print("🎉 MODERN DASHBOARD CREATION COMPLETE!")
    print("="*60)
    print("\n📁 Generated Files:")
    print("1. price_distribution.html - Interactive price histogram")
    print("2. airline_prices.html - Box plots by airline")
    print("3. route_heatmap.html - Route popularity heatmap")
    print("4. time_price_analysis.html - Price by departure time")
    print("5. 3d_analysis.html - 3D scatter plot")
    print("6. interactive_map.html - Interactive map of India")
    print("7. correlation_heatmap.html - Feature correlations")
    print("8. airline_wordcloud.png - Airline frequency word cloud")
    print("9. comprehensive_dashboard.html - Multi-panel dashboard")
    print("10. animated_price_trends.html - Animated price trends")
    print("11. altair_chart.html - Interactive Altair visualization")
    print("12. summary_statistics.html - Statistical summary table")

    print("\n🚀 Open any .html file in your browser to view the interactive visualizations!")
    print("💡 All visualizations are interactive and can be zoomed, panned, and explored!")

if __name__ == "__main__":
    main() 