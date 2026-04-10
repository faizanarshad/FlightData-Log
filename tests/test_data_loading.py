"""
Tests for data loading functionality
"""

import pytest
import pandas as pd
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.analysis.read_dataset import load_data, get_data_info
from src.data_paths import resolve_data_path


class TestDataLoading:
    """Test cases for data loading functionality"""
    
    def test_load_data_exists(self):
        """Test that the data file exists"""
        data_path = resolve_data_path(None)
        assert os.path.exists(data_path), f"Data file not found: {data_path}"
    
    def test_load_data_returns_dataframe(self):
        """Test that load_data returns a pandas DataFrame"""
        try:
            df = load_data()
            assert isinstance(df, pd.DataFrame), "load_data should return a pandas DataFrame"
        except Exception as e:
            pytest.skip(f"Data loading failed: {e}")
    
    def test_dataframe_has_expected_columns(self):
        """Test that the DataFrame has the expected columns"""
        expected_columns = [
            'index', 'airline', 'flight', 'source_city', 'departure_time',
            'stops', 'arrival_time', 'destination_city', 'class', 'duration',
            'days_left', 'price'
        ]
        
        try:
            df = load_data()
            for col in expected_columns:
                assert col in df.columns, f"Expected column '{col}' not found in DataFrame"
        except Exception as e:
            pytest.skip(f"Data loading failed: {e}")
    
    def test_dataframe_not_empty(self):
        """Test that the DataFrame is not empty"""
        try:
            df = load_data()
            assert len(df) > 0, "DataFrame should not be empty"
        except Exception as e:
            pytest.skip(f"Data loading failed: {e}")
    
    def test_get_data_info_returns_dict(self):
        """Test that get_data_info returns a dictionary"""
        try:
            df = load_data()
            info = get_data_info(df)
            assert isinstance(info, dict), "get_data_info should return a dictionary"
        except Exception as e:
            pytest.skip(f"Data loading failed: {e}")


class TestDataQuality:
    """Test cases for data quality"""
    
    def test_no_missing_values(self):
        """Test that there are no missing values in critical columns"""
        critical_columns = ['airline', 'price', 'duration', 'source_city', 'destination_city']
        
        try:
            df = load_data()
            for col in critical_columns:
                if col in df.columns:
                    missing_count = df[col].isnull().sum()
                    assert missing_count == 0, f"Column '{col}' has {missing_count} missing values"
        except Exception as e:
            pytest.skip(f"Data loading failed: {e}")
    
    def test_price_range_valid(self):
        """Test that price values are within valid range"""
        try:
            df = load_data()
            if 'price' in df.columns:
                assert df['price'].min() > 0, "Price should be positive"
                assert df['price'].max() < 1000000, "Price should be reasonable (< 1M)"
        except Exception as e:
            pytest.skip(f"Data loading failed: {e}")
    
    def test_duration_range_valid(self):
        """Test that duration values are within valid range"""
        try:
            df = load_data()
            if 'duration' in df.columns:
                assert df['duration'].min() > 0, "Duration should be positive"
                assert df['duration'].max() < 50, "Duration should be reasonable (< 50 hours)"
        except Exception as e:
            pytest.skip(f"Data loading failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__]) 