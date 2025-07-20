import pandas as pd
import sys
import os
import numpy as np
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

def process_and_upload_crime_data():
    """Process crime data and upload to Supabase."""
    
    print("=== PROCESSING AND UPLOADING CRIME DATA ===")
    
    # Load the CSV file
    file_path = "../data/raw/abs/Data_Tables_LGA_Recorded_Offences_Year_Ending_March_2025.csv"
    
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} total crime records")
        
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
        
        # Clean and prepare data for Supabase
        melbourne_crime = melbourne_crime.rename(columns={
            "Year": "year",
            "Year ending": "year_ending", 
            "Police Service Area": "police_service_area",
            "Local Government Area": "lga",
            "Offence Division": "offence_division",
            "Offence Subdivision": "offence_subdivision", 
            "Offence Subgroup": "offence_subgroup",
            "Offence Count": "offence_count",
            "PSA Rate per 100,000 population": "psa_rate_per_100k",
            "LGA Rate per 100,000 population": "lga_rate_per_100k"
        })
        
        # Fix data types properly
        print("Converting data types...")
        
        # Convert numeric columns to proper types
        melbourne_crime["offence_count"] = pd.to_numeric(melbourne_crime["offence_count"], errors="coerce")
        melbourne_crime["year"] = pd.to_numeric(melbourne_crime["year"], errors="coerce") 
        melbourne_crime["psa_rate_per_100k"] = pd.to_numeric(melbourne_crime["psa_rate_per_100k"], errors="coerce")
        melbourne_crime["lga_rate_per_100k"] = pd.to_numeric(melbourne_crime["lga_rate_per_100k"], errors="coerce")
        
        # Convert to proper integer types (fill NaN with 0 first for counts)
        melbourne_crime["offence_count"] = melbourne_crime["offence_count"].fillna(0).astype(int)
        melbourne_crime["year"] = melbourne_crime["year"].fillna(2025).astype(int)
        
        # Handle string columns
        melbourne_crime["year_ending"] = melbourne_crime["year_ending"].fillna("March")
        melbourne_crime["police_service_area"] = melbourne_crime["police_service_area"].fillna("Unknown")
        melbourne_crime["lga"] = melbourne_crime["lga"].fillna("Unknown")
        melbourne_crime["offence_division"] = melbourne_crime["offence_division"].fillna("Unknown")
        melbourne_crime["offence_subdivision"] = melbourne_crime["offence_subdivision"].fillna("Unknown") 
        melbourne_crime["offence_subgroup"] = melbourne_crime["offence_subgroup"].fillna("Unknown")
        
        # Handle float columns (replace NaN with None for nullable columns)
        melbourne_crime["psa_rate_per_100k"] = melbourne_crime["psa_rate_per_100k"].where(pd.notna(melbourne_crime["psa_rate_per_100k"]), None)
        melbourne_crime["lga_rate_per_100k"] = melbourne_crime["lga_rate_per_100k"].where(pd.notna(melbourne_crime["lga_rate_per_100k"]), None)
        
        # Remove rows with invalid data
        melbourne_crime = melbourne_crime[melbourne_crime["offence_count"] > 0]
        melbourne_crime = melbourne_crime[melbourne_crime["year"] > 2020]
        
        print(f"Cleaned data: {len(melbourne_crime)} records")
        
        # Convert to records and ensure clean serialization
        records = []
        for _, row in melbourne_crime.iterrows():
            record = {
                "year": int(row["year"]),
                "year_ending": str(row["year_ending"]),
                "police_service_area": str(row["police_service_area"]),
                "lga": str(row["lga"]),
                "offence_division": str(row["offence_division"]),
                "offence_subdivision": str(row["offence_subdivision"]),
                "offence_subgroup": str(row["offence_subgroup"]),
                "offence_count": int(row["offence_count"]),
                "psa_rate_per_100k": float(row["psa_rate_per_100k"]) if row["psa_rate_per_100k"] is not None else None,
                "lga_rate_per_100k": float(row["lga_rate_per_100k"]) if row["lga_rate_per_100k"] is not None else None
            }
            
            # Check for problematic values
            if not isinstance(record["offence_count"], int) or record["offence_count"] < 0:
                continue
            if not isinstance(record["year"], int) or record["year"] < 2020:
                continue
                
            records.append(record)
        
        print(f"Prepared {len(records)} clean records for upload")
        
        # Upload to Supabase
        supabase = create_supabase_client()
        if not supabase:
            print("Cannot connect to Supabase")
            return False
        
        # Upload in batches
        batch_size = 50  # Smaller batches to avoid issues
        total_uploaded = 0
        total_batches = (len(records) + batch_size - 1) // batch_size
        
        print(f"Uploading {len(records)} records in {total_batches} batches...")
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            try:
                print(f"Uploading batch {batch_num}/{total_batches}...")
                
                result = supabase.table("crime_data").insert(batch).execute()
                
                if result.data:
                    total_uploaded += len(batch)
                    print(f"  SUCCESS: Uploaded {len(batch)} records")
                else:
                    print(f"  FAILED: Batch {batch_num}")
                    
            except Exception as e:
                print(f"  ERROR: Batch {batch_num} - {str(e)[:100]}...")
                # Print first record in failed batch for debugging
                if len(batch) > 0:
                    print(f"    Sample record: {batch[0]}")
                continue
        
        print(f"\n=== UPLOAD COMPLETE ===")
        print(f"Total uploaded: {total_uploaded}/{len(records)}")
        print(f"Success rate: {(total_uploaded/len(records)*100):.1f}%")
        
        return total_uploaded > 0
        
    except Exception as e:
        print(f"Error processing crime data: {e}")
        return False

