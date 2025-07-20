#!/usr/bin/env python3
"""
Test script to verify Supabase integration is working correctly.
Run this after uploading your data to Supabase to ensure all modules can access it.
"""

import sys
import pandas as pd

def test_supabase_loader():
    """Test the core Supabase data loader."""
    print("=== Testing Supabase Data Loader ===")
    
    try:
        sys.path.append('../src')
        from data.supabase_loader import SupabaseDataLoader, load_amenities_data
        
        # Test connection
        loader = SupabaseDataLoader()
        if not loader.test_connection():
            print("FAILED: Cannot connect to Supabase")
            return False
        
        # Test data loading
        df = load_amenities_data()
        if df.empty:
            print("FAILED: No data found in Supabase")
            return False
        
        print(f"SUCCESS: Loaded {len(df)} amenity records")
        print(f"Columns: {list(df.columns)}")
        print(f"Categories: {df['category'].value_counts().to_dict()}")
        
        return True
        
    except ImportError as e:
        print(f"FAILED: Import error - {e}")
        return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_generic_loader():
    """Test the generic data loader with Supabase fallback."""
    print("\n=== Testing Generic Data Loader ===")
    
    try:
        sys.path.append('../src')
        from data.load_data import load_amenities, load_demographics
        
        # Test amenities loading (should use Supabase)
        df_amenities = load_amenities(use_supabase=True)
        if df_amenities.empty:
            print("FAILED: No amenities data loaded")
            return False
        
        print(f"SUCCESS: Generic loader loaded {len(df_amenities)} amenities from Supabase")
        
        # Test demographics loading (CSV fallback)
        df_demographics = load_demographics(use_supabase=False)
        if not df_demographics.empty:
            print(f"SUCCESS: Loaded {len(df_demographics)} demographic records from CSV")
        else:
            print("WARNING: No demographics data found (this is okay if CSV doesn't exist)")
        
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_visualization_compatibility():
    """Test that visualization scripts can load data."""
    print("\n=== Testing Visualization Compatibility ===")
    
    try:
        # Test the updated visualization functions
        sys.path.append('../src')
        from data.supabase_loader import load_amenities_data, load_demographics_data
        
        amenities = load_amenities_data()
        demographics = load_demographics_data()
        
        print(f"SUCCESS: Visualization can load {len(amenities)} amenities and {len(demographics)} demographics")
        
        # Check required columns exist
        required_amenity_cols = ['suburb', 'category', 'name', 'lat', 'lon']
        missing_cols = [col for col in required_amenity_cols if col not in amenities.columns]
        
        if missing_cols:
            print(f"WARNING: Missing columns in amenities data: {missing_cols}")
        else:
            print("SUCCESS: All required amenity columns present")
        
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_data_quality():
    """Basic data quality checks."""
    print("\n=== Testing Data Quality ===")
    
    try:
        sys.path.append('../src')
        from data.supabase_loader import load_amenities_data
        
        df = load_amenities_data()
        
        # Check for missing values
        missing_data = df.isnull().sum()
        print("Missing values per column:")
        for col, missing in missing_data.items():
            if missing > 0:
                print(f"  {col}: {missing}")
        
        # Check coordinate ranges (should be Melbourne area)
        lat_range = (df['lat'].min(), df['lat'].max())
        lon_range = (df['lon'].min(), df['lon'].max())
        
        # Melbourne roughly: lat -38.5 to -37.3, lon 144.0 to 145.5
        if not (-38.5 <= lat_range[0] <= -37.3 and -38.5 <= lat_range[1] <= -37.3):
            print(f"WARNING: Latitude range seems wrong: {lat_range}")
        
        if not (144.0 <= lon_range[0] <= 145.5 and 144.0 <= lon_range[1] <= 145.5):
            print(f"WARNING: Longitude range seems wrong: {lon_range}")
        
        print(f"Coordinate ranges: lat {lat_range}, lon {lon_range}")
        print(f"Unique suburbs: {df['suburb'].nunique()}")
        print(f"Unique categories: {df['category'].nunique()}")
        
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def main():
    """Run all tests."""
    print("SUPABASE INTEGRATION TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_supabase_loader,
        test_generic_loader,
        test_visualization_compatibility,
        test_data_quality
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"TEST CRASHED: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("SUCCESS: ALL TESTS PASSED! Supabase integration is working correctly.")
        print("\nYou can now:")
        print("- Run visualize_amenities_with_boundaries.py to create maps")
        print("- Use clean_duplicate_amenities.py with Supabase data")
        print("- Access your data programmatically via the Supabase API")
    else:
        print("FAILED: Some tests failed. Check the errors above.")
        print("\nCommon issues:")
        print("- Make sure you've uploaded data: python upload_to_supabase.py your_file.csv")
        print("- Check your Supabase credentials in config/supabase_config.py")
        print("- Ensure you've installed dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 