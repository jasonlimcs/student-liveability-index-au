import pandas as pd
import os
import sys

# Add supabase loader
try:
    from .supabase_loader import load_amenities_data, load_demographics_data
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: Supabase loader not available, falling back to CSV only")

def load_csv(filepath):
    """Load data from CSV file."""
    return pd.read_csv(filepath)

def save_csv(df, filepath):
    """Save DataFrame to CSV file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)

def load_amenities(use_supabase=True):
    """
    Load amenities data from Supabase (preferred) or CSV fallback.
    
    Args:
        use_supabase (bool): Whether to try Supabase first
    
    Returns:
        pd.DataFrame: Amenities data
    """
    if use_supabase and SUPABASE_AVAILABLE:
        try:
            return load_amenities_data()
        except Exception as e:
            print(f"Supabase failed, falling back to CSV: {e}")
    
    # Fallback to CSV
    csv_files = [
        "data/processed/melbourne_amenities_improved_20250718_175145_cleaned_20250718_191258.csv",
        "data/processed/melbourne_amenities_improved_20250718_175145.csv",
        "data/processed/melbourne_amenities_20250717_170324.csv"
    ]
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            print(f"Loaded amenities from CSV: {csv_file}")
            return df
        except FileNotFoundError:
            continue
    
    print("No amenities data found")
    return pd.DataFrame()

def load_demographics(use_supabase=False):
    """
    Load demographics data (currently CSV only).
    
    Args:
        use_supabase (bool): Whether to try Supabase (not implemented yet)
    
    Returns:
        pd.DataFrame: Demographics data
    """
    if use_supabase and SUPABASE_AVAILABLE:
        try:
            return load_demographics_data()
        except Exception as e:
            print(f"Supabase demographics failed, falling back to CSV: {e}")
    
    # Load from CSV
    try:
        return pd.read_csv("data/processed/abs_demographics_merged.csv")
    except FileNotFoundError:
        print("Demographics CSV not found")
        return pd.DataFrame()