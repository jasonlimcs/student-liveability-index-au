import pandas as pd
import geopandas as gpd
import folium
from folium import plugins
from folium.features import GeoJsonTooltip
import numpy as np

def create_combined_map():
    """Create an interactive folium map showing Melbourne SA2 demographics and amenities."""
    
    print("Loading demographic and geographic data...")
    # Load demographics and SA2 geometry data
    try:
        demographics = pd.read_csv("data/processed/abs_demographics_merged.csv")
        gdf_sa2 = gpd.read_file("data/external/SA2_2021_AUST_GDA2020.shp")
        print(f"Loaded demographics for {len(demographics)} SA2 areas")
        print(f"Loaded geometry data for {len(gdf_sa2)} SA2 areas")
    except FileNotFoundError as e:
        print(f"Error loading demographic/geographic data: {e}")
        print("Creating map with amenities only...")
        return create_amenities_only_map()
    
    # Prepare SA2 data
    gdf_sa2 = gdf_sa2[['SA2_CODE21', 'geometry']]
    gdf_sa2.columns = ['sa2_code', 'geometry']
    gdf_sa2['sa2_code'] = gdf_sa2['sa2_code'].astype(str)
    demographics['sa2_code'] = demographics['sa2_code'].astype(str)
    
    # Merge demographics with geometry
    gdf = gdf_sa2.merge(demographics, on='sa2_code', how='inner')
    gdf = gdf.replace([np.inf, -np.inf], np.nan).dropna()
    gdf = gdf.to_crs(epsg=4326)
    print(f"Merged data contains {len(gdf)} SA2 areas with complete data")
    
    # OPTIMIZATION 1: Filter to Melbourne metropolitan area only
    # Define Melbourne bounding box (expanded to include outer suburbs)
    melbourne_bbox = {
        'min_lat': -38.3,   # Expanded south to include Frankston, Dandenong areas
        'max_lat': -37.2,   # Expanded north to include Whittlesea, Nillumbik areas  
        'min_lon': 144.3,   # Expanded west to include Melton, Wyndham areas
        'max_lon': 145.9    # Expanded east to include Yarra Ranges, Knox areas
    }
    
    # Filter geometries to Melbourne area
    gdf_bounds = gdf.bounds
    melbourne_mask = (
        (gdf_bounds['miny'] >= melbourne_bbox['min_lat']) &
        (gdf_bounds['maxy'] <= melbourne_bbox['max_lat']) &
        (gdf_bounds['minx'] >= melbourne_bbox['min_lon']) &
        (gdf_bounds['maxx'] <= melbourne_bbox['max_lon'])
    )
    gdf = gdf[melbourne_mask].copy()
    print(f"Filtered to {len(gdf)} SA2 areas within Melbourne metropolitan area")
    
    # OPTIMIZATION 2: Simplify geometries to reduce file size
    print("Simplifying geometries to reduce file size...")
    # Use a tolerance that maintains shape but reduces detail (in degrees)
    tolerance = 0.001  # About 100m at Melbourne's latitude
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    
    # OPTIMIZATION 3: Round coordinates to reduce precision
    def round_coords(geom, precision=4):
        """Round coordinates to specified decimal places."""
        if geom.geom_type == 'Polygon':
            from shapely.geometry import Polygon
            exterior = [(round(x, precision), round(y, precision)) for x, y in geom.exterior.coords]
            holes = [[(round(x, precision), round(y, precision)) for x, y in hole.coords] 
                    for hole in geom.interiors]
            return Polygon(exterior, holes)
        elif geom.geom_type == 'MultiPolygon':
            from shapely.geometry import MultiPolygon, Polygon
            polygons = []
            for poly in geom.geoms:
                exterior = [(round(x, precision), round(y, precision)) for x, y in poly.exterior.coords]
                holes = [[(round(x, precision), round(y, precision)) for x, y in hole.coords] 
                        for hole in poly.interiors]
                polygons.append(Polygon(exterior, holes))
            return MultiPolygon(polygons)
        else:
            return geom
    
    gdf['geometry'] = gdf['geometry'].apply(lambda x: round_coords(x, precision=4))
    print("Optimized geometries for smaller file size")
    
    # Load amenities data
    print("Loading amenities data...")
    df_amenities = pd.read_csv('data/processed/melbourne_amenities_20250717_170324.csv')
    print(f"Loaded {len(df_amenities)} amenity records")
    print("\nBreakdown by category:")
    print(df_amenities['category'].value_counts())
    
    # Create base map centered on Melbourne
    melbourne_center = [-37.8136, 144.9631]
    m = folium.Map(
        location=melbourne_center,
        zoom_start=10,
        tiles='CartoDB positron'
    )
    
    # Add additional tile layers
    folium.TileLayer('OpenStreetMap').add_to(m)
    folium.TileLayer('CartoDB dark_matter').add_to(m)
    
    # Add SA2 Choropleth Layer (Base layer) - optimized
    metric = 'rent_to_income_ratio'
    tooltip_fields = ['sa2_code', 'median_weekly_rent', 'median_weekly_income', 'rent_to_income_ratio']
    
    print("Adding optimized SA2 choropleth layer...")
    folium.Choropleth(
        geo_data=gdf,
        name='Rent to Income Ratio',
        data=gdf,
        columns=['sa2_code', metric],
        key_on='feature.properties.sa2_code',
        fill_color='YlOrRd',
        fill_opacity=0.6,
        line_opacity=0.2,
        line_weight=1,  # Thinner lines
        nan_fill_color='gray',
        legend_name='Rent to Income Ratio'
    ).add_to(m)
    
    # Add Interactive Tooltip for SA2 areas (simplified)
    folium.GeoJson(
        gdf,
        name='SA2 Info',
        style_function=lambda x: {
            'fillColor': 'transparent', 
            'color': 'transparent',
            'weight': 0
        },
        tooltip=GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=['SA2 Code:', 'Weekly Rent ($):', 'Weekly Income ($):', 'Rent/Income Ratio:'],
            localize=True,
            sticky=True,
            labels=True
        )
    ).add_to(m)
    
    # Define colors and icons for each amenity category
    category_styles = {
        'supermarket': {'color': 'blue', 'icon': 'shopping-cart', 'prefix': 'fa'},
        'cafe': {'color': 'orange', 'icon': 'coffee', 'prefix': 'fa'},
        'gym': {'color': 'red', 'icon': 'dumbbell', 'prefix': 'fa'},
        'library': {'color': 'green', 'icon': 'book', 'prefix': 'fa'}
    }
    
    # Create marker clusters for each amenity category
    marker_clusters = {}
    for category in df_amenities['category'].unique():
        cluster = plugins.MarkerCluster(
            name=f'{category.title()}s',
            overlay=True,
            control=True,
            show=True,
            options={'maxClusterRadius': 50, 'spiderfyOnMaxZoom': True}
        )
        marker_clusters[category] = cluster
        m.add_child(cluster)
    
    # Add amenity markers
    print("Adding amenity markers...")
    for idx, row in df_amenities.iterrows():
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
    
    # Add enhanced legend
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 220px; height: 200px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; border-radius: 5px;">
    <h4 style="margin-top: 0;">Map Legend</h4>
    <hr>
    <h5>Rent-to-Income Ratio</h5>
    <p style="margin: 5px 0;"><span style="background: #ffffcc; padding: 2px 5px;">Low</span> to <span style="background: #bd0026; color: white; padding: 2px 5px;">High</span></p>
    <hr>
    <h5>Amenities</h5>
    <p style="margin: 3px 0;"><i class="fa fa-shopping-cart" style="color:blue"></i> Supermarkets</p>
    <p style="margin: 3px 0;"><i class="fa fa-coffee" style="color:orange"></i> Cafes</p>
    <p style="margin: 3px 0;"><i class="fa fa-dumbbell" style="color:red"></i> Gyms</p>
    <p style="margin: 3px 0;"><i class="fa fa-book" style="color:green"></i> Libraries</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl(position='topleft').add_to(m)
    
    # Add additional map features
    plugins.MiniMap(toggle_display=True, position='bottomleft').add_to(m)
    plugins.MeasureControl(position='topleft').add_to(m)
    plugins.Fullscreen(
        position='topleft',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True
    ).add_to(m)
    
    print(f"\nOptimized combined map created successfully!")
    print(f"SA2 areas with demographic data: {len(gdf)}")
    print(f"Total amenity markers added: {len(df_amenities)}")
    print(f"Amenity categories: {', '.join(df_amenities['category'].unique())}")
    print("File size optimizations applied:")
    print("  - Filtered to Melbourne metropolitan area only")
    print("  - Simplified geometries for smaller file size") 
    print("  - Reduced coordinate precision")
    
    return m, df_amenities, gdf

