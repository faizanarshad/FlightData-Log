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
import json
import plotly.io as pio
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

from src.data_paths import resolve_data_path

def create_ml_models(df):
    """Create and train ML models for price prediction and demand forecasting."""
    print("🤖 Training ML Models...")
    
    # Prepare data for ML
    df_ml = df.copy()
    
    # Encode categorical variables
    le_airline = LabelEncoder()
    le_source = LabelEncoder()
    le_dest = LabelEncoder()
    le_class = LabelEncoder()
    le_stops = LabelEncoder()
    le_dep_time = LabelEncoder()
    le_arr_time = LabelEncoder()
    
    df_ml['airline_encoded'] = le_airline.fit_transform(df_ml['airline'])
    df_ml['source_encoded'] = le_source.fit_transform(df_ml['source_city'])
    df_ml['dest_encoded'] = le_dest.fit_transform(df_ml['destination_city'])
    df_ml['class_encoded'] = le_class.fit_transform(df_ml['class'])
    df_ml['stops_encoded'] = le_stops.fit_transform(df_ml['stops'])
    df_ml['dep_time_encoded'] = le_dep_time.fit_transform(df_ml['departure_time'])
    df_ml['arr_time_encoded'] = le_arr_time.fit_transform(df_ml['arrival_time'])
    
    # Features for price prediction
    price_features = ['airline_encoded', 'source_encoded', 'dest_encoded', 'class_encoded', 
                     'stops_encoded', 'dep_time_encoded', 'arr_time_encoded', 'duration', 'days_left']
    
    X_price = df_ml[price_features]
    y_price = df_ml['price']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_price, y_price, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'Linear Regression': LinearRegression()
    }
    
    model_results = {}
    
    for name, model in models.items():
        if name == 'Linear Regression':
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        model_results[name] = {
            'model': model,
            'mae': mae,
            'mse': mse,
            'r2': r2,
            'predictions': y_pred,
            'actual': y_test
        }
    
    # Demand forecasting model (using days_left as proxy for demand)
    demand_features = ['airline_encoded', 'source_encoded', 'dest_encoded', 'class_encoded', 'duration']
    X_demand = df_ml[demand_features]
    y_demand = df_ml['days_left']
    
    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X_demand, y_demand, test_size=0.2, random_state=42)
    
    demand_model = RandomForestRegressor(n_estimators=100, random_state=42)
    demand_model.fit(X_train_d, y_train_d)
    demand_pred = demand_model.predict(X_test_d)
    
    demand_mae = mean_absolute_error(y_test_d, demand_pred)
    demand_r2 = r2_score(y_test_d, demand_pred)
    
    return model_results, demand_model, demand_mae, demand_r2, scaler, le_airline, le_source, le_dest, le_class, le_stops, le_dep_time, le_arr_time

