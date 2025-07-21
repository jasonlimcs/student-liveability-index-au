import pandas as pd
import sys
import os
sys.path.append("config")

from supabase_config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

def get_all_crime_data():
    """Get all crime data using pagination."""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    all_records = []
    page_size = 1000
    offset = 0
    
    print("Fetching all crime data using pagination...")
    
    while True:
        print(f"Fetching records {offset} to {offset + page_size}...")
        
        result = supabase.table("crime_data").select("*").range(offset, offset + page_size - 1).execute()
        
        if not result.data or len(result.data) == 0:
            break
            
        all_records.extend(result.data)
        offset += page_size
        
        if len(result.data) < page_size:
            break
    
    print(f"Total records fetched: {len(all_records)}")
    return all_records

def create_safety_scores_for_existing_lgas():
    """Create safety scores for LGAs that are currently in the database."""
    
    print("=== CREATING SAFETY SCORES FOR ALL LGAs ===")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Clear existing safety scores first
        print("Clearing existing safety scores...")
        supabase.table("safety_scores").delete().neq("id", 0).execute()
        
        # Get all crime data from Supabase using pagination
        all_data = get_all_crime_data()
        df = pd.DataFrame(all_data)
        
        if df.empty:
            print("No crime data found in Supabase")
            return
        
        print(f"Loaded {len(df)} crime records from Supabase")
        print(f"LGAs in database: {sorted(df['lga'].unique())}")
        
        # Create safety score aggregations by LGA
        safety_scores = []
        
        for lga in df["lga"].unique():
            lga_data = df[df["lga"] == lga]
            
            # Calculate key safety metrics
            total_crimes = int(lga_data["offence_count"].sum())
            
            # Handle missing lga_rate_per_100k values more carefully
            lga_rates = pd.to_numeric(lga_data["lga_rate_per_100k"], errors="coerce")
            avg_rate_per_100k = float(lga_rates.mean()) if not lga_rates.isna().all() else 0.0
            
            # Count different crime types
            violent_crimes = int(lga_data[
                lga_data["offence_division"].str.contains("Crimes against the person", na=False)
            ]["offence_count"].sum())
            
            property_crimes = int(lga_data[
                lga_data["offence_division"].str.contains("Property and deception", na=False)
            ]["offence_count"].sum())

            drug_offences = int(lga_data[
                lga_data["offence_division"].str.contains("Drug offences", na=False)
            ]["offence_count"].sum())

            public_order_offences = int(lga_data[
                lga_data["offence_division"].str.contains("Public order and security offences", na=False)
            ]["offence_count"].sum())

            justice_procedures_offences = int(lga_data[
                lga_data["offence_division"].str.contains("Justice procedures offences", na=False)
            ]["offence_count"].sum())
            
            # Calculate safety score (higher is safer)
            all_rates = pd.to_numeric(df["lga_rate_per_100k"], errors="coerce")
            max_rate = float(all_rates.max()) if not all_rates.isna().all() else 1.0
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
                "drug_offence_count": drug_offences,
                "public_order_offence_count": public_order_offences,
                "justice_procedures_offence_count": justice_procedures_offences,
                "safety_score": round(safety_score, 1),
                "safety_category": safety_category,
                "year": 2025,
                "year_ending": "March"
            }
            
            safety_scores.append(safety_data)
            
            print(f"  {lga}: {total_crimes} crimes, {safety_score:.1f} safety score, {safety_category} safety")
        
        # Create DataFrame and save locally
        safety_df = pd.DataFrame(safety_scores)
        os.makedirs("../data/processed/safety", exist_ok=True)
        output_file = "../data/processed/safety/lga_safety_scores.csv"
        safety_df.to_csv(output_file, index=False)
        
        print(f"\nSafety scores saved to: {output_file}")
        
        # Upload to Supabase
        records = safety_df.to_dict("records")
        result = supabase.table("safety_scores").insert(records).execute()
        
        if result.data:
            print(f"SUCCESS: Uploaded {len(records)} safety score records to Supabase")
            
            # Show results
            print(f"\nTop 5 safest LGAs:")
            top_safe = safety_df.nlargest(5, "safety_score")[["lga", "safety_score", "safety_category"]]
            print(top_safe.to_string(index=False))
            
            print(f"\nTop 5 highest crime rate LGAs:")
            top_crime = safety_df.nlargest(5, "avg_crime_rate_per_100k")[["lga", "avg_crime_rate_per_100k", "total_crime_count"]]
            print(top_crime.to_string(index=False))
            
            print(f"\nSafety score distribution:")
            print(safety_df["safety_category"].value_counts())
            
        else:
            print("FAILED: Could not upload safety scores")
        
        return safety_df
        
    except Exception as e:
        print(f"Error creating safety scores: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_safety_scores_for_existing_lgas() 