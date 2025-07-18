import requests
import time
import pandas as pd
from datetime import datetime

overpass_url = "http://overpass-api.de/api/interpreter"

def get_amenities_in_suburb(suburb_element, amenity_type="supermarket"):
    """
    Get amenities in a suburb using the most appropriate method based on element type.
    """
    suburb_name = suburb_element['tags'].get('name', 'Unnamed')
    elem_type = suburb_element['type']
    elem_id = suburb_element['id']
    
    amenities = []
    
    # METHOD 1: Try area query for relations (most accurate)
    if elem_type == 'relation':
        area_id = 3600000000 + elem_id
        
        area_query = f"""
        [out:json][timeout:30];
        area({area_id});
        (
          node["shop"="{amenity_type}"](area);
          way["shop"="{amenity_type}"](area);
          relation["shop"="{amenity_type}"](area);
        );
        out center;
        """
        
        try:
            response = requests.get(overpass_url, params={'data': area_query})
            response.raise_for_status()
            area_result = response.json()
            
            if area_result['elements']:
                for element in area_result['elements']:
                    name = element['tags'].get('name', f'Unnamed {amenity_type}')
                    if 'center' in element:
                        lat, lon = element['center']['lat'], element['center']['lon']
                    else:
                        lat, lon = element['lat'], element['lon']
                    
                    amenities.append({
                        'suburb': suburb_name,
                        'category': amenity_type,
                        'name': name,
                        'lat': lat,
                        'lon': lon
                    })
                
                print(f"  Area query: Found {len(amenities)} {amenity_type}s")
                return amenities
                
        except Exception as e:
            print(f"  Area query failed: {e}")
    
    # METHOD 2: Fallback to bounding box query (works for all element types)
    print(f"  Using bounding box approach...")
    
    # Get coordinates for the suburb
    if elem_type == 'node':
        center_lat = suburb_element['lat']
        center_lon = suburb_element['lon']
    elif 'center' in suburb_element:
        center_lat = suburb_element['center']['lat']
        center_lon = suburb_element['center']['lon']
    else:
        print(f"  No coordinates available for {suburb_name}")
        return amenities
    
    # Create bounding box around suburb center
    # Adjust margin based on suburb type (larger for bigger areas)
    margin = 0.02 if elem_type == 'relation' else 0.015  # ~2km for relations, ~1.5km for nodes/ways
    bbox = f"{center_lat - margin},{center_lon - margin},{center_lat + margin},{center_lon + margin}"
    
    bbox_query = f"""
    [out:json][timeout:30];
    (
      node["shop"="{amenity_type}"]({bbox});
      way["shop"="{amenity_type}"]({bbox});
      relation["shop"="{amenity_type}"]({bbox});
    );
    out center;
    """
    
    try:
        response = requests.get(overpass_url, params={'data': bbox_query})
        response.raise_for_status()
        bbox_result = response.json()
        
        for element in bbox_result['elements']:
            name = element['tags'].get('name', f'Unnamed {amenity_type}')
            if 'center' in element:
                lat, lon = element['center']['lat'], element['center']['lon']
            else:
                lat, lon = element['lat'], element['lon']
            
            amenities.append({
                'suburb': suburb_name,
                'category': amenity_type,
                'name': name,
                'lat': lat,
                'lon': lon
            })
        
        print(f"  Bounding box: Found {len(amenities)} {amenity_type}s")
        
    except Exception as e:
        print(f"  Bounding box query failed: {e}")
    
    return amenities

def extract_all_amenities():
    """Extract all amenities for Melbourne suburbs with the improved approach."""
    
    print("=== IMPROVED Melbourne Amenities Extraction ===")
    
    # Get all suburbs using the improved query
    melbourne_bbox = "-38.2255,144.18,-37.5,145.375"
    
    suburb_query = f"""
    [out:json][timeout:180];
    (
      relation["admin_level"="10"]["boundary"="administrative"]({melbourne_bbox});
      relation["admin_level"="9"]["place"="suburb"]({melbourne_bbox});
      relation["place"="suburb"]({melbourne_bbox});
      way["place"="suburb"]({melbourne_bbox});
      node["place"="suburb"]({melbourne_bbox});
    );
    out ids tags center;
    """
    
    print("Step 1: Getting all Melbourne suburbs...")
    try:
        response = requests.get(overpass_url, params={'data': suburb_query})
        response.raise_for_status()
        suburbs_data = response.json()
    except Exception as e:
        print(f"Error fetching suburbs: {e}")
        return
    
    print(f"Found {len(suburbs_data['elements'])} suburb elements")
    
    # Remove duplicates by name
    unique_suburbs = {}
    for elem in suburbs_data['elements']:
        name = elem['tags'].get('name')
        if name and name not in unique_suburbs:
            unique_suburbs[name] = elem
    
    print(f"Unique suburbs: {len(unique_suburbs)}")
    
    # Extract amenities for each category
    amenity_categories = {
        'supermarket': 'supermarket',
        'cafe': 'cafe', 
        'gym': 'fitness_centre',
        'library': 'library'
    }
    
    all_amenities = []
    total_suburbs = len(unique_suburbs)
    
    for i, (suburb_name, suburb_elem) in enumerate(unique_suburbs.items()):
        print(f"\n[{i+1}/{total_suburbs}] Processing {suburb_name}...")
        
        for category_name, osm_tag in amenity_categories.items():
            print(f"  Fetching {category_name}s...")
            
            if category_name == 'cafe':
                # Cafes use amenity tag instead of shop tag
                amenities = get_amenities_in_suburb_cafe(suburb_elem)
            elif category_name == 'gym':
                # Gyms use leisure tag
                amenities = get_amenities_in_suburb_gym(suburb_elem)
            elif category_name == 'library':
                # Libraries use amenity tag
                amenities = get_amenities_in_suburb_library(suburb_elem)
            else:
                # Supermarkets use shop tag
                amenities = get_amenities_in_suburb(suburb_elem, osm_tag)
            
            all_amenities.extend(amenities)
            
            if amenities:
                for amenity in amenities[:3]:  # Show first 3
                    print(f"    Found: {amenity['name']}")
        
        # Be polite to the API
        time.sleep(0.5)
    
    # Save results
    if all_amenities:
        df = pd.DataFrame(all_amenities)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/processed/melbourne_amenities_improved_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        print(f"\n=== EXTRACTION COMPLETE ===")
        print(f"Total amenities extracted: {len(all_amenities)}")
        print(f"Saved to: {filename}")
        
        # Summary by category
        print(f"\nBreakdown by category:")
        for category in df['category'].value_counts().items():
            print(f"  {category[0]}: {category[1]}")
        
        # Summary by suburb (top 10)
        print(f"\nTop 10 suburbs by amenity count:")
        top_suburbs = df['suburb'].value_counts().head(10)
        for suburb, count in top_suburbs.items():
            print(f"  {suburb}: {count}")
            
    else:
        print("No amenities found!")

