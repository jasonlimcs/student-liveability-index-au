import pandas as pd
import sys
import os
from datetime import datetime

# Add config and src paths
sys.path.append("../config")
sys.path.append("../src")

from supabase_config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

def create_supabase_client():
    """Initialize Supabase client."""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None

def process_crime_data():
    """Process the CSA crime data CSV and prepare for Supabase upload."""
    
    print("=== PROCESSING CRIME DATA ===")
    
    # Load the CSV file
    file_path = "../data/raw/abs/Data_Tables_LGA_Recorded_Offences_Year_Ending_March_2025.csv"
    
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} crime records")
        
        # Show data overview
        print(f"Columns: {df.columns.tolist()}")
        print(f"Date range: {df['Year ending'].unique()}")
        print(f"LGAs: {len(df['Local Government Area'].unique())} unique areas")
        
        # Filter for Melbourne metropolitan LGAs
        melbourne_lgas = [
            "Melbourne", "Port Phillip", "Yarra", "Stonnington", "Glen Eira",
            "Bayside", "Kingston", "Monash", "Whitehorse", "Manningham",
            "Boroondara", "Darebin", "Banyule", "Nillumbik", "Whittlesea",
            "Hume", "Moreland", "Moonee Valley", "Maribyrnong", "Hobsons Bay",
            "Wyndham", "Melton", "Brimbank", "Maroondah", "Knox", "Cardinia",
            "Casey", "Frankston", "Mornington Peninsula"
        ]
        
        # Filter data for Melbourne LGAs
        melbourne_crime = df[df["Local Government Area"].isin(melbourne_lgas)].copy()
        print(f"Melbourne crime records: {len(melbourne_crime)}")
        
        return melbourne_crime
        
    except Exception as e:
        print(f"Error processing crime data: {e}")
        return None

if __name__ == "__main__":
    # Test the data processing
    crime_df = process_crime_data()
    
    if crime_df is not None:
        print(f"\nSample data:")
        print(crime_df.head())
        
        print(f"\nCrime types:")
        print(crime_df["Offence Division"].value_counts())
        
        print(f"\nMelbourne LGAs in data:")
        print(crime_df["Local Government Area"].value_counts())