def create_amenities_only_map():
    """Fallback function to create amenities-only map if demographic data is unavailable."""
    
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
    
    print(f"\nMap created successfully!")
    print(f"Total markers added: {len(df)}")
    print(f"Categories: {', '.join(df['category'].unique())}")
    
    return m, df

def analyze_amenities(df_amenities, gdf=None):
    """Provide analysis of the amenities data and optionally demographic data."""
    print("\n" + "="*60)
    print("COMBINED ANALYSIS: DEMOGRAPHICS & AMENITIES")
    print("="*60)
    
    # Amenities analysis
    print(f"\nAMENITIES OVERVIEW")
    print(f"Total amenities: {len(df_amenities):,}")
    print(f"Total suburbs: {df_amenities['suburb'].nunique():,}")
    
    # Category breakdown
    print(f"\nCATEGORY BREAKDOWN:")
    category_counts = df_amenities['category'].value_counts()
    for category, count in category_counts.items():
        percentage = (count / len(df_amenities)) * 100
        print(f"  {category.title()}: {count:,} ({percentage:.1f}%)")
    
    # Top suburbs by total amenities
    print(f"\nTOP 10 SUBURBS BY TOTAL AMENITIES:")
    suburb_counts = df_amenities['suburb'].value_counts().head(10)
    for i, (suburb, count) in enumerate(suburb_counts.items(), 1):
        print(f"  {i:2d}. {suburb}: {count}")
    
    # Demographic analysis if available
    if gdf is not None:
        print(f"\nDEMOGRAPHIC OVERVIEW")
        print(f"SA2 areas with data: {len(gdf):,}")
        
        if 'rent_to_income_ratio' in gdf.columns:
            ratio_stats = gdf['rent_to_income_ratio'].describe()
            print(f"\nRENT-TO-INCOME RATIO STATISTICS:")
            print(f"  Average: {ratio_stats['mean']:.2f}")
            print(f"  Median: {ratio_stats['50%']:.2f}")
            print(f"  Range: {ratio_stats['min']:.2f} - {ratio_stats['max']:.2f}")
            
            # Find areas with highest and lowest ratios
            high_ratio_areas = gdf.nlargest(5, 'rent_to_income_ratio')[['sa2_code', 'rent_to_income_ratio']]
            low_ratio_areas = gdf.nsmallest(5, 'rent_to_income_ratio')[['sa2_code', 'rent_to_income_ratio']]
            
            print(f"\nHIGHEST RENT-TO-INCOME RATIOS:")
            for _, area in high_ratio_areas.iterrows():
                print(f"  SA2 {area['sa2_code']}: {area['rent_to_income_ratio']:.2f}")
            
            print(f"\nLOWEST RENT-TO-INCOME RATIOS:")
            for _, area in low_ratio_areas.iterrows():
                print(f"  SA2 {area['sa2_code']}: {area['rent_to_income_ratio']:.2f}")
    
    # Calculate amenity ratios
    print(f"\nAMENITY RATIOS:")
    total_cafes = len(df_amenities[df_amenities['category'] == 'cafe'])
    total_gyms = len(df_amenities[df_amenities['category'] == 'gym'])
    total_libraries = len(df_amenities[df_amenities['category'] == 'library'])
    total_supermarkets = len(df_amenities[df_amenities['category'] == 'supermarket'])
    
    if total_gyms > 0:
        print(f"  Cafes per gym: {total_cafes/total_gyms:.1f}")
    if total_libraries > 0:
        print(f"  Cafes per library: {total_cafes/total_libraries:.1f}")
    if total_supermarkets > 0:
        print(f"  Cafes per supermarket: {total_cafes/total_supermarkets:.1f}")
    
    return category_counts, suburb_counts

