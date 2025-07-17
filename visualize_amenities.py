import pandas as pd
import folium
from folium import plugins
import numpy as np

def create_amenities_map():
    """Create an interactive folium map showing Melbourne amenities by category."""
    
    # Load the amenities data
    print("Loading amenities data...")
    df = pd.read_csv('data/processed/melbourne_amenities_20250717_170324.csv')
    
    print(f"Loaded {len(df)} amenity records")
    print("\nBreakdown by category:")
    print(df['category'].value_counts())
    
    # Create base map centered on Melbourne
    melbourne_center = [-37.8136, 144.9631]
    m = folium.Map(
        location=melbourne_center,
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add additional tile layers
    folium.TileLayer('CartoDB positron').add_to(m)
    folium.TileLayer('CartoDB dark_matter').add_to(m)
    
    # Define colors and icons for each category
    category_styles = {
        'supermarket': {'color': 'blue', 'icon': 'shopping-cart', 'prefix': 'fa'},
        'cafe': {'color': 'brown', 'icon': 'coffee', 'prefix': 'fa'},
        'gym': {'color': 'red', 'icon': 'dumbbell', 'prefix': 'fa'},
        'library': {'color': 'green', 'icon': 'book', 'prefix': 'fa'}
    }
    
    # Create marker clusters for each category
    marker_clusters = {}
    for category in df['category'].unique():
        cluster = plugins.MarkerCluster(
            name=f'{category.title()}s',
            overlay=True,
            control=True,
            show=True
        )
        marker_clusters[category] = cluster
        m.add_child(cluster)
    
    # Add markers for each amenity
    print("\nAdding markers to map...")
    for idx, row in df.iterrows():
        category = row['category']
        style = category_styles.get(category, {'color': 'gray', 'icon': 'info-sign', 'prefix': 'glyphicon'})
        
        # Create popup content
        popup_content = f"""
        <div style="width: 200px;">
            <h4 style="color: {style['color']};">{row['name']}</h4>
            <hr>
            <p><strong>Category:</strong> {category.title()}</p>
            <p><strong>Suburb:</strong> {row['suburb']}</p>
            <p><strong>Coordinates:</strong><br>
               Lat: {row['lat']:.4f}<br>
               Lon: {row['lon']:.4f}</p>
        </div>
        """
        
        # Create marker
        marker = folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=f"{row['name']} ({category})",
            icon=folium.Icon(
                color=style['color'],
                icon=style['icon'],
                prefix=style['prefix']
            )
        )
        
        # Add to appropriate cluster
        marker_clusters[category].add_child(marker)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 180px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Amenity Categories</h4>
    <p><i class="fa fa-shopping-cart" style="color:blue"></i> Supermarkets</p>
    <p><i class="fa fa-coffee" style="color:brown"></i> Cafes</p>
    <p><i class="fa fa-dumbbell" style="color:red"></i> Gyms</p>
    <p><i class="fa fa-book" style="color:green"></i> Libraries</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add a minimap
    minimap = plugins.MiniMap(toggle_display=True)
    m.add_child(minimap)
    
    # Add measure control
    plugins.MeasureControl().add_to(m)
    
    # Add fullscreen button
    plugins.Fullscreen(
        position='topleft',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True
    ).add_to(m)
    
    # Add search functionality
    plugins.Search(
        layer=marker_clusters['cafe'],  # You can search cafes as an example
        placeholder='Search for cafes...',
        collapsed=False,
    ).add_to(m)
    
    print(f"\nMap created successfully!")
    print(f"Total markers added: {len(df)}")
    print(f"Categories: {', '.join(df['category'].unique())}")
    
    return m, df

def analyze_amenities(df):
    """Provide some basic analysis of the amenities data."""
    print("\n" + "="*50)
    print("AMENITIES ANALYSIS")
    print("="*50)
    
    # Overall statistics
    print(f"\nTotal amenities: {len(df)}")
    print(f"Total suburbs: {df['suburb'].nunique()}")
    
    # Category breakdown
    print(f"\nCategory breakdown:")
    category_counts = df['category'].value_counts()
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {category.title()}: {count:,} ({percentage:.1f}%)")
    
    # Top suburbs by total amenities
    print(f"\nTop 10 suburbs by total amenities:")
    suburb_counts = df['suburb'].value_counts().head(10)
    for suburb, count in suburb_counts.items():
        print(f"  {suburb}: {count}")
    
    # Amenity density by category per suburb
    print(f"\nAverage amenities per suburb by category:")
    for category in df['category'].unique():
        cat_data = df[df['category'] == category]
        avg_per_suburb = len(cat_data) / cat_data['suburb'].nunique()
        print(f"  {category.title()}: {avg_per_suburb:.1f}")
    
    return category_counts, suburb_counts

if __name__ == "__main__":
    # Create the map
    map_obj, data = create_amenities_map()
    
    # Analyze the data
    category_counts, suburb_counts = analyze_amenities(data)
    
    # Save the map
    output_file = 'melbourne_amenities_map.html'
    map_obj.save(output_file)
    print(f"\nMap saved as: {output_file}")
    print("Open this file in your web browser to view the interactive map!")
    
    # Display some interesting findings
    print(f"\n" + "="*50)
    print("INTERESTING FINDINGS")
    print("="*50)
    
    # Find suburbs with most cafes
    cafe_suburbs = data[data['category'] == 'cafe']['suburb'].value_counts().head(5)
    print(f"\nTop 5 suburbs for cafes:")
    for suburb, count in cafe_suburbs.items():
        print(f"  {suburb}: {count} cafes")
    
    # Find suburbs with most supermarkets
    super_suburbs = data[data['category'] == 'supermarket']['suburb'].value_counts().head(5)
    print(f"\nTop 5 suburbs for supermarkets:")
    for suburb, count in super_suburbs.items():
        print(f"  {suburb}: {count} supermarkets")
    
    # Calculate amenity ratios
    print(f"\nAmenity ratios:")
    total_cafes = len(data[data['category'] == 'cafe'])
    total_gyms = len(data[data['category'] == 'gym'])
    total_libraries = len(data[data['category'] == 'library'])
    total_supermarkets = len(data[data['category'] == 'supermarket'])
    
    if total_gyms > 0:
        print(f"  Cafes per gym: {total_cafes/total_gyms:.1f}")
    if total_libraries > 0:
        print(f"  Cafes per library: {total_cafes/total_libraries:.1f}")
    if total_supermarkets > 0:
        print(f"  Cafes per supermarket: {total_cafes/total_supermarkets:.1f}") 