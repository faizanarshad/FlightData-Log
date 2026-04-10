import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

from src.data_paths import resolve_data_path

def load_data(data_path=None):
    """Load the airlines dataset from the specified path or default location."""
    data_path = resolve_data_path(data_path)
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    print(f"Reading the airlines flights dataset from: {data_path}")
    df = pd.read_csv(data_path)
    return df

def get_data_info(df):
    """Get basic information about the dataset."""
    info = {
        'shape': df.shape,
        'columns': list(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'price_stats': {
            'min': df['price'].min(),
            'max': df['price'].max(),
            'mean': df['price'].mean(),
            'median': df['price'].median()
        }
    }
    return info

def main(data_path=None):
    """Main function to run the data analysis."""
    # Read the dataset
    df = load_data(data_path)

    # Basic information about the dataset
    print("\n" + "="*50)
    print("DATASET OVERVIEW")
    print("="*50)
    print(f"Dataset shape: {df.shape}")
    print(f"Number of rows: {df.shape[0]:,}")
    print(f"Number of columns: {df.shape[1]}")

    print("\n" + "="*50)
    print("COLUMN INFORMATION")
    print("="*50)
    print(df.info())

    print("\n" + "="*50)
    print("FIRST 10 ROWS")
    print("="*50)
    print(df.head(10))

    print("\n" + "="*50)
    print("BASIC STATISTICS")
    print("="*50)
    print(df.describe())

    print("\n" + "="*50)
    print("MISSING VALUES")
    print("="*50)
    missing_values = df.isnull().sum()
    print(missing_values[missing_values > 0] if missing_values.sum() > 0 else "No missing values found")

    print("\n" + "="*50)
    print("UNIQUE VALUES IN CATEGORICAL COLUMNS")
    print("="*50)
    categorical_columns = ['airline', 'source_city', 'destination_city', 'class', 'stops', 'departure_time', 'arrival_time']
    for col in categorical_columns:
        if col in df.columns:
            print(f"\n{col}:")
            print(f"  Unique values: {df[col].nunique()}")
            print(f"  Top 5 values: {df[col].value_counts().head().to_dict()}")

    print("\n" + "="*50)
    print("PRICE ANALYSIS")
    print("="*50)
    print(f"Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
    print(f"Average price: ${df['price'].mean():,.0f}")
    print(f"Median price: ${df['price'].median():,.0f}")

    print("\n" + "="*50)
    print("DURATION ANALYSIS")
    print("="*50)
    print(f"Duration range: {df['duration'].min():.2f} - {df['duration'].max():.2f} hours")
    print(f"Average duration: {df['duration'].mean():.2f} hours")
    print(f"Median duration: {df['duration'].median():.2f} hours")

    print("\n" + "="*50)
    print("DAYS LEFT ANALYSIS")
    print("="*50)
    print(f"Days left range: {df['days_left'].min()} - {df['days_left'].max()} days")
    print(f"Average days left: {df['days_left'].mean():.1f} days")
    print(f"Median days left: {df['days_left'].median():.1f} days")

    # Save summary to a file
    output_path = 'data/processed/dataset_summary.txt'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write("AIRLINES FLIGHTS DATASET SUMMARY\n")
        f.write("="*50 + "\n")
        f.write(f"Dataset shape: {df.shape}\n")
        f.write(f"Number of rows: {df.shape[0]:,}\n")
        f.write(f"Number of columns: {df.shape[1]}\n\n")
        
        f.write("COLUMNS:\n")
        for i, col in enumerate(df.columns, 1):
            f.write(f"{i}. {col}\n")
        
        f.write(f"\nPRICE STATISTICS:\n")
        f.write(f"Min: ${df['price'].min():,.0f}\n")
        f.write(f"Max: ${df['price'].max():,.0f}\n")
        f.write(f"Mean: ${df['price'].mean():,.0f}\n")
        f.write(f"Median: ${df['price'].median():,.0f}\n")

    print(f"\nDataset summary saved to '{output_path}'")
    print("\nDataset reading and analysis complete!")
    return df

if __name__ == "__main__":
    main() 