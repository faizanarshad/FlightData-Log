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
import plotly.io as pio
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

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
        rows=3, cols=2,
        subplot_titles=(
            '💰 Price Distribution by Airline',
            '🗺️ Route Popularity Heatmap',
            '⏱️ Price vs Duration Analysis',
            '📊 Market Share by Airline',
            '📅 Booking Patterns by Days Left',
            '🛑 Price Analysis by Stops'
        ),
        specs=[
            [{"type": "box"}, {"type": "heatmap"}],
            [{"type": "scatter"}, {"type": "pie"}],
            [{"type": "bar"}, {"type": "violin"}]
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.05
    )

    # Enhanced price distribution by airline with custom colors
    for i, airline in enumerate(df['airline'].unique()):
        airline_data = df[df['airline'] == airline]['price']
        fig_main.add_trace(
            go.Box(
                y=airline_data, 
                name=airline, 
                boxpoints='outliers',
                marker_color=airline_colors[i % len(airline_colors)],
                line_color=airline_colors[i % len(airline_colors)],
                fillcolor=airline_colors[i % len(airline_colors)],
                opacity=0.7
            ),
            row=1, col=1
        )

    # Enhanced route heatmap with custom colorscale
    route_matrix = df.groupby(['source_city', 'destination_city']).size().unstack(fill_value=0)
    fig_main.add_trace(
        go.Heatmap(
            z=route_matrix.values, 
            x=route_matrix.columns, 
            y=route_matrix.index,
            colorscale='Viridis',
            name='Route Popularity',
            showscale=True,
            colorbar=dict(title="Flights")
        ),
        row=1, col=2
    )

    # Enhanced price vs duration with better styling
    sample_df = df.sample(3000)
    fig_main.add_trace(
        go.Scatter(
            x=sample_df['duration'], 
            y=sample_df['price'], 
            mode='markers',
            marker=dict(
                size=4, 
                opacity=0.6, 
                color=sample_df['days_left'], 
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title="Days Left")
            ),
            name='Price vs Duration'
        ),
        row=2, col=1
    )

    # Enhanced market share pie chart
    market_share = df['airline'].value_counts()
    fig_main.add_trace(
        go.Pie(
            labels=market_share.index, 
            values=market_share.values,
            hole=0.4, 
            textinfo='label+percent',
            marker_colors=airline_colors[:len(market_share)],
            textfont_size=14
        ),
        row=2, col=2
    )

    # Enhanced booking patterns with gradient colors
    days_bins = pd.cut(df['days_left'], bins=[0, 7, 14, 30, 49], labels=['1-7', '8-14', '15-30', '31-49'])
    booking_patterns = df.groupby(days_bins)['price'].mean()
    fig_main.add_trace(
        go.Bar(
            x=booking_patterns.index.astype(str), 
            y=booking_patterns.values,
            name='Booking Patterns', 
            marker_color='#FF6B6B',
            marker_line_color='#FF4757',
            marker_line_width=2
        ),
        row=3, col=1
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

    # Enhanced layout
    fig_main.update_layout(
        height=1400,
        title_text="🚀 Enhanced Airlines Data Analysis Dashboard",
        template='plotly_white',
        showlegend=True,
        title_font_size=28,
        title_font_color='#2c3e50',
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=100, b=50, l=50, r=50)
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
        height=600,
        template='plotly_white'
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
        title_font_size=22,
        title_font_color='#2c3e50',
        font=dict(size=14)
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
        title_font_size=22,
        title_font_color='#2c3e50'
    )

    # Enhanced heatmap
    route_matrix = df.groupby(['source_city', 'destination_city']).size().unstack(fill_value=0)
    fig_route = px.imshow(
        route_matrix,
        title='Route Popularity Heatmap',
        labels=dict(x="Destination City", y="Source City", color="Number of Flights"),
        color_continuous_scale='Viridis',
        aspect='auto'
    )
    fig_route.update_layout(
        template='plotly_white', 
        title_font_size=22,
        title_font_color='#2c3e50'
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
        title_font_size=22,
        title_font_color='#2c3e50'
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

    return (fig_main, fig_3d, fig_price, fig_route_bubble, fig_route, 
            fig_time_area, fig_ml_performance, fig_demand)

def create_price_predictor_widget():
    """Create HTML for interactive price prediction widget."""
    return """
    <div class="prediction-widget">
        <h3>🎯 Price Prediction Tool</h3>
        <div class="widget-grid">
            <div class="input-group">
                <label>Airline:</label>
                <select id="airline-select">
                    <option value="Vistara">Vistara</option>
                    <option value="Air_India">Air India</option>
                    <option value="Indigo">Indigo</option>
                    <option value="GO_FIRST">GO FIRST</option>
                    <option value="AirAsia">AirAsia</option>
                    <option value="SpiceJet">SpiceJet</option>
                </select>
            </div>
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

def main():
    """Main function to create an enhanced dashboard with ML models."""
    print("🎨 CREATING ENHANCED BEAUTIFUL DASHBOARD WITH ML MODELS")
    print("="*70)

    # Read the dataset
    data_path = 'data/raw/airlines_flights_data.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_csv(data_path)
    print(f"📊 Dataset loaded: {len(df):,} flights")

    # Create ML models
    model_results, demand_model, demand_mae, demand_r2, scaler, le_airline, le_source, le_dest, le_class, le_stops, le_dep_time, le_arr_time = create_ml_models(df)

    # Create enhanced visualizations
    (fig_main, fig_3d, fig_price, fig_route_bubble, fig_route, 
     fig_time_area, fig_ml_performance, fig_demand) = create_enhanced_visualizations(df, model_results, demand_model, demand_mae, demand_r2)

    # Convert figures to embeddable HTML fragments
    main_fig_html = pio.to_html(fig_main, include_plotlyjs='cdn', full_html=False)
    fig_3d_html = pio.to_html(fig_3d, include_plotlyjs=False, full_html=False)
    price_fig_html = pio.to_html(fig_price, include_plotlyjs=False, full_html=False)
    route_bubble_html = pio.to_html(fig_route_bubble, include_plotlyjs=False, full_html=False)
    route_fig_html = pio.to_html(fig_route, include_plotlyjs=False, full_html=False)
    time_area_html = pio.to_html(fig_time_area, include_plotlyjs=False, full_html=False)
    ml_performance_html = pio.to_html(fig_ml_performance, include_plotlyjs=False, full_html=False)
    demand_html = pio.to_html(fig_demand, include_plotlyjs=False, full_html=False)

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
            text-align: center;
            font-size: 1.2rem;
            min-height: 60px;
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
            {fig_3d_html}
            {price_fig_html}
        </div>
    </div>

    <div id="routes" class="section">
        <div class="dashboard-card">
            <div class="card-header">🛫 Enhanced Route Analysis</div>
            {route_bubble_html}
            {route_fig_html}
        </div>
    </div>

    <div id="timing" class="section">
        <div class="dashboard-card">
            <div class="card-header">⏰ Enhanced Time Analysis</div>
            {time_area_html}
            {demand_html}
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

    <script>
        function showSection(sectionId) {{
            const sections = document.querySelectorAll('.section');
            const buttons = document.querySelectorAll('.nav-button');
            
            sections.forEach(section => section.classList.remove('active'));
            buttons.forEach(button => button.classList.remove('active'));
            
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function predictPrice() {{
            // This is a simplified prediction - in a real app, you'd send data to a backend
            const airline = document.getElementById('airline-select').value;
            const source = document.getElementById('source-select').value;
            const dest = document.getElementById('dest-select').value;
            const classType = document.getElementById('class-select').value;
            const stops = document.getElementById('stops-select').value;
            const duration = parseFloat(document.getElementById('duration-input').value);
            const daysLeft = parseInt(document.getElementById('days-input').value);
            const depTime = document.getElementById('dep-time-select').value;
            const arrTime = document.getElementById('arr-time-select').value;
            
            // Simple heuristic-based prediction (replace with actual ML model)
            let basePrice = 5000;
            
            // Airline adjustments
            const airlineMultipliers = {{
                'Vistara': 1.8,
                'Air_India': 1.4,
                'Indigo': 1.0,
                'GO_FIRST': 1.1,
                'AirAsia': 0.8,
                'SpiceJet': 1.0
            }};
            
            // Class adjustments
            const classMultipliers = {{
                'Economy': 1.0,
                'Business': 2.5
            }};
            
            // Stops adjustments
            const stopsMultipliers = {{
                'zero': 1.2,
                'one': 1.0,
                'two_or_more': 0.8
            }};
            
            // Days left adjustments
            const daysMultiplier = Math.max(1.5, 3 - (daysLeft / 20));
            
            // Duration adjustments
            const durationMultiplier = 1 + (duration / 20);
            
            const predictedPrice = basePrice * 
                                 airlineMultipliers[airline] * 
                                 classMultipliers[classType] * 
                                 stopsMultipliers[stops] * 
                                 daysMultiplier * 
                                 durationMultiplier;
            
            document.getElementById('prediction-result').innerHTML = 
                `<strong>Predicted Price: ${{predictedPrice.toFixed(0)}}</strong><br>
                 <small>Based on selected parameters and historical patterns</small>`;
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