#!/usr/bin/env python3
"""
Script to prepare and validate data for the Melbourne Student Liveability Dashboard.
This script ensures that the CSV files are properly formatted and accessible.
"""

import pandas as pd
import os
import sys
from pathlib import Path

def validate_amenities_data(file_path):
    """Validate and prepare amenities data."""
    try:
        df = pd.read_csv(file_path)
        print(f"✓ Amenities data loaded: {len(df)} records")
        
        # Check for required columns
        required_columns = ['name', 'category', 'latitude', 'longitude']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"⚠ Warning: Missing columns in amenities data: {missing_columns}")
        else:
            print("✓ All required columns present in amenities data")
        
        # Count amenities by category
        category_counts = df['category'].value_counts()
        print("\nAmenities by category:")
        for category, count in category_counts.head(10).items():
            print(f"  {category}: {count}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading amenities data: {e}")
        return False

def validate_demographics_data(file_path):
    """Validate and prepare demographics data."""
    try:
        df = pd.read_csv(file_path)
        print(f"✓ Demographics data loaded: {len(df)} records")
        
        # Check for required columns
        required_columns = ['suburb', 'population']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"⚠ Warning: Missing columns in demographics data: {missing_columns}")
            # Show available columns
            print(f"Available columns: {list(df.columns)}")
        else:
            print("✓ All required columns present in demographics data")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading demographics data: {e}")
        return False

def check_map_files():
    """Check if HTML map files exist."""
    output_dir = Path("output")
    map_files = [
        "melbourne_amenities_map.html",
        "melbourne_combined_map.html"
    ]
    
    print("\nChecking map files:")
    for map_file in map_files:
        file_path = output_dir / map_file
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✓ {map_file}: {size_mb:.1f} MB")
        else:
            print(f"✗ {map_file}: Not found")

def main():
    """Main function to validate all dashboard data."""
    print("Melbourne Student Liveability Dashboard - Data Validation")
    print("=" * 60)
    
    # Check amenities data
    amenities_file = "data/processed/melbourne_amenities_improved_20250718_175145_cleaned_20250718_191258.csv"
    print(f"\nValidating amenities data: {amenities_file}")
    amenities_ok = validate_amenities_data(amenities_file)
    
    # Check demographics data
    demographics_file = "data/processed/abs_demographics_merged.csv"
    print(f"\nValidating demographics data: {demographics_file}")
    demographics_ok = validate_demographics_data(demographics_file)
    
    # Check map files
    check_map_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY:")
    print(f"✓ Amenities data: {'OK' if amenities_ok else 'FAILED'}")
    print(f"✓ Demographics data: {'OK' if demographics_ok else 'FAILED'}")
    
    if amenities_ok and demographics_ok:
        print("\n🎉 All data validation passed! Dashboard should work correctly.")
        print("\nNext steps:")
        print("1. Run 'npm run dev' to start the development server")
        print("2. Open http://localhost:3000 in your browser")
        print("3. Navigate through the dashboard tabs to view maps and statistics")
    else:
        print("\n❌ Some data validation failed. Please check the data files.")
        sys.exit(1)

if __name__ == "__main__":
    main() 