if __name__ == "__main__":
    # Create the combined map
    try:
        map_obj, amenities_data, demographic_data = create_combined_map()
        
        # Analyze the data
        category_counts, suburb_counts = analyze_amenities(amenities_data, demographic_data)
        
        # Save the map
        output_file = 'melbourne_combined_map.html'
        map_obj.save(output_file)
        print(f"\nCombined map saved as: {output_file}")
        print("Open this file in your web browser to view the interactive map!")
        
    except Exception as e:
        print(f"Error creating combined map: {e}")
        print("Creating amenities-only map as fallback...")
        
        map_obj, amenities_data = create_amenities_only_map()
        category_counts, suburb_counts = analyze_amenities(amenities_data)
        
        output_file = 'melbourne_amenities_map.html'
        map_obj.save(output_file)
        print(f"\nAmenities map saved as: {output_file}")
        print("Open this file in your web browser to view the interactive map!")
    
    # Display some interesting findings
    print(f"\n" + "="*60)
    print("INTERESTING FINDINGS")
    print("="*60)
    
    # Find suburbs with most cafes
    cafe_suburbs = amenities_data[amenities_data['category'] == 'cafe']['suburb'].value_counts().head(5)
    print(f"\nTOP 5 CAFE DESTINATIONS:")
    for i, (suburb, count) in enumerate(cafe_suburbs.items(), 1):
        print(f"  {i}. {suburb}: {count} cafes")
    
    # Find suburbs with most supermarkets
    super_suburbs = amenities_data[amenities_data['category'] == 'supermarket']['suburb'].value_counts().head(5)
    print(f"\nTOP 5 SHOPPING DESTINATIONS:")
    for i, (suburb, count) in enumerate(super_suburbs.items(), 1):
        print(f"  {i}. {suburb}: {count} supermarkets") 