def get_amenities_in_suburb_cafe(suburb_element):
    """Get cafes using amenity=cafe tag."""
    return get_amenities_with_tag(suburb_element, "amenity", "cafe", "cafe")

def get_amenities_in_suburb_gym(suburb_element):
    """Get gyms using leisure=fitness_centre tag."""
    return get_amenities_with_tag(suburb_element, "leisure", "fitness_centre", "gym")

def get_amenities_in_suburb_library(suburb_element):
    """Get libraries using amenity=library tag."""
    return get_amenities_with_tag(suburb_element, "amenity", "library", "library")

def get_amenities_with_tag(suburb_element, tag_key, tag_value, category_name):
    """Generic function to get amenities with specific tag."""
    suburb_name = suburb_element['tags'].get('name', 'Unnamed')
    elem_type = suburb_element['type']
    elem_id = suburb_element['id']
    
    amenities = []
    
    # Try area query for relations first
    if elem_type == 'relation':
        area_id = 3600000000 + elem_id
        
        area_query = f"""
        [out:json][timeout:30];
        area({area_id});
        (
          node["{tag_key}"="{tag_value}"](area);
          way["{tag_key}"="{tag_value}"](area);
          relation["{tag_key}"="{tag_value}"](area);
        );
        out center;
        """
        
        try:
            response = requests.get(overpass_url, params={'data': area_query})
            response.raise_for_status()
            area_result = response.json()
            
            if area_result['elements']:
                for element in area_result['elements']:
                    name = element['tags'].get('name', f'Unnamed {category_name}')
                    if 'center' in element:
                        lat, lon = element['center']['lat'], element['center']['lon']
                    else:
                        lat, lon = element['lat'], element['lon']
                    
                    amenities.append({
                        'suburb': suburb_name,
                        'category': category_name,
                        'name': name,
                        'lat': lat,
                        'lon': lon
                    })
                
                print(f"    Area query: Found {len(amenities)} {category_name}s")
                return amenities
                
        except Exception as e:
            print(f"    Area query failed, trying bounding box...")
    
    # Fallback to bounding box
    if elem_type == 'node':
        center_lat = suburb_element['lat']
        center_lon = suburb_element['lon']
    elif 'center' in suburb_element:
        center_lat = suburb_element['center']['lat']
        center_lon = suburb_element['center']['lon']
    else:
        return amenities
    
    margin = 0.02 if elem_type == 'relation' else 0.015
    bbox = f"{center_lat - margin},{center_lon - margin},{center_lat + margin},{center_lon + margin}"
    
    bbox_query = f"""
    [out:json][timeout:30];
    (
      node["{tag_key}"="{tag_value}"]({bbox});
      way["{tag_key}"="{tag_value}"]({bbox});
      relation["{tag_key}"="{tag_value}"]({bbox});
    );
    out center;
    """
    
    try:
        response = requests.get(overpass_url, params={'data': bbox_query})
        response.raise_for_status()
        bbox_result = response.json()
        
        for element in bbox_result['elements']:
            name = element['tags'].get('name', f'Unnamed {category_name}')
            if 'center' in element:
                lat, lon = element['center']['lat'], element['center']['lon']
            else:
                lat, lon = element['lat'], element['lon']
            
            amenities.append({
                'suburb': suburb_name,
                'category': category_name,
                'name': name,
                'lat': lat,
                'lon': lon
            })
        
        print(f"    Bounding box: Found {len(amenities)} {category_name}s")
        
    except Exception as e:
        print(f"    Query failed: {e}")
    
    return amenities

if __name__ == "__main__":
    extract_all_amenities() 