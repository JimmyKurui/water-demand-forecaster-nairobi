import os, re
from flask import current_app
import geopandas as gpd
import folium
from folium import Choropleth, GeoJson
from itertools import chain
from ..constants import zones

# file_path = os.path.join(current_app.root_path, 'static/gis/kenya_wards/kenya_wards.shp')
file_path = os.path.join(current_app.root_path, 'static/gis/kenya_wards_zones/kenya_wards_zones.shp')

class Map:
    def __init__(self):
        kenya_wards = gpd.read_file(file_path)
        self.nairobi = kenya_wards[kenya_wards['county'] == 'Nairobi']
        self.crs = {'init':'epsg:4326'}
        self.category_colors = {
            'R1': 'green',
            'R2': 'blue',
            'R3': 'purple',
            'R4': 'red',
        }
        self.convert_crs()
        # self.append_zones()
    
    def convert_crs(self, _standard=None):
        self.nairobi.crs = _standard or self.crs
        
    def append_zones(self):
        ward_categories = {}
        ward_categories = {ward: self.match_zone(ward) for ward in self.nairobi['ward']}
        print('ward cats', ward_categories)
        self.nairobi['category'] = self.nairobi['ward'].map(ward_categories)
        self.nairobi.to_file(os.path.join(current_app.root_path, 'static/gis/kenya_wards_zones/kenya_wards_zones.shp'))
    
    def match_zone(self, gdf_ward):
        category = [k for k, v in zones.items() for el in v if re.search(rf'{el}', gdf_ward, re.IGNORECASE)][0]
        return category
    
    
    def create_water_choropleth(self, water_data=None, date=None):
        gdf = self.nairobi.copy()
        
        if water_data is None:
            return
        if not date:
            date = water_data.index.max()
        water_values = water_data.loc[date]
        
        gdf['volume'] = gdf['category'].map(water_values)
        
        center = [self.nairobi.geometry.centroid.y.mean(), self.nairobi.geometry.centroid.x.mean()]
        m = folium.Map(location=center, tiles='cartodbpositron', zoom_start=11)

        print(gdf.category.unique())
        choropleth = Choropleth(geo_data=gdf.__geo_interface__, 
            data=gdf[['ward', 'volume']], 
            columns=['ward', 'volume'],
            key_on="feature.properties.ward", 
            fill_color='YlGnBu', 
            legend_name='Water Prediction by Area Zones'
        )
        
        choropleth.add_to(m)
        map_path = os.path.join(current_app.root_path, 'static/maps/nairobi_map.html')
        m.save(map_path)
        return "/maps/nairobi_map.html"

    def generate_interactive_map(self):
        center = [self.nairobi.geometry.centroid.y.mean(), self.nairobi.geometry.centroid.x.mean()]
        m = folium.Map(location=center, tiles='cartodbpositron', zoom_start=11)
        # Zones chloropleth
        for k, v in zones.items():
            pattern = '|'.join([re.escape(word) for word in v])
            zone_gdf = self.nairobi[self.nairobi['ward'].str.contains(pattern, case=False, na=False)]
    

            color = self.category_colors.get(k, 'gray')
            def style_function(feature, color=color):
                return {'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.6}

            GeoJson(
                zone_gdf.__geo_interface__, 
                name=f'Category {k}',
                style_function=style_function
            ).add_to(m)
        folium.LayerControl().add_to(m)
        
        usage_choropleth = self.create_water_choropleth()
        usage_choropleth.add_to(m) if usage_choropleth else None
        folium.GeoJson(self.nairobi).add_to(m)
        map_path = os.path.join(current_app.root_path, 'static/maps/nairobi_map.html')
        m.save(map_path)
        return "/maps/nairobi_map.html"
    