def create_enhanced_visualizations(df, model_results, demand_model, demand_mae, demand_r2):
    """Create enhanced visualizations with better colors and layouts."""
    
    # Color schemes
    airline_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    route_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    time_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    # 1. Enhanced Main Dashboard with gradient colors
    print("📊 Creating Enhanced Main Dashboard...")
    fig_main = make_subplots(
        rows=5, cols=2,  # Expanded to 5 rows to accommodate new price analysis graphs
        subplot_titles=(
            '🔬 Advanced Price Distribution by Airline',
            '🚀 3D Price-Duration-Days Analysis',
            '⏱️ Price vs Duration + Days Left Analysis',
            '📊 Market Share by Airline',
            '🛑 Price Analysis by Stops',
            '🌍 Route Popularity Map',
            '💰 Price Distribution by Class',
            '📈 Price Trends by Departure Time',
            '🎯 Price vs Distance Analysis',
            '📊 Price Statistics by Airline'
        ),
        specs=[
            [{"type": "box"}, {"type": "scene"}],
            [{"type": "scatter"}, {"type": "pie"}],
            [{"type": "xy"}, {"type": "violin"}],
            [{"type": "violin"}, {"type": "scatter"}],  # New row for price analysis
            [{"type": "scatter"}, {"type": "bar"}]       # New row for price analysis
        ],
        vertical_spacing=0.08,  # Reduced spacing for more compact layout
        horizontal_spacing=0.08
    )

    # Advanced Price Distribution by Airline with Violin + Box + Density
    for i, airline in enumerate(df['airline'].unique()):
        airline_data = df[df['airline'] == airline]['price']
        
        # Add Violin plot for distribution shape
        fig_main.add_trace(
            go.Violin(
                y=airline_data,
                name=f"{airline} (Violin)",
                box_visible=True,
                meanline_visible=True,
                line_color=airline_colors[i % len(airline_colors)],
                fillcolor=airline_colors[i % len(airline_colors)],
                opacity=0.6,
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add Box plot for quartiles and outliers
        fig_main.add_trace(
            go.Box(
                y=airline_data,
                name=f"{airline} (Box)",
                boxpoints='outliers',
                marker_color=airline_colors[i % len(airline_colors)],
                line_color=airline_colors[i % len(airline_colors)],
                fillcolor='rgba(255, 255, 255, 0.1)',
                opacity=0.8,
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add Scatter plot for individual data points (sampled for performance)
        sample_data = airline_data.sample(min(100, len(airline_data)))
        fig_main.add_trace(
            go.Scatter(
                x=[airline] * len(sample_data),
                y=sample_data,
                mode='markers',
                name=f"{airline} (Points)",
                marker=dict(
                    color=airline_colors[i % len(airline_colors)],
                    size=4,
                    opacity=0.4,
                    line=dict(width=1, color='white')
                ),
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add statistical summary annotations
        mean_price = airline_data.mean()
        median_price = airline_data.median()
        std_price = airline_data.std()
        
        # Position annotation above the violin plot with improved styling
        fig_main.add_annotation(
            x=airline,
            y=mean_price + std_price * 1.5,
            text=f"μ: ${mean_price:.0f}<br>σ: ${std_price:.0f}<br>N: {len(airline_data)}",
            showarrow=False,
            font=dict(size=10, color=airline_colors[i % len(airline_colors)], family="Arial, sans-serif"),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor=airline_colors[i % len(airline_colors)],
            borderwidth=2,
            row=1, col=1
        )

    # Advanced 3D Scatter Plot: Multi-Dimensional Airline Analysis
    # Sample data for better performance
    sample_3d = df.sample(5000)
    
    # Create 3D scatter plot with multiple dimensions and enhanced tooltips
    fig_main.add_trace(
        go.Scatter3d(
            x=sample_3d['duration'],
            y=sample_3d['days_left'],
            z=sample_3d['price'],
            mode='markers',
            marker=dict(
                size=sample_3d['price'] / 200 + 2,  # Size based on price
                color=sample_3d['airline'].astype('category').cat.codes,  # Color by airline
                colorscale='Viridis',
                opacity=0.8,
                showscale=True,
                colorbar=dict(
                    title="Airline Categories", 
                    titlefont=dict(size=14, family="Arial, sans-serif"),
                    tickfont=dict(size=12, family="Arial, sans-serif"),
                    x=1.15, 
                    thickness=20, 
                    len=0.8
                )
            ),
            text=sample_3d['airline'] + '<br>Class: ' + sample_3d['class'],
            hovertemplate='<b>%{text}</b><br><br>⏱️ Duration: %{x:.1f} hours<br>📅 Days Left: %{y}<br>💰 Price: $%{z:.0f}<br><br><i>Click and drag to rotate view</i><extra></extra>',
            name='3D Price-Duration-Days Analysis'
        ),
        row=1, col=2
    )
    




    # Enhanced market share pie chart with improved tooltips
    market_share = df['airline'].value_counts()
    fig_main.add_trace(
        go.Pie(
            labels=market_share.index, 
            values=market_share.values,
            hole=0.4, 
            textinfo='label+percent',
            marker_colors=airline_colors[:len(market_share)],
            textfont_size=14,
            hovertemplate='<b>✈️ %{label}</b><br><br>📊 Market Share: %{percent:.1%}<br>✈️ Total Flights: %{value}<br>💰 Avg Price: $%{customdata:.0f}<br><br><i>Click to highlight airline</i><extra></extra>',
            customdata=df.groupby('airline')['price'].mean().reindex(market_share.index)
        ),
        row=2, col=2
    )

    # Enhanced price vs duration with days left integration
    sample_df = df.sample(3000)
    
    # Create enhanced scatter plot with days left as color and size
    fig_main.add_trace(
        go.Scatter(
            x=sample_df['duration'], 
            y=sample_df['price'],
            mode='markers',
            marker=dict(
                size=sample_df['days_left'] / 5 + 3,  # Size based on days left
                color=sample_df['days_left'],
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(
                    title="Days Left",
                    titlefont=dict(size=14, family="Arial, sans-serif"),
                    tickfont=dict(size=12, family="Arial, sans-serif"),
                    x=1.15,
                    thickness=20,
                    len=0.8
                ),
                opacity=0.7
            ),
            text=sample_df['airline'] + '<br>Days Left: ' + sample_df['days_left'].astype(str),
            hovertemplate='<b>✈️ %{text}</b><br><br>⏱️ Duration: %{x:.1f} hours<br>💰 Price: $%{y:.0f}<br>📅 Days Left: %{marker.size}<br><br><i>Size indicates days until departure</i><extra></extra>',
            name='Price vs Duration + Days Left'
        ),
        row=2, col=1
    )
    
    # Add trend line for price vs duration
    z = np.polyfit(sample_df['duration'], sample_df['price'], 1)
    p = np.poly1d(z)
    fig_main.add_trace(
        go.Scatter(
            x=sample_df['duration'],
            y=p(sample_df['duration']),
            mode='lines',
            line=dict(color='#FF6B6B', width=3, dash='dash'),
            name='Trend Line',
            showlegend=False
        ),
        row=2, col=1
    )

    # Enhanced price by stops with custom colors
    for i, stop_type in enumerate(df['stops'].unique()):
        stop_data = df[df['stops'] == stop_type]['price']
        fig_main.add_trace(
            go.Violin(
                y=stop_data, 
                name=stop_type, 
                box_visible=True, 
                meanline_visible=True,
                line_color=route_colors[i % len(route_colors)],
                fillcolor=route_colors[i % len(route_colors)],
                opacity=0.7
            ),
                    row=3, col=2
    )
    
    # Route Popularity Analysis (Row 3, Col 1) with enhanced styling
    route_popularity = df.groupby(['source_city', 'destination_city']).size().reset_index(name='count')
    route_popularity = route_popularity.sort_values('count', ascending=False).head(15)
    
    fig_main.add_trace(
        go.Bar(
            x=route_popularity['source_city'] + ' → ' + route_popularity['destination_city'],
            y=route_popularity['count'],
            name='Route Popularity',
            marker_color='#4ECDC4',
            marker_line_color='#26A69A',
            marker_line_width=2,
            customdata=route_popularity['count'] / route_popularity['count'].sum() * 100,  # For percentage calculation
            hovertemplate='<b>🌍 Route: %{x}</b><br><br>✈️ Total Flights: %{y}<br>📊 Market Share: %{customdata:.1f}%<br><br><i>Most popular routes in the dataset</i><extra></extra>'
        ),
        row=3, col=1
    )
    
    # Enhanced layout with improved typography, spacing, and positioning
    fig_main.update_layout(
        height=1400,  # Reduced height for more compact layout
        title_text="🚀 Enhanced Airlines Data Analysis Dashboard",
        template='plotly_white',
        showlegend=True,
        title_font_size=24,  # Slightly smaller title
        title_font_color='#1a1a1a',  # Darker title for better contrast
        font=dict(
            size=12,  # Reduced base font size for compactness
            family="Arial, sans-serif"  # Professional font family
        ),
        paper_bgcolor='rgba(248, 249, 250, 0.95)',  # Light gray background
        plot_bgcolor='rgba(255, 255, 255, 0.9)',  # Semi-transparent white
        margin=dict(
            t=80,   # Reduced top margin
            b=40,   # Reduced bottom margin
            l=40,   # Reduced left margin
            r=40    # Reduced right margin
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),  # Smaller legend font
            bgcolor='rgba(255, 255, 255, 0.8)',  # Semi-transparent background
            bordercolor='rgba(0, 0, 0, 0.1)',    # Subtle border
            borderwidth=1
        ),
    )
    
    # Update axis styling for better readability
    fig_main.update_xaxes(
        title_font=dict(size=16, family="Arial, sans-serif"),
        tickfont=dict(size=12, family="Arial, sans-serif"),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0, 0, 0, 0.1)',
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='rgba(0, 0, 0, 0.2)'
    )
    
    fig_main.update_yaxes(
        title_font=dict(size=16, family="Arial, sans-serif"),
        tickfont=dict(size=12, family="Arial, sans-serif"),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0, 0, 0, 0.1)',
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='rgba(0, 0, 0, 0.2)'
    )
    
    # 4. NEW PRICE ANALYSIS GRAPHS - Row 4 & 5
    print("💰 Creating Additional Price Analysis Graphs...")
    
    # Row 4, Col 1: Price Distribution by Class (Violin Plot)
    for i, class_type in enumerate(df['class'].unique()):
        class_data = df[df['class'] == class_type]['price']
        fig_main.add_trace(
            go.Violin(
                y=class_data,
                name=f"{class_type}",
                box_visible=True,
                meanline_visible=True,
                line_color=airline_colors[i % len(airline_colors)],
                fillcolor=airline_colors[i % len(airline_colors)],
                opacity=0.7,
                showlegend=False
            ),
            row=4, col=1
        )
    
    # Row 4, Col 2: Price Trends by Departure Time (Scatter Plot)
    time_price_data = df.groupby('departure_time')['price'].agg(['mean', 'count']).reset_index()
    time_price_data = time_price_data[time_price_data['count'] > 10]  # Filter for meaningful data
    
    fig_main.add_trace(
        go.Scatter(
            x=time_price_data['departure_time'],
            y=time_price_data['mean'],
            mode='markers+lines',
            name='Average Price by Time',
            marker=dict(
                size=time_price_data['count'] / 50 + 5,  # Size based on flight count
                color=time_price_data['mean'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title="Price ($)",
                    titlefont=dict(size=14, family="Arial, sans-serif"),
                    tickfont=dict(size=12, family="Arial, sans-serif"),
                    x=1.15,
                    thickness=20,
                    len=0.8
                )
            ),
            line=dict(color='#FF6B6B', width=3),
            text=time_price_data['departure_time'] + '<br>Flights: ' + time_price_data['count'].astype(str),
            hovertemplate='<b>🕐 %{text}</b><br><br>💰 Average Price: $%{y:.0f}<br>✈️ Flight Count: %{marker.size}<br><br><i>Size indicates number of flights</i><extra></extra>'
        ),
        row=4, col=2
    )
    
    # Row 5, Col 1: Price vs Distance Analysis (Scatter Plot)
    # Create a simple distance proxy based on duration
    df['distance_proxy'] = df['duration'] * 800  # Rough km estimate
    
    sample_distance = df.sample(3000)
    fig_main.add_trace(
        go.Scatter(
            x=sample_distance['distance_proxy'],
            y=sample_distance['price'],
            mode='markers',
            name='Price vs Distance',
            marker=dict(
                size=sample_distance['days_left'] / 10 + 3,  # Size based on days left
                color=sample_distance['airline'].astype('category').cat.codes,
                colorscale='Plasma',
                opacity=0.7,
                showscale=True,
                colorbar=dict(
                    title="Airline",
                    titlefont=dict(size=14, family="Arial, sans-serif"),
                    tickfont=dict(size=12, family="Arial, sans-serif"),
                    x=1.15,
                    thickness=20,
                    len=0.8
                )
            ),
            text=sample_distance['airline'] + '<br>Class: ' + sample_distance['class'],
            hovertemplate='<b>✈️ %{text}</b><br><br>🌍 Distance: %{x:.0f} km<br>💰 Price: $%{y:.0f}<br>📅 Days Left: %{marker.size}<br><br><i>Size indicates days until departure</i><extra></extra>'
        ),
        row=5, col=1
    )
    
    # Row 5, Col 2: Price Statistics by Airline (Bar Chart)
    airline_price_stats = df.groupby('airline').agg({
        'price': ['mean', 'median', 'std', 'count']
    }).reset_index()
    airline_price_stats.columns = ['airline', 'avg_price', 'median_price', 'price_std', 'flight_count']
    airline_price_stats = airline_price_stats.sort_values('avg_price', ascending=False)
    
    fig_main.add_trace(
        go.Bar(
            x=airline_price_stats['airline'],
            y=airline_price_stats['avg_price'],
            name='Average Price by Airline',
            marker_color='#4ECDC4',
            marker_line_color='#26A69A',
            marker_line_width=2,
            text=airline_price_stats['avg_price'].round(0),
            textposition='outside',
            textfont=dict(size=12, family="Arial, sans-serif"),
            hovertemplate='<b>✈️ %{x}</b><br><br>💰 Average Price: $%{y:.0f}<br>📊 Median Price: $%{customdata[0]:.0f}<br>📈 Price Std: $%{customdata[1]:.0f}<br>✈️ Flights: %{customdata[2]}<br><br><i>Click to highlight airline</i><extra></extra>',
            customdata=np.column_stack([
                airline_price_stats['median_price'],
                airline_price_stats['price_std'],
                airline_price_stats['flight_count']
            ])
        ),
        row=5, col=2
    )

    # 2. Enhanced price analysis with 3D visualization
    print("💰 Creating Enhanced Price Analysis...")
    
    # 3D Price Analysis
    sample_3d = df.sample(5000)
    fig_3d = go.Figure(data=[go.Scatter3d(
        x=sample_3d['duration'],
        y=sample_3d['days_left'],
        z=sample_3d['price'],
        mode='markers',
        marker=dict(
            size=3,
            color=sample_3d['price'],
            colorscale='Viridis',
            opacity=0.8
        ),
        text=sample_3d['airline'],
        hovertemplate='<b>Airline:</b> %{text}<br>' +
                     '<b>Duration:</b> %{x} hours<br>' +
                     '<b>Days Left:</b> %{y}<br>' +
                     '<b>Price:</b> $%{z}<extra></extra>'
    )])
    
    fig_3d.update_layout(
        title='3D Price Analysis: Duration vs Days Left vs Price',
        scene=dict(
            xaxis_title='Duration (hours)',
            yaxis_title='Days Left',
            zaxis_title='Price ($)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        height=350,
        template='plotly_white',
        margin=dict(l=60, r=60, t=80, b=60)
    )

    # Enhanced box plot
    fig_price = px.box(
        df, x='airline', y='price', color='class',
        title='Price Distribution by Airline and Class',
        labels={'price': 'Price ($)', 'airline': 'Airline', 'class': 'Class'},
        color_discrete_map={'Economy': '#4ECDC4', 'Business': '#FF6B6B'}
    )
    fig_price.update_layout(
        template='plotly_white', 
        title_font_size=20,
        title_font_color='#2c3e50',
        font=dict(size=12),
        margin=dict(l=60, r=60, t=80, b=60),
        height=350
    )
    
    # Advanced Price Analysis: Additional Sophisticated Visualizations
    print("🔬 Creating Advanced Price Analysis Visualizations...")
    
    # 1. Price Distribution by Stops with Violin + Box Plot
    fig_price_stops = go.Figure()
    
    for i, stops in enumerate(sorted(df['stops'].unique())):
        stops_data = df[df['stops'] == stops]['price']
        
        # Add Violin plot
        fig_price_stops.add_trace(go.Violin(
            y=stops_data,
            name=f"{stops} Stops",
            box_visible=True,
            meanline_visible=True,
            line_color=airline_colors[i % len(airline_colors)],
            fillcolor=airline_colors[i % len(airline_colors)],
            opacity=0.7
        ))
    
    fig_price_stops.update_layout(
        title='🎯 Price Distribution by Number of Stops',
        yaxis_title='Price ($)',
        xaxis_title='Number of Stops',
        template='plotly_white',
        height=350,
        showlegend=True,
        title_font_size=18,
        title_font_color='#2c3e50',
        margin=dict(l=60, r=60, t=80, b=60),
        legend=dict(x=0.98, y=0.98, xanchor='right', yanchor='top')
    )
    
    # 2. Price Heatmap: Airline vs Class vs Average Price
    price_heatmap_data = df.groupby(['airline', 'class'])['price'].mean().unstack(fill_value=0)
    
    fig_price_heatmap = go.Figure(data=go.Heatmap(
        z=price_heatmap_data.values,
        x=price_heatmap_data.columns,
        y=price_heatmap_data.index,
        colorscale='Viridis',
        text=price_heatmap_data.values.round(0),
        texttemplate='$%{text:.0f}',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>✈️ %{y}</b><br><b>💺 %{x}</b><br><b>💰 Average Price: $%{z:.0f}</b><extra></extra>'
    ))
    
    fig_price_heatmap.update_layout(
        title='🔥 Price Heatmap: Airline vs Class',
        xaxis_title='Class',
        yaxis_title='Airline',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # 3. Price vs Duration Scatter with Trend Lines
    sample_scatter = df.sample(8000)
    
    fig_price_duration = go.Figure()
    
    # Add scatter plot
    fig_price_duration.add_trace(go.Scatter(
        x=sample_scatter['duration'],
        y=sample_scatter['price'],
        mode='markers',
        name='Flight Data',
        marker=dict(
            size=6,
            color=sample_scatter['price'],
            colorscale='Plasma',
            opacity=0.6,
            showscale=True,
            colorbar=dict(
                title="Price ($)",
                titlefont=dict(size=14),
                tickfont=dict(size=12),
                x=1.15,
                thickness=20
            )
        ),
        text=sample_scatter['airline'] + '<br>Class: ' + sample_scatter['class'],
        hovertemplate='<b>✈️ %{text}</b><br><br>⏱️ Duration: %{x:.1f} hours<br>💰 Price: $%{y:.0f}<extra></extra>'
    ))
    
    # Add trend line
    z = np.polyfit(sample_scatter['duration'], sample_scatter['price'], 2)
    p = np.poly1d(z)
    x_trend = np.linspace(sample_scatter['duration'].min(), sample_scatter['duration'].max(), 100)
    y_trend = p(x_trend)
    
    fig_price_duration.add_trace(go.Scatter(
        x=x_trend,
        y=y_trend,
        mode='lines',
        name='Trend Line (Polynomial)',
        line=dict(color='red', width=3, dash='dash'),
        showlegend=True
    ))
    
    fig_price_duration.update_layout(
        title='📈 Price vs Duration Analysis with Trend Line',
        xaxis_title='Duration (hours)',
        yaxis_title='Price ($)',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        margin=dict(l=60, r=80, t=80, b=60),
        coloraxis_colorbar=dict(x=1.02, thickness=20)
    )
    
    # 4. Price Distribution by Days Left (Histogram + KDE)
    fig_price_days = go.Figure()
    
    # Create histogram
    fig_price_days.add_trace(go.Histogram(
        x=df['days_left'],
        y=df['price'],
        histfunc='avg',
        nbinsx=20,
        name='Average Price by Days Left',
        marker_color='#4ECDC4',
        opacity=0.7,
        hovertemplate='<b>📅 Days Left: %{x}</b><br><b>💰 Average Price: $%{y:.0f}</b><extra></extra>'
    ))
    
    # Add KDE-like smoothing
    days_bins = pd.cut(df['days_left'], bins=20)
    price_by_days = df.groupby(days_bins)['price'].mean().reset_index()
    price_by_days['days_mid'] = price_by_days['days_left'].apply(lambda x: x.mid)
    
    fig_price_days.add_trace(go.Scatter(
        x=price_by_days['days_mid'],
        y=price_by_days['price'],
        mode='lines+markers',
        name='Price Trend',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=6, color='#FF6B6B'),
        hovertemplate='<b>📅 Days Left: %{x:.0f}</b><br><b>💰 Average Price: $%{y:.0f}</b><extra></extra>'
    ))
    
    fig_price_days.update_layout(
        title='📊 Price Distribution by Days Until Departure',
        xaxis_title='Days Left',
        yaxis_title='Average Price ($)',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        barmode='overlay',
        margin=dict(l=60, r=60, t=80, b=60),
        legend=dict(x=0.98, y=0.98, xanchor='right', yanchor='top')
    )

    # 3. Enhanced route analysis with bubble chart
    print("🛫 Creating Enhanced Route Analysis...")
    
    # Route bubble chart
    route_stats = df.groupby(['source_city', 'destination_city']).agg({
        'price': ['mean', 'count'],
        'duration': 'mean'
    }).reset_index()
    route_stats.columns = ['source_city', 'destination_city', 'avg_price', 'flight_count', 'avg_duration']
    
    fig_route_bubble = px.scatter(
        route_stats,
        x='avg_price',
        y='avg_duration',
        size='flight_count',
        color='source_city',
        hover_data=['destination_city'],
        title='Route Analysis: Price vs Duration vs Flight Count',
        labels={'avg_price': 'Average Price ($)', 'avg_duration': 'Average Duration (hours)', 'flight_count': 'Number of Flights'},
        color_discrete_sequence=route_colors
    )
    fig_route_bubble.update_layout(
        template='plotly_white',
        title_font_size=18,
        title_font_color='#2c3e50',
        height=350,
        margin=dict(l=60, r=60, t=80, b=60)
    )

    # Route Popularity Bar Chart (replacing problematic sunburst)
    route_popularity = df.groupby(['source_city', 'destination_city']).size().reset_index(name='flight_count')
    route_popularity = route_popularity.sort_values('flight_count', ascending=False).head(20)
    route_popularity['route'] = route_popularity['source_city'] + ' → ' + route_popularity['destination_city']
    
    fig_route = go.Figure(data=[
        go.Bar(
            x=route_popularity['route'],
            y=route_popularity['flight_count'],
            marker_color='#4ECDC4',
            marker_line_color='#26A69A',
            marker_line_width=2,
            text=route_popularity['flight_count'],
            textposition='outside',
            textfont=dict(size=10),
            hovertemplate='<b>🌍 Route: %{x}</b><br><br>✈️ Flight Count: %{y}<br>📊 Rank: %{customdata}<extra></extra>',
            customdata=[i+1 for i in range(len(route_popularity))]
        )
    ])
    
    fig_route.update_layout(
        title='🌍 Top 20 Route Popularity',
        xaxis_title='Route',
        yaxis_title='Number of Flights',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        xaxis=dict(tickangle=45),
        margin=dict(l=60, r=60, t=80, b=80)
    )
    
    # Add a beautiful network graph for top routes
    print("🕸️ Creating Route Network Graph...")
    top_routes = df.groupby(['source_city', 'destination_city']).size().reset_index(name='flight_count')
    top_routes = top_routes.nlargest(15, 'flight_count')  # Top 15 routes
    
    # Create network graph
    nodes = list(set(top_routes['source_city'].tolist() + top_routes['destination_city'].tolist()))
    node_indices = {node: i for i, node in enumerate(nodes)}
    
    edge_x = []
    edge_y = []
    edge_weights = []
    
    for _, route in top_routes.iterrows():
        x0, y0 = node_indices[route['source_city']], node_indices[route['destination_city']]
        edge_x.extend([x0, y0, None])
        edge_y.extend([y0, x0, None])
        edge_weights.extend([route['flight_count'], route['flight_count'], None])
    
    node_trace = go.Scatter(
        x=[], y=[],
        text=[],
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='Viridis',
            size=20,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2,
            line_color='white'
        ),
        textposition='middle center',
        textfont=dict(size=12, color='white')
    )
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Position nodes in a circle
    import math
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / len(nodes)
        node_x.append(math.cos(angle))
        node_y.append(math.sin(angle))
        node_text.append(node)
        node_colors.append(len([r for _, r in top_routes.iterrows() if r['source_city'] == node or r['destination_city'] == node]))
    
    node_trace.x = node_x
    node_trace.y = node_y
    node_trace.text = node_text
    node_trace.marker.color = node_colors
    node_trace.marker.size = [max(15, c * 2) for c in node_colors]  # Size based on connections
    
    fig_network = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title='Top Routes Network Graph',
                               titlefont_size=18,
                               title_font_color='#2c3e50',
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=60,l=60,r=60,t=80),
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               template='plotly_white',
                               height=350
                           ))
    
    # Additional Enhanced Route Analysis Charts
    print("🗺️ Creating Additional Route Analysis Charts...")
    
    # 1. Route Price Distribution by Airline
    route_airline_price = df.groupby(['source_city', 'destination_city', 'airline'])['price'].agg(['mean', 'count']).reset_index()
    route_airline_price = route_airline_price[route_airline_price['count'] > 5]  # Filter for meaningful data
    
    fig_route_airline = go.Figure()
    
    for airline in route_airline_price['airline'].unique():
        airline_data = route_airline_price[route_airline_price['airline'] == airline]
        fig_route_airline.add_trace(go.Scatter(
            x=airline_data['source_city'] + ' → ' + airline_data['destination_city'],
            y=airline_data['mean'],
            mode='markers',
            name=airline,
            marker=dict(
                size=airline_data['count'] / 2 + 5,
                opacity=0.7
            ),
            text=airline_data['airline'] + '<br>Flights: ' + airline_data['count'].astype(str),
            hovertemplate='<b>✈️ %{text}</b><br><br>🌍 Route: %{x}<br>💰 Average Price: $%{y:.0f}<br>✈️ Flight Count: %{marker.size}<br><br><i>Size indicates number of flights</i><extra></extra>'
        ))
    
    fig_route_airline.update_layout(
        title='✈️ Route Price Analysis by Airline',
        xaxis_title='Route',
        yaxis_title='Average Price ($)',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        xaxis=dict(tickangle=45),
        margin=dict(l=60, r=60, t=80, b=80)
    )
    
    # 2. Route Efficiency Analysis (Price per Hour)
    route_efficiency = df.groupby(['source_city', 'destination_city']).agg({
        'price': 'mean',
        'duration': 'mean'
    }).reset_index()
    route_efficiency['flight_count'] = df.groupby(['source_city', 'destination_city']).size().reset_index(name='count')['count']
    route_efficiency['price_per_hour'] = route_efficiency['price'] / route_efficiency['duration']
    route_efficiency = route_efficiency.sort_values('price_per_hour', ascending=False).head(20)
    
    fig_route_efficiency = go.Figure(data=[
        go.Bar(
            x=route_efficiency['source_city'] + ' → ' + route_efficiency['destination_city'],
            y=route_efficiency['price_per_hour'],
            marker_color='#FF6B6B',
            marker_line_color='#E53E3E',
            marker_line_width=2,
            text=route_efficiency['price_per_hour'].round(2),
            textposition='outside',
            textfont=dict(size=10),
            hovertemplate='<b>🌍 Route: %{x}</b><br><br>💰 Price/Hour: $%{y:.2f}<br>⏱️ Duration: %{customdata[0]:.1f}h<br>✈️ Flights: %{customdata[1]}<extra></extra>',
            customdata=np.column_stack([route_efficiency['duration'], route_efficiency['flight_count']])
        )
    ])
    
    fig_route_efficiency.update_layout(
        title='⚡ Route Efficiency: Price per Hour Analysis',
        xaxis_title='Route',
        yaxis_title='Price per Hour ($/h)',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        xaxis=dict(tickangle=45),
        margin=dict(l=60, r=60, t=80, b=80)
    )
    
    # 3. Route Popularity Treemap (Removed to reduce to 6 charts)
    
    # 4. Route Price Range Analysis (Box Plot)
    route_price_ranges = df.groupby(['source_city', 'destination_city'])['price'].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
    route_price_ranges = route_price_ranges[route_price_ranges['count'] > 10]  # Filter for routes with sufficient data
    route_price_ranges = route_price_ranges.sort_values('mean', ascending=False).head(15)
    
    fig_route_price_ranges = go.Figure()
    
    for _, route in route_price_ranges.iterrows():
        route_data = df[(df['source_city'] == route['source_city']) & 
                       (df['destination_city'] == route['destination_city'])]['price']
        
        fig_route_price_ranges.add_trace(go.Box(
            y=route_data,
            name=route['source_city'] + ' → ' + route['destination_city'],
            boxpoints='outliers',
            marker_color='#4ECDC4',
            line_color='#26A69A',
            hovertemplate='<b>🌍 Route: %{fullData.name}</b><br><br>💰 Price: $%{y}<br>📊 Mean: $%{customdata[0]:.0f}<br>📈 Std: $%{customdata[1]:.0f}<br>✈️ Flights: %{customdata[2]}<extra></extra>',
            customdata=np.column_stack([
                [route['mean']] * len(route_data),
                [route['std']] * len(route_data),
                [route['count']] * len(route_data)
            ])
        ))
    
    fig_route_price_ranges.update_layout(
        title='📊 Route Price Distribution Analysis',
        yaxis_title='Price ($)',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        showlegend=False,
        margin=dict(l=60, r=60, t=80, b=60)
    )

    # 4. Enhanced time analysis with area charts
    print("⏰ Creating Enhanced Time Analysis...")
    
    # Time-based price trends
    time_price = df.groupby(['departure_time', 'class'])['price'].mean().reset_index()
    fig_time_area = px.area(
        time_price, 
        x='departure_time', 
        y='price',
        color='class',
        title='Price Trends by Departure Time and Class',
        labels={'price': 'Average Price ($)', 'departure_time': 'Departure Time', 'class': 'Class'},
        color_discrete_map={'Economy': '#4ECDC4', 'Business': '#FF6B6B'}
    )
    fig_time_area.update_layout(
        template='plotly_white', 
        title_font_size=18,
        title_font_color='#2c3e50',
        height=350,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # Additional Time Analysis Charts
    print("⏰ Creating Additional Time Analysis Charts...")
    
    # 1. Price Trends by Days Left (Line Chart)
    days_price_trend = df.groupby('days_left')['price'].agg(['mean', 'std']).reset_index()
    days_price_trend = days_price_trend[days_price_trend['days_left'] <= 30]  # Focus on last 30 days
    
    fig_days_price_trend = go.Figure()
    
    fig_days_price_trend.add_trace(go.Scatter(
        x=days_price_trend['days_left'],
        y=days_price_trend['mean'],
        mode='lines+markers',
        name='Average Price',
        line=dict(color='#667eea', width=3),
        marker=dict(size=6, color='#667eea'),
        hovertemplate='<b>📅 Days Left: %{x}</b><br><br>💰 Average Price: $%{y:.0f}<br>📊 Std Dev: $%{customdata[0]:.0f}<extra></extra>',
        customdata=days_price_trend['std']
    ))
    
    # Add confidence interval
    fig_days_price_trend.add_trace(go.Scatter(
        x=days_price_trend['days_left'],
        y=days_price_trend['mean'] + days_price_trend['std'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig_days_price_trend.add_trace(go.Scatter(
        x=days_price_trend['days_left'],
        y=days_price_trend['mean'] - days_price_trend['std'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.2)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig_days_price_trend.update_layout(
        title='📈 Price Trends by Days Until Departure',
        xaxis_title='Days Left',
        yaxis_title='Average Price ($)',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # 2. Departure Time Distribution (Histogram)
    fig_departure_dist = go.Figure()
    
    fig_departure_dist.add_trace(go.Histogram(
        x=df['departure_time'],
        nbinsx=12,
        marker_color='#4ECDC4',
        opacity=0.7,
        hovertemplate='<b>🕐 Departure Time: %{x}</b><br><br>✈️ Number of Flights: %{y}<extra></extra>'
    ))
    
    fig_departure_dist.update_layout(
        title='🕐 Flight Distribution by Departure Time',
        xaxis_title='Departure Time',
        yaxis_title='Number of Flights',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # 3. Price vs Duration by Time of Day (Scatter)
    sample_time_scatter = df.sample(min(5000, len(df)))
    
    fig_time_scatter = go.Figure()
    
    for time_slot in ['Morning', 'Afternoon', 'Evening', 'Night']:
        if time_slot == 'Morning':
            time_data = sample_time_scatter[sample_time_scatter['departure_time'].isin(['6AM-12PM'])]
            color = '#FFD93D'
        elif time_slot == 'Afternoon':
            time_data = sample_time_scatter[sample_time_scatter['departure_time'].isin(['12PM-6PM'])]
            color = '#FF6B6B'
        elif time_slot == 'Evening':
            time_data = sample_time_scatter[sample_time_scatter['departure_time'].isin(['6PM-12AM'])]
            color = '#4ECDC4'
        else:  # Night
            time_data = sample_time_scatter[sample_time_scatter['departure_time'].isin(['12AM-6AM'])]
            color = '#6C5CE7'
        
        if len(time_data) > 0:
            fig_time_scatter.add_trace(go.Scatter(
                x=time_data['duration'],
                y=time_data['price'],
                mode='markers',
                name=time_slot,
                marker=dict(
                    size=6,
                    color=color,
                    opacity=0.6
                ),
                hovertemplate='<b>%{fullData.name}</b><br><br>⏱️ Duration: %{x:.1f}h<br>💰 Price: $%{y:.0f}<extra></extra>'
            ))
    
    fig_time_scatter.update_layout(
        title='🌅 Price vs Duration by Time of Day',
        xaxis_title='Duration (hours)',
        yaxis_title='Price ($)',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # 4. Monthly Price Patterns by Days Left (Box Plot)
    # Create monthly buckets based on days left
    df['month_bucket'] = pd.cut(df['days_left'], bins=[0, 7, 15, 30, 60, 90, 120, 150, 180, 365], 
                                labels=['1 Week', '2 Weeks', '1 Month', '2 Months', '3 Months', '4 Months', '5 Months', '6 Months', '1 Year'])
    
    monthly_price = df.groupby('month_bucket')['price'].apply(list).reset_index()
    monthly_price = monthly_price.dropna()
    
    fig_weekly_price = go.Figure()
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#FFB6C1', '#20B2AA']
    
    for i, month in enumerate(monthly_price['month_bucket']):
        if pd.notna(month):
            month_data = monthly_price[monthly_price['month_bucket'] == month]['price'].iloc[0]
            fig_weekly_price.add_trace(go.Box(
                y=month_data,
                name=str(month),
                marker_color=colors[i % len(colors)],
                boxpoints='outliers',
                hovertemplate='<b>📅 %{fullData.name}</b><br><br>💰 Price: $%{y}<extra></extra>'
            ))
    
    fig_weekly_price.update_layout(
        title='📅 Price Patterns by Booking Time (Days Left)',
        yaxis_title='Price ($)',
        template='plotly_white',
        height=350,
        title_font_size=18,
        title_font_color='#2c3e50',
        xaxis=dict(tickangle=45),
        margin=dict(l=60, r=60, t=80, b=60)
    )

    # 5. ML Model Performance Dashboard
    print("🤖 Creating ML Model Performance Dashboard...")
    
    # Model comparison
    model_names = list(model_results.keys())
    mae_scores = [model_results[name]['mae'] for name in model_names]
    r2_scores = [model_results[name]['r2'] for name in model_names]
    
    fig_ml_performance = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Model MAE Comparison', 'Model R² Score Comparison'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    fig_ml_performance.add_trace(
        go.Bar(x=model_names, y=mae_scores, name='MAE', marker_color='#FF6B6B'),
        row=1, col=1
    )
    
    fig_ml_performance.add_trace(
        go.Bar(x=model_names, y=r2_scores, name='R²', marker_color='#4ECDC4'),
        row=1, col=2
    )
    
    fig_ml_performance.update_layout(
        title_text='ML Model Performance Comparison',
        template='plotly_white',
        title_font_size=22,
        title_font_color='#2c3e50',
        height=500
    )

    # 6. Demand Forecasting Visualization
    print("📈 Creating Demand Forecasting Visualization...")
    
    # Days left distribution by airline
    fig_demand = px.histogram(
        df,
        x='days_left',
        color='airline',
        title='Demand Distribution by Days Left and Airline',
        labels={'days_left': 'Days Until Departure', 'count': 'Number of Bookings', 'airline': 'Airline'},
        nbins=20,
        color_discrete_sequence=airline_colors
    )
    fig_demand.update_layout(
        template='plotly_white',
        title_font_size=22,
        title_font_color='#2c3e50'
    )

    return (fig_main, fig_3d, fig_price, fig_route_bubble, fig_route, fig_network,
            fig_time_area, fig_ml_performance, fig_demand, fig_price_stops, 
            fig_price_heatmap, fig_price_duration, fig_price_days, fig_route_airline,
            fig_route_efficiency, fig_route_price_ranges, fig_days_price_trend,
            fig_departure_dist, fig_time_scatter, fig_weekly_price)


def build_predictor_payload(model_results, scaler, le_airline, le_source, le_dest, le_class, le_stops, le_dep_time, le_arr_time):
    """Serialize LinearRegression + StandardScaler for client-side price prediction."""
    lr = model_results["Linear Regression"]["model"]
    return {
        "means": scaler.mean_.tolist(),
        "scales": scaler.scale_.tolist(),
        "coef": lr.coef_.tolist(),
        "intercept": float(lr.intercept_),
        "airlines": le_airline.classes_.tolist(),
        "sources": le_source.classes_.tolist(),
        "dests": le_dest.classes_.tolist(),
        "classes": le_class.classes_.tolist(),
        "stops": le_stops.classes_.tolist(),
        "dep_times": le_dep_time.classes_.tolist(),
        "arr_times": le_arr_time.classes_.tolist(),
        "r2": float(model_results["Linear Regression"]["r2"]),
    }


def create_price_predictor_widget():
    """Create HTML for interactive price prediction widget."""
    return """
    <div class="prediction-widget">
        <h3>🎯 Price Prediction Tool</h3>
        <p class="prediction-widget-note">Enter route and trip details below. You will see <strong>predicted prices for every airline</strong> using the same parameters (trained linear regression model on scaled features).</p>
        <div class="widget-grid">
            <div class="input-group">
                <label>Source City:</label>
                <select id="source-select">
                    <option value="Delhi">Delhi</option>
                    <option value="Mumbai">Mumbai</option>
                    <option value="Bangalore">Bangalore</option>
                    <option value="Kolkata">Kolkata</option>
                    <option value="Hyderabad">Hyderabad</option>
                    <option value="Chennai">Chennai</option>
                </select>
            </div>
            <div class="input-group">
                <label>Destination City:</label>
                <select id="dest-select">
                    <option value="Mumbai">Mumbai</option>
                    <option value="Delhi">Delhi</option>
                    <option value="Bangalore">Bangalore</option>
                    <option value="Kolkata">Kolkata</option>
                    <option value="Hyderabad">Hyderabad</option>
                    <option value="Chennai">Chennai</option>
                </select>
            </div>
            <div class="input-group">
                <label>Class:</label>
                <select id="class-select">
                    <option value="Economy">Economy</option>
                    <option value="Business">Business</option>
                </select>
            </div>
            <div class="input-group">
                <label>Stops:</label>
                <select id="stops-select">
                    <option value="zero">Zero</option>
                    <option value="one">One</option>
                    <option value="two_or_more">Two or More</option>
                </select>
            </div>
            <div class="input-group">
                <label>Duration (hours):</label>
                <input type="number" id="duration-input" min="0.5" max="50" step="0.1" value="2.0">
            </div>
            <div class="input-group">
                <label>Days Left:</label>
                <input type="number" id="days-input" min="1" max="49" value="7">
            </div>
            <div class="input-group">
                <label>Departure Time:</label>
                <select id="dep-time-select">
                    <option value="Early_Morning">Early Morning</option>
                    <option value="Morning">Morning</option>
                    <option value="Afternoon">Afternoon</option>
                    <option value="Evening">Evening</option>
                    <option value="Night">Night</option>
                    <option value="Late_Night">Late Night</option>
                </select>
            </div>
            <div class="input-group">
                <label>Arrival Time:</label>
                <select id="arr-time-select">
                    <option value="Early_Morning">Early Morning</option>
                    <option value="Morning">Morning</option>
                    <option value="Afternoon">Afternoon</option>
                    <option value="Evening">Evening</option>
                    <option value="Night">Night</option>
                    <option value="Late_Night">Late Night</option>
                </select>
            </div>
        </div>
        <button onclick="predictPrice()" class="predict-btn">🚀 Predict Price</button>
        <div id="prediction-result" class="prediction-result"></div>
    </div>
    """

def main(data_path=None):
    """Main function to create an enhanced dashboard with ML models."""
    print("🎨 CREATING ENHANCED BEAUTIFUL DASHBOARD WITH ML MODELS")
    print("="*70)

    # Read the dataset
    data_path = resolve_data_path(data_path)
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_csv(data_path)
    print(f"📊 Dataset loaded: {len(df):,} flights")

    # Create ML models
    model_results, demand_model, demand_mae, demand_r2, scaler, le_airline, le_source, le_dest, le_class, le_stops, le_dep_time, le_arr_time = create_ml_models(df)

    predictor_json = json.dumps(
        build_predictor_payload(
            model_results,
            scaler,
            le_airline,
            le_source,
            le_dest,
            le_class,
            le_stops,
            le_dep_time,
            le_arr_time,
        )
    )

    # Create enhanced visualizations
    (fig_main, fig_3d, fig_price, fig_route_bubble, fig_route, fig_network,
     fig_time_area, fig_ml_performance, fig_demand, fig_price_stops, 
     fig_price_heatmap, fig_price_duration, fig_price_days, fig_route_airline,
     fig_route_efficiency, fig_route_price_ranges, fig_days_price_trend,
     fig_departure_dist, fig_time_scatter, fig_weekly_price) = create_enhanced_visualizations(df, model_results, demand_model, demand_mae, demand_r2)

    # Convert figures to embeddable HTML fragments
    main_fig_html = pio.to_html(fig_main, include_plotlyjs='cdn', full_html=False)
    fig_3d_html = pio.to_html(fig_3d, include_plotlyjs=False, full_html=False)
    price_fig_html = pio.to_html(fig_price, include_plotlyjs=False, full_html=False)
    route_bubble_html = pio.to_html(fig_route_bubble, include_plotlyjs=False, full_html=False)
    route_fig_html = pio.to_html(fig_route, include_plotlyjs=False, full_html=False)
    fig_network_html = pio.to_html(fig_network, include_plotlyjs=False, full_html=False)
    time_area_html = pio.to_html(fig_time_area, include_plotlyjs=False, full_html=False)
    ml_performance_html = pio.to_html(fig_ml_performance, include_plotlyjs=False, full_html=False)
    demand_html = pio.to_html(fig_demand, include_plotlyjs=False, full_html=False)
    
    # Convert new Advanced Price Analysis figures to HTML
    price_stops_html = pio.to_html(fig_price_stops, include_plotlyjs=False, full_html=False)
    price_heatmap_html = pio.to_html(fig_price_heatmap, include_plotlyjs=False, full_html=False)
    price_duration_html = pio.to_html(fig_price_duration, include_plotlyjs=False, full_html=False)
    price_days_html = pio.to_html(fig_price_days, include_plotlyjs=False, full_html=False)
    
    # Convert new Enhanced Route Analysis figures to HTML
    route_airline_html = pio.to_html(fig_route_airline, include_plotlyjs=False, full_html=False)
    route_efficiency_html = pio.to_html(fig_route_efficiency, include_plotlyjs=False, full_html=False)
    route_price_ranges_html = pio.to_html(fig_route_price_ranges, include_plotlyjs=False, full_html=False)
    
    # Convert new Enhanced Time Analysis figures to HTML
    days_price_trend_html = pio.to_html(fig_days_price_trend, include_plotlyjs=False, full_html=False)
    departure_dist_html = pio.to_html(fig_departure_dist, include_plotlyjs=False, full_html=False)
    time_scatter_html = pio.to_html(fig_time_scatter, include_plotlyjs=False, full_html=False)
    weekly_price_html = pio.to_html(fig_weekly_price, include_plotlyjs=False, full_html=False)

    # Create price prediction widget
    prediction_widget = create_price_predictor_widget()

    print("🎨 Assembling enhanced dashboard...")
    
    # Create the enhanced HTML dashboard
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Flight Data Analysis Dashboard with ML</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
            color: #2c3e50;
        }}
        
        .header {{
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            font-size: 1.2rem;
            color: #7f8c8d;
        }}
        
        .nav {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 30px 0;
            flex-wrap: wrap;
            padding: 0 20px;
        }}
        
        .nav-button {{
            padding: 15px 30px;
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
            border: none;
            border-radius: 30px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            color: #2c3e50;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        
        .nav-button:hover {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }}
        
        .nav-button.active {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }}
        
        .section {{ 
            display: none; 
            padding: 30px; 
            animation: fadeIn 0.5s ease-in;
        }}
        
        .section.active {{ display: block; }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .dashboard-card {{
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            margin: 30px auto;
            max-width: 1600px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .dashboard-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }}
        
        .card-header {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 25px;
            color: #2c3e50;
            text-align: center;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        .prediction-widget {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 20px;
            margin: 20px 0;
        }}
        
        .prediction-widget h3 {{
            text-align: center;
            margin-bottom: 25px;
            font-size: 1.5rem;
        }}

        .prediction-widget-note {{
            text-align: center;
            margin-bottom: 20px;
            font-size: 0.95rem;
            opacity: 0.95;
            line-height: 1.45;
        }}
        
        .widget-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        
        .input-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .input-group label {{
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .input-group select,
        .input-group input {{
            padding: 12px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            background: rgba(255,255,255,0.9);
            color: #2c3e50;
        }}
        
        .predict-btn {{
            background: linear-gradient(45deg, #FF6B6B, #FF8E53);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: block;
            margin: 0 auto;
        }}
        
        .predict-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }}
        
        .prediction-result {{
            margin-top: 20px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            text-align: left;
            font-size: 1rem;
            min-height: 60px;
        }}

        .prediction-result table {{
            width: 100%;
            border-collapse: collapse;
            color: white;
        }}

        .prediction-result th, .prediction-result td {{
            padding: 10px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.25);
        }}

        .prediction-result th {{
            font-weight: 700;
            text-align: left;
            background: rgba(0,0,0,0.15);
        }}

        .prediction-result tr.row-lowest td {{
            background: rgba(46, 204, 113, 0.25);
            font-weight: 600;
        }}

        .prediction-result .model-meta {{
            margin-top: 12px;
            font-size: 0.85rem;
            opacity: 0.9;
            text-align: center;
        }}
        
        /* Price Analysis Grid Styling */
        .price-analysis-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 15px;
        }}
        
        .price-chart {{
            background: rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .price-chart:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            background: rgba(255, 255, 255, 0.95);
        }}
        
        .price-chart h4 {{
            text-align: center;
            margin-bottom: 15px;
            color: #2c3e50;
            font-size: 1.1rem;
            font-weight: 600;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        /* Responsive design for smaller screens */
        @media (max-width: 1400px) {{
            .price-analysis-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
            }}
        }}
        @media (max-width: 900px) {{
            .price-analysis-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
        }}
        
        /* Route Analysis Grid Styling */
        .route-analysis-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 15px;
        }}
        
        .route-chart {{
            background: rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .route-chart:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            background: rgba(255, 255, 255, 0.95);
        }}
        
        .route-chart h4 {{
            text-align: center;
            margin-bottom: 15px;
            color: #2c3e50;
            font-size: 1.1rem;
            font-weight: 600;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        /* Responsive design for route analysis */
        @media (max-width: 1400px) {{
            .route-analysis-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
            }}
        }}
        @media (max-width: 900px) {{
            .route-analysis-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
        }}
        
        /* Time Analysis Grid Styling */
        .time-analysis-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 15px;
        }}
        
        .time-chart {{
            background: rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .time-chart:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            background: rgba(255, 255, 255, 0.95);
        }}
        
        .time-chart h4 {{
            text-align: center;
            margin-bottom: 15px;
            color: #2c3e50;
            font-size: 1.1rem;
            font-weight: 600;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        /* Responsive design for time analysis */
        @media (max-width: 1400px) {{
            .time-analysis-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
            }}
        }}
        
        @media (max-width: 900px) {{
            .time-analysis-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.8) 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .stat-card h4 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        @media (max-width: 768px) {{
            .nav {{
                flex-direction: column;
                align-items: center;
            }}
            
            .widget-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Enhanced Flight Data Analysis Dashboard</h1>
        <p>Advanced Analytics with Machine Learning Models for Price Prediction & Demand Forecasting</p>
    </div>

    <div class="nav">
        <button class="nav-button active" onclick="showSection('main')">📊 Main Dashboard</button>
        <button class="nav-button" onclick="showSection('pricing')">💰 Price Analysis</button>
        <button class="nav-button" onclick="showSection('routes')">🛫 Route Analysis</button>
        <button class="nav-button" onclick="showSection('timing')">⏰ Time Analysis</button>
        <button class="nav-button" onclick="showSection('ml')">🤖 ML Models</button>
        <button class="nav-button" onclick="showSection('prediction')">🎯 Price Predictor</button>
    </div>

    <div id="main" class="section active">
        <div class="dashboard-card">
            <div class="card-header">📊 Enhanced Main Dashboard</div>
            {main_fig_html}
        </div>
    </div>

    <div id="pricing" class="section">
        <div class="dashboard-card">
            <div class="card-header">💰 Advanced Price Analysis</div>
            <div class="price-analysis-grid">
                <div class="price-chart">
                    <h4>🚀 3D Price Analysis</h4>
                    {fig_3d_html}
                </div>
                <div class="price-chart">
                    <h4>📊 Price by Airline & Class</h4>
                    {price_fig_html}
                </div>
                <div class="price-chart">
                    <h4>🎯 Price by Number of Stops</h4>
                    {price_stops_html}
                </div>
                <div class="price-chart">
                    <h4>🔥 Price Heatmap</h4>
                    {price_heatmap_html}
                </div>
                <div class="price-chart">
                    <h4>📈 Price vs Duration Trend</h4>
                    {price_duration_html}
                </div>
                <div class="price-chart">
                    <h4>📅 Price by Days Left</h4>
                    {price_days_html}
                </div>
            </div>
        </div>
    </div>

    <div id="routes" class="section">
        <div class="dashboard-card">
            <div class="card-header">🛫 Enhanced Route Analysis</div>
            <div class="route-analysis-grid">
                <div class="route-chart">
                    <h4>🚀 Route Bubble Analysis</h4>
                    {route_bubble_html}
                </div>
                <div class="route-chart">
                    <h4>🌍 Top 20 Route Popularity</h4>
                    {route_fig_html}
                </div>
                <div class="route-chart">
                    <h4>✈️ Route Price by Airline</h4>
                    {route_airline_html}
                </div>
                <div class="route-chart">
                    <h4>⚡ Route Efficiency Analysis</h4>
                    {route_efficiency_html}
                </div>
                <div class="route-chart">
                    <h4>🕸️ Route Network Graph</h4>
                    {fig_network_html}
                </div>
                <div class="route-chart">
                    <h4>📊 Route Price Distribution</h4>
                    {route_price_ranges_html}
                </div>
            </div>
        </div>
    </div>

    <div id="timing" class="section">
        <div class="dashboard-card">
            <div class="card-header">⏰ Enhanced Time Analysis</div>
            <div class="time-analysis-grid">
                <div class="time-chart">
                    <h4>💰 Price Trends by Time & Class</h4>
                    {time_area_html}
                </div>
                <div class="time-chart">
                    <h4>📈 Price Trends by Days Left</h4>
                    {days_price_trend_html}
                </div>
                <div class="time-chart">
                    <h4>🕐 Flight Distribution by Time</h4>
                    {departure_dist_html}
                </div>
                <div class="time-chart">
                    <h4>🌅 Price vs Duration by Time</h4>
                    {time_scatter_html}
                </div>
                <div class="time-chart">
                    <h4>📅 Weekly Price Patterns</h4>
                    {weekly_price_html}
                </div>
                <div class="time-chart">
                    <h4>📊 Demand by Days Left</h4>
                    {demand_html}
                </div>
            </div>
        </div>
    </div>

    <div id="ml" class="section">
        <div class="dashboard-card">
            <div class="card-header">🤖 Machine Learning Models</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>Best Model (R² Score)</h4>
                    <div class="stat-value">{max([model_results[name]['r2'] for name in model_results.keys()]):.3f}</div>
                </div>
                <div class="stat-card">
                    <h4>Best Model (MAE)</h4>
                    <div class="stat-value">${min([model_results[name]['mae'] for name in model_results.keys()]):.0f}</div>
                </div>
                <div class="stat-card">
                    <h4>Demand Forecast (R²)</h4>
                    <div class="stat-value">{demand_r2:.3f}</div>
                </div>
                <div class="stat-card">
                    <h4>Demand Forecast (MAE)</h4>
                    <div class="stat-value">{demand_mae:.1f} days</div>
                </div>
            </div>
            {ml_performance_html}
        </div>
    </div>

    <div id="prediction" class="section">
        <div class="dashboard-card">
            <div class="card-header">🎯 Interactive Price Prediction Tool</div>
            {prediction_widget}
        </div>
    </div>

    <script id="predictor-config" type="application/json">
{predictor_json}
    </script>

    <script>
        function showSection(sectionId) {{
            const sections = document.querySelectorAll('.section');
            const buttons = document.querySelectorAll('.nav-button');
            
            sections.forEach(section => section.classList.remove('active'));
            buttons.forEach(button => button.classList.remove('active'));
            
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function encodeLabel(val, classes) {{
            const idx = classes.indexOf(val);
            return idx >= 0 ? idx : 0;
        }}

        function formatAirlineDisplay(code) {{
            if (code === 'GO_FIRST') return 'GO FIRST';
            return String(code).replace(/_/g, ' ');
        }}

        function predictPriceForAirline(P, airline, source, dest, classType, stops, depTime, arrTime, duration, daysLeft) {{
            const raw = [
                encodeLabel(airline, P.airlines),
                encodeLabel(source, P.sources),
                encodeLabel(dest, P.dests),
                encodeLabel(classType, P.classes),
                encodeLabel(stops, P.stops),
                encodeLabel(depTime, P.dep_times),
                encodeLabel(arrTime, P.arr_times),
                duration,
                daysLeft
            ];
            const scaled = raw.map((v, i) => {{
                const s = P.scales[i];
                const denom = (s === 0 || !isFinite(s)) ? 1 : s;
                return (v - P.means[i]) / denom;
            }});
            let price = P.intercept;
            for (let i = 0; i < scaled.length; i++) {{
                price += P.coef[i] * scaled[i];
            }}
            // Linear regression is unconstrained; clip so ticket price is never shown negative
            return Math.max(0, price);
        }}

        function predictPrice() {{
            const cfgEl = document.getElementById('predictor-config');
            if (!cfgEl) {{
                document.getElementById('prediction-result').innerHTML = '<span>Prediction model not loaded.</span>';
                return;
            }}
            let P;
            try {{
                P = JSON.parse(cfgEl.textContent);
            }} catch (e) {{
                document.getElementById('prediction-result').innerHTML = '<span>Invalid prediction configuration.</span>';
                return;
            }}

            const source = document.getElementById('source-select').value;
            const dest = document.getElementById('dest-select').value;
            const classType = document.getElementById('class-select').value;
            const stops = document.getElementById('stops-select').value;
            const duration = parseFloat(document.getElementById('duration-input').value);
            const daysLeft = parseInt(document.getElementById('days-input').value, 10);
            const depTime = document.getElementById('dep-time-select').value;
            const arrTime = document.getElementById('arr-time-select').value;

            if (!isFinite(duration) || !isFinite(daysLeft)) {{
                document.getElementById('prediction-result').innerHTML = '<span>Please enter valid duration and days left.</span>';
                return;
            }}

            const rows = [];
            for (let i = 0; i < P.airlines.length; i++) {{
                const airline = P.airlines[i];
                const p = predictPriceForAirline(P, airline, source, dest, classType, stops, depTime, arrTime, duration, daysLeft);
                rows.push({{ airline, price: p, label: formatAirlineDisplay(airline) }});
            }}
            rows.sort((a, b) => a.price - b.price);

            let html = '<table><thead><tr><th>Airline</th><th>Predicted price ($)</th></tr></thead><tbody>';
            const lowest = rows.length ? rows[0].price : null;
            for (let j = 0; j < rows.length; j++) {{
                const r = rows[j];
                const isLow = lowest !== null && Math.abs(r.price - lowest) < 1e-6;
                const cls = isLow ? ' class="row-lowest"' : '';
                html += '<tr' + cls + '><td>' + r.label + '</td><td>' + r.price.toFixed(0) + '</td></tr>';
            }}
            html += '</tbody></table>';
            html += '<div class="model-meta">Linear regression (same scaling as training) · R² = ' + P.r2.toFixed(3) + ' · sorted cheapest → most expensive · values below $0 are shown as $0 (model extrapolation)</div>';

            document.getElementById('prediction-result').innerHTML = html;
        }}
        
        // Initialize first button as active
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelector('.nav-button').classList.add('active');
        }});
    </script>
</body>
</html>
"""

    with open('enhanced_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("\n" + "="*70)
    print("🎉 ENHANCED DASHBOARD WITH ML MODELS CREATION COMPLETE!")
    print("="*70)
    print("\n📁 Generated Files:")
    print("1. enhanced_dashboard.html - Enhanced dashboard with ML models and beautiful visualizations")
    print("\n🚀 Open 'enhanced_dashboard.html' in your browser for the complete experience!")
    print("\n🤖 ML Models Trained:")
    for name, results in model_results.items():
        print(f"   - {name}: R² = {results['r2']:.3f}, MAE = ${results['mae']:.0f}")
    print(f"   - Demand Forecasting: R² = {demand_r2:.3f}, MAE = {demand_mae:.1f} days")

if __name__ == "__main__":
    main() 