def create_safety_scores():
    """Create aggregated safety scores by LGA."""
    
    print(f"\n=== CREATING SAFETY SCORES ===")
    
    supabase = create_supabase_client()
    if not supabase:
        return
    
    try:
        # Get crime data from Supabase
        result = supabase.table("crime_data").select("*").execute()
        df = pd.DataFrame(result.data)
        
        if df.empty:
            print("No crime data found in Supabase")
            return
        
        print(f"Loaded {len(df)} crime records from Supabase")
        
        # Create safety score aggregations by LGA
        safety_scores = []
        
        for lga in df["lga"].unique():
            lga_data = df[df["lga"] == lga]
            
            # Calculate key safety metrics
            total_crimes = int(lga_data["offence_count"].sum())
            avg_rate_per_100k = float(lga_data["lga_rate_per_100k"].mean()) if not lga_data["lga_rate_per_100k"].isna().all() else 0.0
            
            # Count different crime types
            violent_crimes = int(lga_data[
                lga_data["offence_division"].str.contains("Crimes against the person", na=False)
            ]["offence_count"].sum())
            
            property_crimes = int(lga_data[
                lga_data["offence_division"].str.contains("Property and deception", na=False)
            ]["offence_count"].sum())
            
            # Calculate safety score (higher is safer)
            max_rate = float(df["lga_rate_per_100k"].max()) if not df["lga_rate_per_100k"].isna().all() else 1.0
            safety_score = max(0.0, 100.0 - (avg_rate_per_100k / max_rate * 100.0)) if max_rate > 0 else 50.0
            
            safety_category = (
                "High" if safety_score > 70 else 
                "Medium" if safety_score > 40 else 
                "Low"
            )
            
            safety_data = {
                "lga": str(lga),
                "total_crime_count": total_crimes,
                "avg_crime_rate_per_100k": round(avg_rate_per_100k, 2),
                "violent_crime_count": violent_crimes,
                "property_crime_count": property_crimes,
                "safety_score": round(safety_score, 1),
                "safety_category": safety_category,
                "year": 2025,
                "year_ending": "March"
            }
            
            safety_scores.append(safety_data)
        
        # Create DataFrame and save locally
        safety_df = pd.DataFrame(safety_scores)
        os.makedirs("../data/processed/safety", exist_ok=True)
        output_file = "../data/processed/safety/lga_safety_scores.csv"
        safety_df.to_csv(output_file, index=False)
        
        print(f"Safety scores saved to: {output_file}")
        
        # Upload to Supabase
        records = safety_df.to_dict("records")
        result = supabase.table("safety_scores").insert(records).execute()
        
        if result.data:
            print(f"SUCCESS: Uploaded {len(records)} safety score records to Supabase")
            
            # Show top results
            print(f"\nTop 5 safest LGAs:")
            top_safe = safety_df.nlargest(5, "safety_score")[["lga", "safety_score", "safety_category"]]
            print(top_safe.to_string(index=False))
            
            print(f"\nTop 5 highest crime rate LGAs:")
            top_crime = safety_df.nlargest(5, "avg_crime_rate_per_100k")[["lga", "avg_crime_rate_per_100k", "total_crime_count"]]
            print(top_crime.to_string(index=False))
            
        else:
            print("FAILED: Could not upload safety scores")
        
        return safety_df
        
    except Exception as e:
        print(f"Error creating safety scores: {e}")
        return None

def show_sql_instructions():
    """Show SQL table creation instructions."""
    
    print(f"\n" + "="*60)
    print("SUPABASE TABLE SETUP INSTRUCTIONS")
    print("="*60)
    print("1. Go to your Supabase SQL Editor")
    print("2. Run the SQL script: create_safety_tables.sql")
    print("3. This will create both crime_data and safety_scores tables")
    print("4. Then run this script again to upload the data")
    print("="*60)

if __name__ == "__main__":
    
    print("CRIME DATA UPLOADER FOR SUPABASE")
    print("=" * 50)
    
    # Test Supabase connection first
    supabase = create_supabase_client()
    if not supabase:
        print("Cannot connect to Supabase. Check your configuration.")
        exit(1)
    
    # Check if tables exist by trying to query them
    try:
        result = supabase.table("crime_data").select("count", count="exact").limit(1).execute()
        print(f"Tables exist. Current crime_data records: {result.count}")
        
        choice = input("\nDo you want to upload new data? This will add to existing data. (y/n): ")
        if choice.lower() != "y":
            print("Upload cancelled.")
            exit(0)
            
    except Exception as e:
        print("Tables do not exist or there was an error accessing them.")
        show_sql_instructions()
        
        choice = input("\nHave you created the tables in Supabase? (y/n): ")
        if choice.lower() != "y":
            print("Please create the tables first using create_safety_tables.sql")
            exit(0)
    
    # Process and upload crime data
    success = process_and_upload_crime_data()
    
    if success:
        print("\nCrime data uploaded successfully!")
        
        # Create and upload safety scores
        safety_df = create_safety_scores()
        
        if safety_df is not None:
            print(f"\nSafety analysis complete for {len(safety_df)} LGAs")
            print("\nYou can now use this data in your map visualizations!")
        
    else:
        print("Upload failed. Check the error messages above.") 