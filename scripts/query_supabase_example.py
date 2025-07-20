import sys
import pandas as pd
from supabase import create_client, Client

# Add config directory to path
sys.path.append('../config')
from supabase_config import SUPABASE_URL, SUPABASE_KEY

def create_supabase_client():
    """Initialize Supabase client."""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None

def get_amenities_by_category(supabase, category):
    """Get all amenities of a specific category."""
    try:
        result = supabase.table("amenities").select("*").eq("category", category).execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        print(f"Error fetching {category}s: {e}")
        return pd.DataFrame()

def get_amenities_by_suburb(supabase, suburb):
    """Get all amenities in a specific suburb."""
    try:
        result = supabase.table("amenities").select("*").eq("suburb", suburb).execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        print(f"Error fetching amenities for {suburb}: {e}")
        return pd.DataFrame()

def get_amenities_near_location(supabase, lat, lon, radius=0.01):
    """
    Get amenities near a specific location.
    radius: approximate distance in degrees (0.01 ~ 1km)
    """
    try:
        result = supabase.table("amenities").select("*").execute()
        df = pd.DataFrame(result.data)
        
        if not df.empty:
            # Calculate simple distance (not geographically accurate but fast)
            df['distance'] = abs(df['latitude'] - lat) + abs(df['longitude'] - lon)
            nearby = df[df['distance'] <= radius].sort_values('distance')
            return nearby
        return df
    except Exception as e:
        print(f"Error fetching nearby amenities: {e}")
        return pd.DataFrame()

def get_statistics(supabase):
    """Get general statistics about the amenities data."""
    try:
        # Get all data
        result = supabase.table("amenities").select("*").execute()
        df = pd.DataFrame(result.data)
        
        if df.empty:
            print("No data found in the database.")
            return
        
        print("=== AMENITIES DATABASE STATISTICS ===")
        print(f"Total amenities: {len(df)}")
        
        print(f"\nBy category:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
        
        print(f"\nTop 10 suburbs by amenity count:")
        suburb_counts = df['suburb'].value_counts().head(10)
        for suburb, count in suburb_counts.items():
            print(f"  {suburb}: {count}")
        
        return df
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return pd.DataFrame()

def main():
    """Example usage of the query functions."""
    
    print("=== SUPABASE AMENITIES QUERY EXAMPLES ===\n")
    
    # Initialize client
    supabase = create_supabase_client()
    if not supabase:
        print("Failed to connect to Supabase. Check your configuration.")
        return
    
    # Example 1: Get general statistics
    print("1. General Statistics:")
    stats_df = get_statistics(supabase)
    
    if stats_df.empty:
        print("No data available. Make sure you've uploaded your CSV first.")
        return
    
    # Example 2: Get all cafes
    print("\n2. All Cafes (first 5):")
    cafes = get_amenities_by_category(supabase, "cafe")
    if not cafes.empty:
        print(cafes[['name', 'suburb', 'latitude', 'longitude']].head())
    else:
        print("No cafes found.")
    
    # Example 3: Get amenities in a specific suburb
    print("\n3. Amenities in Carlton (first 5):")
    carlton_amenities = get_amenities_by_suburb(supabase, "Carlton")
    if not carlton_amenities.empty:
        print(carlton_amenities[['name', 'category', 'latitude', 'longitude']].head())
    else:
        print("No amenities found in Carlton.")
    
    # Example 4: Get amenities near Melbourne CBD
    print("\n4. Amenities near Melbourne CBD (-37.8136, 144.9631):")
    melbourne_lat, melbourne_lon = -37.8136, 144.9631
    nearby = get_amenities_near_location(supabase, melbourne_lat, melbourne_lon, radius=0.005)
    if not nearby.empty:
        print(nearby[['name', 'category', 'suburb', 'distance']].head())
    else:
        print("No amenities found near Melbourne CBD.")
    
    # Example 5: Custom query using SQL
    print("\n5. Custom Query - Suburbs with most supermarkets:")
    try:
        result = supabase.rpc('sql', {
            'query': '''
                SELECT suburb, COUNT(*) as supermarket_count
                FROM amenities 
                WHERE category = 'supermarket'
                GROUP BY suburb 
                ORDER BY supermarket_count DESC 
                LIMIT 5
            '''
        }).execute()
        
        if result.data:
            df_custom = pd.DataFrame(result.data)
            print(df_custom)
        else:
            print("Custom query returned no results.")
            
    except Exception as e:
        print(f"Custom query failed: {e}")
        print("Note: You might need to enable custom SQL functions in Supabase.")

if __name__ == "__main__":
    main() 