import pandas as pd
import sys
import os

# Add paths
sys.path.append("../config")
from supabase_config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

def load_safety_data():
    """Load safety scores from Supabase."""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Load safety scores
        result = supabase.table("safety_scores").select("*").execute()
        safety_df = pd.DataFrame(result.data)
        
        if not safety_df.empty:
            print(f"SUCCESS: Loaded {len(safety_df)} safety score records")
            return safety_df
        else:
            print("No safety data found in Supabase")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error loading safety data: {e}")
        return pd.DataFrame()

def load_detailed_crime_data(lga_filter=None):
    """Load detailed crime data from Supabase."""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Build query
        query = supabase.table("crime_data").select("*")
        
        if lga_filter:
            query = query.eq("lga", lga_filter)
        
        result = query.execute()
        crime_df = pd.DataFrame(result.data)
        
        if not crime_df.empty:
            print(f"SUCCESS: Loaded {len(crime_df)} crime records")
            return crime_df
        else:
            print("No crime data found")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error loading crime data: {e}")
        return pd.DataFrame()

def get_suburb_safety_mapping():
    """Create a mapping from suburbs to LGA safety scores."""
    
    # Load safety data
    safety_df = load_safety_data()
    if safety_df.empty:
        return {}
    
    # Load amenities to get suburbs
    sys.path.append("../src")
    from data.supabase_loader import load_amenities_data
    
    amenities_df = load_amenities_data()
    if amenities_df.empty:
        return {}
    
    # Create suburb to LGA mapping
    # This is a simplified mapping - you can enhance it with official data
    suburb_lga_mapping = {
        # Melbourne LGA
        "Melbourne": "Melbourne", "Carlton": "Melbourne", "Southbank": "Melbourne",
        "Docklands": "Melbourne", "East Melbourne": "Melbourne",
        
        # Yarra LGA  
        "Richmond": "Yarra", "Fitzroy": "Yarra", "Collingwood": "Yarra",
        "Abbotsford": "Yarra", "Cremorne": "Yarra",
        
        # Port Phillip LGA
        "St Kilda": "Port Phillip", "South Melbourne": "Port Phillip",
        "Albert Park": "Port Phillip", "Middle Park": "Port Phillip",
        
        # Stonnington LGA
        "South Yarra": "Stonnington", "Toorak": "Stonnington", 
        "Prahran": "Stonnington", "Armadale": "Stonnington",
        
        # Monash LGA
        "Clayton": "Monash", "Glen Waverley": "Monash", "Mount Waverley": "Monash",
        
        # Add more mappings as needed...
    }
    
    # Create suburb safety data
    suburb_safety = {}
    
    for suburb in amenities_df["suburb"].unique():
        lga = suburb_lga_mapping.get(suburb)
        
        if lga:
            lga_safety = safety_df[safety_df["lga"] == lga]
            if not lga_safety.empty:
                safety_info = lga_safety.iloc[0]
                suburb_safety[suburb] = {
                    "safety_score": safety_info["safety_score"],
                    "safety_category": safety_info["safety_category"],
                    "total_crime_count": safety_info["total_crime_count"],
                    "crime_rate_per_100k": safety_info["avg_crime_rate_per_100k"],
                    "violent_crime_count": safety_info["violent_crime_count"],
                    "property_crime_count": safety_info["property_crime_count"],
                    "lga": lga
                }
    
    print(f"Created safety mapping for {len(suburb_safety)} suburbs")
    return suburb_safety

def test_safety_data():
    """Test loading and displaying safety data."""
    
    print("=== TESTING SAFETY DATA LOADING ===")
    
    # Test safety scores
    safety_df = load_safety_data()
    if not safety_df.empty:
        print(f"\nTop 5 safest LGAs:")
        top_safe = safety_df.nlargest(5, "safety_score")[["lga", "safety_score", "safety_category"]]
        print(top_safe.to_string(index=False))
        
        print(f"\nTop 5 highest crime LGAs:")
        top_crime = safety_df.nlargest(5, "avg_crime_rate_per_100k")[["lga", "avg_crime_rate_per_100k", "total_crime_count"]]
        print(top_crime.to_string(index=False))
    
    # Test suburb mapping
    suburb_safety = get_suburb_safety_mapping()
    if suburb_safety:
        print(f"\nSample suburb safety data:")
        for suburb, data in list(suburb_safety.items())[:5]:
            print(f"  {suburb}: {data['safety_category']} safety (score: {data['safety_score']})")
    
    return safety_df, suburb_safety

if __name__ == "__main__":
    safety_df, suburb_safety = test_safety_data()
    
    # Save suburb safety mapping for use in visualization
    if suburb_safety:
        suburb_safety_df = pd.DataFrame.from_dict(suburb_safety, orient="index")
        suburb_safety_df.reset_index(inplace=True)
        suburb_safety_df.rename(columns={"index": "suburb"}, inplace=True)
        
        os.makedirs("../data/processed/safety", exist_ok=True)
        suburb_safety_df.to_csv("../data/processed/safety/suburb_safety_mapping.csv", index=False)
        print(f"\nSaved suburb safety mapping to: ../data/processed/safety/suburb_safety_mapping.csv")

