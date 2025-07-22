import pandas as pd
import geopandas as gpd
import folium
from folium import plugins
from folium.features import GeoJsonTooltip
import numpy as np
import sys
import json

# Add data loading modules
sys.path.append('../src')
from data.supabase_loader import load_amenities_data, load_demographics_data, load_safety_scores

def create_combined_map():
    """Create an interactive folium map showing Melbourne SA2 demographics and amenities with proper boundaries."""
    
    print("Loading demographic and geographic data...")
    demographics = None
    gdf_sa2 = None
    try:
        demographics = load_demographics_data()
        gdf_sa2 = gpd.read_file("../data/external/SA2_2021_AUST_GDA2020.shp")
        print(f"Loaded demographics for {len(demographics)} SA2 areas")
        print(f"Loaded geometry data for {len(gdf_sa2)} SA2 areas")
    except Exception as e:
        print(f"Error loading demographic/geographic data: {e}")
        demographics = None
        gdf_sa2 = None

    # Load amenities data
    print("Loading amenities data...")
    try:
        df_amenities = load_amenities_data()
        if not df_amenities.empty:
            print(f"Loaded {len(df_amenities)} amenity records")
            print("\nBreakdown by category:")
            print(df_amenities['category'].value_counts())
        else:
            print("No amenities data found in database")
            df_amenities = pd.DataFrame()
    except Exception as e:
        print(f"Error loading amenities from database: {e}")
        df_amenities = pd.DataFrame()

    # Create base map centered on Melbourne
    melbourne_center = [-37.8136, 144.9631]
    m = folium.Map(
        location=melbourne_center,
        zoom_start=10,
        tiles='CartoDB positron'
    )
    folium.TileLayer('OpenStreetMap').add_to(m)
    folium.TileLayer('CartoDB dark_matter').add_to(m)

    # Try to add SA2 choropleth if possible
    if demographics is not None and gdf_sa2 is not None and not demographics.empty:
        try:
            gdf_sa2 = gdf_sa2[['SA2_CODE21', 'geometry']]
            gdf_sa2.columns = ['sa2_code', 'geometry']
            gdf_sa2['sa2_code'] = gdf_sa2['sa2_code'].astype(str)
            demographics['sa2_code'] = demographics['sa2_code'].astype(str)
            gdf = gdf_sa2.merge(demographics, on='sa2_code', how='inner')
            gdf = gdf.replace([np.inf, -np.inf], np.nan).dropna()
            gdf = gdf.to_crs(epsg=4326)
            print(f"Merged data contains {len(gdf)} SA2 areas with complete data")
            # Filter to Melbourne area
            gdf_bounds = gdf.bounds
            melbourne_bbox = {
                'min_lat': -38.2255,
                'max_lat': -37.5,
                'min_lon': 144.18,
                'max_lon': 145.375
            }
            melbourne_mask = (
                (gdf_bounds['miny'] >= melbourne_bbox['min_lat']) &
                (gdf_bounds['maxy'] <= melbourne_bbox['max_lat']) &
                (gdf_bounds['minx'] >= melbourne_bbox['min_lon']) &
                (gdf_bounds['maxx'] <= melbourne_bbox['max_lon'])
            )
            gdf = gdf[melbourne_mask].copy()
            print(f"Filtered to {len(gdf)} SA2 areas within Melbourne metropolitan area")
            tolerance = 0.001
            gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
            metric = 'rent_to_income_ratio'
            tooltip_fields = ['sa2_code', 'median_weekly_rent', 'median_weekly_income', 'rent_to_income_ratio']
            print("Adding SA2 choropleth layer with proper boundaries...")
            folium.Choropleth(
                geo_data=gdf,
                name='Rent to Income Ratio',
                data=gdf,
                columns=['sa2_code', metric],
                key_on='feature.properties.sa2_code',
                fill_color='YlOrRd',
                fill_opacity=0.6,
                line_opacity=0.4,
                line_weight=1,
                nan_fill_color='lightgray',
                legend_name='Rent to Income Ratio'
            ).add_to(m)
            folium.GeoJson(
                gdf,
                name='SA2 Boundaries & Info',
                style_function=lambda feature: {
                    'fillColor': 'transparent',
                    'color': '#2c3e50',
                    'weight': 2,
                    'opacity': 0.8,
                    'fillOpacity': 0,
                    'dashArray': '0'
                },
                highlight_function=lambda feature: {
                    'fillColor': '#3498db',
                    'color': '#2980b9',
                    'weight': 3,
                    'opacity': 1.0,
                    'fillOpacity': 0.3
                },
                tooltip=GeoJsonTooltip(
                    fields=tooltip_fields,
                    aliases=['SA2 Code:', 'Weekly Rent ($):', 'Weekly Income ($):', 'Rent/Income Ratio:'],
                    localize=True,
                    sticky=True,
                    labels=True,
                    style="""
                        background-color: white;
                        border: 2px solid black;
                        border-radius: 3px;
                        box-shadow: 3px;
                    """
                ),
                popup=folium.Popup(max_width=300)
            ).add_to(m)
        except Exception as e:
            print(f"Could not add SA2 choropleth: {e}")

    # Always try to add LGA safety layer
    print("\nLoading LGA boundaries and safety scores...")
    try:
        gdf_lga = gpd.read_file("../data/external/LGA/LGA_2024_AUST_GDA2020.shp")
        # Filter to Melbourne area using bounding box
        gdf_lga = gdf_lga.to_crs(epsg=4326)
        lga_bounds = gdf_lga.bounds
        melbourne_bbox = {
            'min_lat': -38.2255,
            'max_lat': -37.5,
            'min_lon': 144.18,
            'max_lon': 145.375
        }
        melbourne_mask = (
            (lga_bounds['miny'] >= melbourne_bbox['min_lat']) &
            (lga_bounds['maxy'] <= melbourne_bbox['max_lat']) &
            (lga_bounds['minx'] >= melbourne_bbox['min_lon']) &
            (lga_bounds['maxx'] <= melbourne_bbox['max_lon'])
        )
        gdf_lga = gdf_lga[melbourne_mask].copy()
        print(f"Filtered to {len(gdf_lga)} LGAs within Melbourne metropolitan area")
        safety_df = load_safety_scores()
        print(f"Loaded {len(safety_df)} safety records")
    except Exception as e:
        print(f"Error loading LGA boundaries or safety data: {e}")
        gdf_lga = None
        safety_df = None
    if gdf_lga is not None and safety_df is not None and not safety_df.empty:
        lga_name_col = None
        for col in gdf_lga.columns:
            if col.lower().startswith("lga") and ("name" in col.lower() or "_name" in col.lower()):
                lga_name_col = col
                break
        if not lga_name_col:
            lga_name_col = "LGA_NAME22" if "LGA_NAME22" in gdf_lga.columns else gdf_lga.columns[0]
        gdf_lga["lga"] = gdf_lga[lga_name_col].astype(str).str.strip()
        # Remove ' (Vic.)' from the end of LGA names for matching
        gdf_lga["lga"] = gdf_lga["lga"].str.replace(r"\s*\(Vic\.\)$", "", regex=True).str.strip()
        safety_df["lga"] = safety_df["lga"].astype(str).str.strip()
        gdf_lga = gdf_lga.to_crs(epsg=4326)
        gdf_lga = gdf_lga.merge(safety_df, on="lga", how="left")
        print(f"Merged LGA boundaries with safety data: {len(gdf_lga)} records")
        print("Adding LGA safety choropleth layer...")
        safety_color_map = {
            "High": "#2ecc40",
            "Medium": "#ffdc00",
            "Low": "#ff4136"
        }
        def lga_style(feature):
            cat = feature["properties"].get("safety_category", "")
            color = safety_color_map.get(cat, "#cccccc")
            return {
                'fillColor': color,
                'color': '#333',
                'weight': 2,
                'fillOpacity': 0.5 if cat else 0,
                'opacity': 0.7
            }
        lga_tooltip_fields = ["lga", "safety_score", "safety_category", "total_crime_count", "violent_crime_count", "property_crime_count", "drug_offence_count", "public_order_offence_count", "justice_procedures_offence_count"]
        lga_tooltip_aliases = ["LGA:", "Safety Score:", "Safety Category:", "Total Crimes:", "Violent Crimes:", "Property Crimes:", "Drug Offences:", "Public Order Offences:", "Justice Procedures Offences:"]
        folium.GeoJson(
            gdf_lga,
            name="LGA Safety Levels",
            style_function=lga_style,
            highlight_function=lambda f: {'weight': 4, 'color': '#0074D9', 'fillOpacity': 0.7},
            tooltip=GeoJsonTooltip(
                fields=lga_tooltip_fields,
                aliases=lga_tooltip_aliases,
                localize=True,
                sticky=True,
                labels=True,
                style="""
                    background-color: white;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """
            ),
            popup=folium.Popup(max_width=350)
        ).add_to(m)

    # Add amenity markers if available
    if not df_amenities.empty:
        print("Adding amenity markers...")
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
    
    # Add university markers (Melbourne area only)
    try:
        with open("../config/universities.json", "r", encoding="utf-8") as f:
            universities = json.load(f)
        # Only show universities in Victoria (lat -38.3 to -37.5, lon 144.5 to 145.5)
        melb_unis = [u for u in universities if -38.3 < u["lat"] < -37.5 and 144.5 < u["lon"] < 145.5]
        for uni in melb_unis:
            folium.Marker(
                location=[uni["lat"], uni["lon"]],
                popup=folium.Popup(f'<b>{uni["name"]}</b>', max_width=250),
                tooltip=uni["name"],
                icon=folium.Icon(color='purple', icon='university', prefix='fa')
            ).add_to(m)
        print(f"Added {len(melb_unis)} university markers to the map.")
    except Exception as e:
        print(f"Error adding university markers: {e}")
    
    # Add enhanced legend
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 250px; height: 220px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 15px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <h4 style="margin-top: 0; color: #2c3e50;">Map Legend</h4>
    <hr style="margin: 10px 0;">
    <h5 style="color: #e74c3c;">Rent-to-Income Ratio</h5>
    <p style="margin: 5px 0;"><span style="background: #ffffcc; padding: 2px 5px; border: 1px solid #ccc;">Low</span> to <span style="background: #bd0026; color: white; padding: 2px 5px;">High</span></p>
    <p style="font-size: 12px; color: #7f8c8d; margin: 5px 0;">Click suburbs to see exact boundaries</p>
    '''
    
    if not df_amenities.empty:
        legend_html += '''
        <hr style="margin: 10px 0;">
        <h5 style="color: #2c3e50;">Amenities</h5>
        <p style="margin: 3px 0;"><i class="fa fa-shopping-cart" style="color:blue"></i> Supermarkets</p>
        <p style="margin: 3px 0;"><i class="fa fa-coffee" style="color:orange"></i> Cafes</p>
        <p style="margin: 3px 0;"><i class="fa fa-dumbbell" style="color:red"></i> Gyms</p>
        <p style="margin: 3px 0;"><i class="fa fa-book" style="color:green"></i> Libraries</p>
        '''
    
    legend_html += '</div>'
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
    
    print(f"\nMap created successfully with proper SA2 boundaries!")
    print(f"SA2 areas with demographic data: {len(gdf)}")
    if not df_amenities.empty:
        print(f"Total amenity markers added: {len(df_amenities)}")
        print(f"Amenity categories: {', '.join(df_amenities['category'].unique())}")
    print("\nInteraction features:")
    print("- Hover over SA2 areas to see tooltips with demographic info")
    print("- Click SA2 areas to highlight exact boundaries (not rectangles)")
    print("- Use layer control to toggle different data layers")
    
    return m, df_amenities if not df_amenities.empty else None, gdf

def create_amenities_only_map():
    """Fallback function to create amenities-only map if demographic data is unavailable."""
    
    print("Loading amenities data from database...")
    try:
        df = load_amenities_data()
        if df.empty:
            print("ERROR: No amenities data found in database!")
            return None, None
    except Exception as e:
        print(f"ERROR: Failed to load amenities from database: {e}")
        return None, None
    
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
        'cafe': {'color': 'orange', 'icon': 'coffee', 'prefix': 'fa'},
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
    <p><i class="fa fa-coffee" style="color:orange"></i> Cafes</p>
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

if __name__ == "__main__":
    # Create the combined map
    try:
        map_obj, amenities_data, demographic_data = create_combined_map()
        
        if map_obj is None:
            print("Failed to create map!")
            exit(1)
        
        # Save the map
        output_file = '../output/melbourne_combined_map.html'
        map_obj.save(output_file)
        print(f"\nCombined map saved as: {output_file}")
        print("Open this file in your web browser to view the interactive map!")
        print("\nKey Features:")
        print("- SA2 areas show EXACT boundaries (not rectangles) when clicked")
        print("- Hover tooltips show demographic information")
        print("- Choropleth colors represent rent-to-income ratios")
        print("- Amenity markers are clustered by category")
        print("- Layer control allows toggling different data")
        
    except Exception as e:
        print(f"Error creating combined map: {e}")
        print("Creating amenities-only map as fallback...")
        
        map_obj, amenities_data = create_amenities_only_map()
        
        if map_obj is None:
            print("Failed to create any map!")
            exit(1)
        
        output_file = '../output/melbourne_amenities_map.html'
        map_obj.save(output_file)
        print(f"\nAmenities map saved as: {output_file}")
        print("Open this file in your web browser to view the interactive map!") 