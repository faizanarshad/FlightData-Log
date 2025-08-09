import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
warnings.filterwarnings('ignore')

def main():
    """Main function to run comprehensive data analysis."""
    # Set style for better plots
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")

    print("🚀 AIRLINES DATASET ANALYSIS EXPLORER")
    print("="*60)

    # Read the dataset
    data_path = 'data/raw/airlines_flights_data.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_csv(data_path)

    print(f"📊 Dataset loaded: {df.shape[0]:,} flights, {df.shape[1]} features")
    print("\n" + "="*60)

    # 1. PRICE ANALYSIS
    print("💰 PRICE ANALYSIS")
    print("-" * 30)

    # Price distribution by airline
    plt.figure(figsize=(15, 10))

    plt.subplot(2, 2, 1)
    airline_prices = df.groupby('airline')['price'].agg(['mean', 'median', 'std']).round(0)
    print("Average prices by airline:")
    print(airline_prices)
    airline_prices['mean'].plot(kind='bar', color='skyblue')
    plt.title('Average Ticket Prices by Airline')
    plt.ylabel('Price ($)')
    plt.xticks(rotation=45)

    # Price vs Duration correlation
    plt.subplot(2, 2, 2)
    plt.scatter(df['duration'], df['price'], alpha=0.5, s=1)
    plt.xlabel('Duration (hours)')
    plt.ylabel('Price ($)')
    plt.title('Price vs Flight Duration')
    correlation = df['price'].corr(df['duration'])
    plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', transform=plt.gca().transAxes, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    # Price distribution
    plt.subplot(2, 2, 3)
    plt.hist(df['price'], bins=50, alpha=0.7, color='lightgreen')
    plt.xlabel('Price ($)')
    plt.ylabel('Frequency')
    plt.title('Price Distribution')
    plt.axvline(df['price'].median(), color='red', linestyle='--', label=f'Median: ${df["price"].median():,.0f}')
    plt.legend()

    # Price by class
    plt.subplot(2, 2, 4)
    class_prices = df.groupby('class')['price'].mean()
    class_prices.plot(kind='bar', color=['orange', 'purple'])
    plt.title('Average Price by Class')
    plt.ylabel('Price ($)')
    plt.xticks(rotation=0)

    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    output_dir = 'static/images'
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'price_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"✅ Price analysis saved to '{output_path}'")

    # 2. ROUTE ANALYSIS
    print("\n🛫 ROUTE ANALYSIS")
    print("-" * 30)

    # Most popular routes
    route_counts = df.groupby(['source_city', 'destination_city']).size().sort_values(ascending=False)
    print("Top 10 Most Popular Routes:")
    for i, (route, count) in enumerate(route_counts.head(10).items(), 1):
        print(f"{i:2d}. {route[0]} → {route[1]}: {count:,} flights")

    # Route pricing analysis
    route_prices = df.groupby(['source_city', 'destination_city'])['price'].agg(['mean', 'count']).round(0)
    route_prices = route_prices.sort_values('mean', ascending=False)
    print(f"\nMost Expensive Routes (avg price):")
    for i, (route, data) in enumerate(route_prices.head(5).iterrows(), 1):
        print(f"{i}. {route[0]} → {route[1]}: ${data['mean']:,.0f} ({data['count']} flights)")

    # 3. TIME ANALYSIS
    print("\n⏰ TIME ANALYSIS")
    print("-" * 30)

    # Departure time preferences
    departure_time_counts = df['departure_time'].value_counts()
    print("Departure Time Preferences:")
    for time, count in departure_time_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {time}: {count:,} flights ({percentage:.1f}%)")

    # Price by departure time
    time_prices = df.groupby('departure_time')['price'].mean().sort_values(ascending=False)
    print(f"\nAverage Prices by Departure Time:")
    for time, price in time_prices.items():
        print(f"  {time}: ${price:,.0f}")

    # 4. BOOKING PATTERNS
    print("\n📅 BOOKING PATTERNS")
    print("-" * 30)

    # Days left analysis
    days_left_bins = pd.cut(df['days_left'], bins=[0, 7, 14, 30, 49], labels=['1-7 days', '8-14 days', '15-30 days', '31-49 days'])
    booking_patterns = df.groupby(days_left_bins)['price'].agg(['mean', 'count'])
    print("Price patterns by booking advance:")
    for period, data in booking_patterns.iterrows():
        print(f"  {period}: ${data['mean']:,.0f} avg price ({data['count']:,} bookings)")

    # 5. AIRLINE PERFORMANCE
    print("\n✈️ AIRLINE PERFORMANCE ANALYSIS")
    print("-" * 30)

    airline_stats = df.groupby('airline').agg({
        'price': ['mean', 'median', 'std'],
        'duration': 'mean',
        'flight': 'count'
    }).round(2)

    airline_stats.columns = ['avg_price', 'median_price', 'price_std', 'avg_duration', 'total_flights']
    airline_stats = airline_stats.sort_values('avg_price')

    print("Airline Performance Summary:")
    print(airline_stats)

    # 6. STOP ANALYSIS
    print("\n🛑 STOP ANALYSIS")
    print("-" * 30)

    stop_analysis = df.groupby('stops').agg({
        'price': ['mean', 'count'],
        'duration': 'mean'
    }).round(2)

    print("Impact of stops on price and duration:")
    for stops, data in stop_analysis.iterrows():
        print(f"  {stops} stops: ${data[('price', 'mean')]:,.0f} avg price, {data[('duration', 'mean')]:.1f} hours avg duration ({data[('price', 'count')]:,} flights)")

    # 7. BUSINESS INTELLIGENCE INSIGHTS
    print("\n💡 BUSINESS INTELLIGENCE INSIGHTS")
    print("-" * 30)

    # Price optimization opportunities
    expensive_routes = route_prices[route_prices['mean'] > route_prices['mean'].quantile(0.9)]
    print(f"High-value routes (top 10% by price): {len(expensive_routes)} routes")

    # Market share analysis
    market_share = df['airline'].value_counts(normalize=True) * 100
    print(f"\nMarket Share by Airline:")
    for airline, share in market_share.items():
        print(f"  {airline}: {share:.1f}%")

    # Revenue potential
    df['revenue_potential'] = df['price'] * (1 + (df['days_left'] < 7) * 0.2)  # 20% premium for last-minute
    revenue_by_airline = df.groupby('airline')['revenue_potential'].sum().sort_values(ascending=False)
    print(f"\nRevenue Potential by Airline:")
    for airline, revenue in revenue_by_airline.items():
        print(f"  {airline}: ${revenue:,.0f}")

    # 8. RECOMMENDATION ENGINE FEATURES
    print("\n🎯 RECOMMENDATION ENGINE FEATURES")
    print("-" * 30)

    # Best value flights (low price, reasonable duration)
    df['value_score'] = (df['price'].max() - df['price']) / df['price'].max() + (df['duration'].max() - df['duration']) / df['duration'].max()
    best_value = df.nlargest(5, 'value_score')[['airline', 'source_city', 'destination_city', 'price', 'duration', 'days_left']]
    print("Best Value Flights (low price + reasonable duration):")
    print(best_value)

    # 9. PREDICTIVE MODELING OPPORTUNITIES
    print("\n🔮 PREDICTIVE MODELING OPPORTUNITIES")
    print("-" * 30)
    print("This dataset is perfect for:")
    print("1. Price prediction models")
    print("2. Demand forecasting")
    print("3. Customer segmentation")
    print("4. Route optimization")
    print("5. Dynamic pricing strategies")
    print("6. Revenue optimization")
    print("7. Market trend analysis")

    # 10. DATA VISUALIZATION OPPORTUNITIES
    print("\n📈 DATA VISUALIZATION OPPORTUNITIES")
    print("-" * 30)
    print("Create interactive dashboards for:")
    print("1. Real-time price monitoring")
    print("2. Route performance metrics")
    print("3. Airline comparison tools")
    print("4. Booking trend analysis")
    print("5. Revenue forecasting charts")

    print("\n" + "="*60)
    print("🎉 ANALYSIS COMPLETE!")
    print("="*60)
    print("\nNext steps you could take:")
    print("1. Build a price prediction model")
    print("2. Create an interactive dashboard")
    print("3. Analyze seasonal patterns")
    print("4. Develop a recommendation system")
    print("5. Perform customer segmentation")
    print("6. Optimize pricing strategies")
    print("7. Forecast demand patterns")

if __name__ == "__main__":
    main() 