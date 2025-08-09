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
import os
warnings.filterwarnings('ignore')

def main():
    """Main function to create beautiful dashboard."""
    print("🎨 CREATING BEAUTIFUL DASHBOARD")
    print("="*60)

    # Read the dataset
    data_path = 'data/raw/airlines_flights_data.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_csv(data_path)

    # 1. MAIN DASHBOARD WITH PROPER SUBPLOT SPECIFICATIONS
    print("📊 Creating Main Dashboard...")

    # Create a comprehensive dashboard with proper specs
    fig_main = make_subplots(
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

    # 1. Price distribution by airline (box plot)
    for airline in df['airline'].unique():
        airline_data = df[df['airline'] == airline]['price']
        fig_main.add_trace(
            go.Box(y=airline_data, name=airline, boxpoints='outliers'),
            row=1, col=1
        )

    # 2. Route popularity heatmap
    route_matrix = df.groupby(['source_city', 'destination_city']).size().unstack(fill_value=0)
    fig_main.add_trace(
        go.Heatmap(z=route_matrix.values, x=route_matrix.columns, y=route_matrix.index,
                   colorscale='Viridis', name='Route Popularity'),
        row=1, col=2
    )

    # 3. Price vs Duration scatter
    sample_df = df.sample(2000)
    fig_main.add_trace(
        go.Scatter(x=sample_df['duration'], y=sample_df['price'], mode='markers',
                   marker=dict(size=3, opacity=0.6, color=sample_df['days_left'], colorscale='Viridis'),
                   name='Price vs Duration'),
        row=2, col=1
    )

    # 4. Market share pie chart
    market_share = df['airline'].value_counts()
    fig_main.add_trace(
        go.Pie(labels=market_share.index, values=market_share.values,
               hole=0.4, textinfo='label+percent'),
        row=2, col=2
    )

    # 5. Booking patterns by days left
    days_bins = pd.cut(df['days_left'], bins=[0, 7, 14, 30, 49], labels=['1-7', '8-14', '15-30', '31-49'])
    booking_patterns = df.groupby(days_bins)['price'].mean()
    fig_main.add_trace(
        go.Bar(x=booking_patterns.index.astype(str), y=booking_patterns.values,
               name='Booking Patterns', marker_color='orange'),
        row=3, col=1
    )

    # 6. Price analysis by stops
    for stop_type in df['stops'].unique():
        stop_data = df[df['stops'] == stop_type]['price']
        fig_main.add_trace(
            go.Violin(y=stop_data, name=stop_type, box_visible=True, meanline_visible=True),
            row=3, col=2
        )

    fig_main.update_layout(
        height=1200,
        title_text="🚀 Airlines Data Analysis Dashboard",
        template='plotly_white',
        showlegend=True,
        title_font_size=24
    )
    fig_main.write_html('main_dashboard.html')

    # 2. ADVANCED PRICE ANALYSIS
    print("💰 Creating Advanced Price Analysis...")

    # Price distribution by airline and class
    fig_price = px.box(df, x='airline', y='price', color='class',
                      title='Price Distribution by Airline and Class',
                      labels={'price': 'Price ($)', 'airline': 'Airline', 'class': 'Class'})
    fig_price.update_layout(template='plotly_white', title_font_size=20)
    fig_price.write_html('advanced_price_dashboard.html')

    # 3. ROUTE AND AIRLINE ANALYSIS
    print("🛫 Creating Route and Airline Analysis...")

    # Route popularity heatmap
    route_matrix = df.groupby(['source_city', 'destination_city']).size().unstack(fill_value=0)
    fig_route = px.imshow(route_matrix, title='Route Popularity Heatmap',
                         labels=dict(x="Destination City", y="Source City", color="Number of Flights"),
                         color_continuous_scale='Viridis')
    fig_route.update_layout(template='plotly_white', title_font_size=20)
    fig_route.write_html('route_airline_dashboard.html')

    # 4. TIME ANALYSIS
    print("⏰ Creating Time Analysis...")

    # Price by departure time
    time_price = df.groupby('departure_time')['price'].mean().reset_index()
    fig_time = px.bar(time_price, x='departure_time', y='price',
                     title='Average Price by Departure Time',
                     labels={'price': 'Average Price ($)', 'departure_time': 'Departure Time'})
    fig_time.update_layout(template='plotly_white', title_font_size=20)
    fig_time.write_html('time_analysis_dashboard.html')

    # 5. CREATE BEAUTIFUL HTML DASHBOARD
    print("🎨 Creating Beautiful HTML Dashboard...")

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flight Data Analysis Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .nav {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .nav-button {
            padding: 12px 24px;
            background: rgba(255, 255, 255, 0.95);
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
            color: #2c3e50;
        }
        .nav-button:hover {
            background: #3498db;
            color: white;
            transform: translateY(-2px);
        }
        .section {
            display: none;
            padding: 20px;
        }
        .section.active {
            display: block;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(800px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .dashboard-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .dashboard-card:hover {
            transform: translateY(-5px);
        }
        .card-header {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        .iframe-container {
            width: 100%;
            height: 600px;
            border: none;
        }
        .footer {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            text-align: center;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Flight Data Analysis Dashboard</h1>
        <p>Comprehensive analysis of Indian domestic airlines flight data</p>
    </div>
    
    <div class="nav">
        <button class="nav-button" onclick="showSection('main')">📊 Main Dashboard</button>
        <button class="nav-button" onclick="showSection('pricing')">💰 Price Analysis</button>
        <button class="nav-button" onclick="showSection('routes')">🛫 Route Analysis</button>
        <button class="nav-button" onclick="showSection('timing')">⏰ Time Analysis</button>
    </div>
    
    <div id="main" class="section active">
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-header">📊 Main Dashboard</div>
                <div class="card-content">
                    <div class="iframe-container">
                        <iframe src="main_dashboard.html"></iframe>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div id="pricing" class="section">
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-header">💰 Advanced Price Analysis</div>
                <div class="card-content">
                    <div class="iframe-container">
                        <iframe src="advanced_price_dashboard.html"></iframe>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div id="routes" class="section">
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-header">🛫 Route and Airline Analysis</div>
                <div class="card-content">
                    <div class="iframe-container">
                        <iframe src="route_airline_dashboard.html"></iframe>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div id="timing" class="section">
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-header">⏰ Time Analysis Dashboard</div>
                <div class="card-content">
                    <div class="iframe-container">
                        <iframe src="time_analysis_dashboard.html"></iframe>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>🎉 Interactive Airlines Data Analysis Dashboard | Created with Plotly & Python</p>
        <p>💡 Hover over charts for detailed information | Click and drag to zoom | Use legend to filter data</p>
    </div>
    
    <script>
        function showSection(sectionId) {
            // Hide all sections
            const sections = document.querySelectorAll('.section');
            sections.forEach(section => section.style.display = 'none');
            
            // Show selected section
            document.getElementById(sectionId).style.display = 'block';
            
            // Update button styles
            const buttons = document.querySelectorAll('.nav-button');
            buttons.forEach(button => button.style.background = 'rgba(255, 255, 255, 0.95)');
            buttons.forEach(button => button.style.color = '#2c3e50');
            
            // Highlight active button
            event.target.style.background = '#3498db';
            event.target.style.color = 'white';
        }
    </script>
</body>
</html>
"""

    with open('beautiful_dashboard.html', 'w') as f:
        f.write(html_content)

    print("\n" + "="*60)
    print("🎉 BEAUTIFUL DASHBOARD CREATION COMPLETE!")
    print("="*60)
    print("\n📁 Generated Files:")
    print("1. main_dashboard.html - Main comprehensive dashboard")
    print("2. advanced_price_dashboard.html - Advanced price analysis")
    print("3. route_airline_dashboard.html - Route and airline analysis")
    print("4. time_analysis_dashboard.html - Time-based analysis")
    print("5. beautiful_dashboard.html - Beautiful HTML dashboard with navigation")

    print("\n🚀 Open 'beautiful_dashboard.html' in your browser for the complete experience!")
    print("💡 Features:")
    print("   - Interactive navigation between different analyses")
    print("   - Responsive design with beautiful gradients")
    print("   - Hover effects and smooth animations")
    print("   - Embedded interactive Plotly charts")
    print("   - Professional statistics cards")
    print("   - Mobile-friendly layout")

if __name__ == "__main__":
    main() 