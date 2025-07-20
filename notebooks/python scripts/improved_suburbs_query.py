import requests
import sys
sys.path.append('../../src')
from data.supabase_loader import load_amenities_data, get_unique_suburbs

def get_all_melbourne_suburbs():
    """Get all suburbs in Melbourne using an improved query that includes ways and nodes."""
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    print("=== Getting all suburbs in Melbourne with improved query ===")
    
    # Expanded bounding box to include southeastern suburbs
    melbourne_bbox = "-38.3,144.28,-37.5,146"
    
    # IMPROVED query that includes relations, ways, AND nodes
    improved_query = f"""
    [out:json][timeout:180];
    (
      // Administrative boundary relations
      relation["admin_level"="10"]["boundary"="administrative"]({melbourne_bbox});
      relation["admin_level"="9"]["place"="suburb"]({melbourne_bbox});
      relation["place"="suburb"]({melbourne_bbox});
      
      // Ways tagged as suburbs
      way["place"="suburb"]({melbourne_bbox});
      
      // Nodes tagged as suburbs  
      node["place"="suburb"]({melbourne_bbox});
    );
    out tags;
    """
    
    print("Querying with improved structure (relations + ways + nodes)...")
    try:
        response = requests.get(overpass_url, params={'data': improved_query})
        response.raise_for_status()
        suburbs_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching suburbs: {e}")
        return []
    
    # Extract unique suburb names
    suburb_names = set()
    for element in suburbs_data['elements']:
        if 'tags' in element and 'name' in element['tags']:
            name = element['tags']['name']
            # Filter out non-Melbourne areas that might be in the bbox
            if any(exclude in name.lower() for exclude in ['geelong', 'ballarat', 'bendigo']):
                continue
            suburb_names.add(name)
    
    suburb_names = sorted(list(suburb_names))
    
    print(f"Found {len(suburb_names)} unique suburbs")
    
    # Check for our target suburbs
    target_suburbs = ['Clayton', 'Burwood East', 'Glen Waverley']
    print(f"\nChecking for previously missing suburbs:")
    all_found = True
    for suburb in target_suburbs:
        found = suburb in suburb_names
        print(f"  {suburb}: {'Found' if found else 'Missing'}")
        if not found:
            all_found = False
    
    if all_found:
        print("\nSUCCESS! All target suburbs now included!")
    else:
        print("\nSome suburbs still missing - may need further query refinement")
    
    return suburb_names

def compare_with_original():
    """Compare with the original amenities dataset."""
    import pandas as pd
    
    # Get current amenities suburbs from Supabase
    print("Loading amenities data from database...")
    df = load_amenities_data()
    if df.empty:
        print("No amenities data found in database")
        return
    
    current_suburbs = set(df['suburb'].unique())
    
    # Get improved suburbs list
    improved_suburbs = set(get_all_melbourne_suburbs())
    
    print(f"\n" + "="*60)
    print("COMPARISON WITH CURRENT AMENITIES DATASET")
    print("="*60)
    
    print(f"Current amenities dataset: {len(current_suburbs)} suburbs")
    print(f"Improved query results: {len(improved_suburbs)} suburbs")
    
    # Find new suburbs that would be added
    new_suburbs = improved_suburbs - current_suburbs
    missing_suburbs = current_suburbs - improved_suburbs
    
    print(f"\nNew suburbs that would be added: {len(new_suburbs)}")
    if new_suburbs:
        for suburb in sorted(new_suburbs):
            print(f"  + {suburb}")
    
    print(f"\nSuburbs in current dataset but not in improved query: {len(missing_suburbs)}")
    if missing_suburbs:
        for suburb in sorted(missing_suburbs):
            print(f"  - {suburb}")
    
    target_suburbs = ['Clayton', 'Burwood East', 'Glen Waverley']
    print(f"\nTarget suburbs status:")
    for suburb in target_suburbs:
        in_current = suburb in current_suburbs
        in_improved = suburb in improved_suburbs
        status = "Fixed" if (not in_current and in_improved) else "Already present" if in_current else "Still missing"
        print(f"  {suburb}: {status}")

if __name__ == "__main__":
    compare_with_original() 