import os, re
from flask import current_app
import geopandas as gpd
import folium
from folium import Choropleth, GeoJson
from itertools import chain
from ..constants import zones

file_path = os.path.join(current_app.root_path, 'static/gis/kenya_wards/kenya_wards.shp')

class Map:
    def __init__(self):
        kenya_wards = gpd.read_file(file_path)
        self.nairobi = kenya_wards[kenya_wards['county'] == 'Nairobi']
        self.crs = {'init': 'epsg:4326'}
        self.category_colors = {
            'R1': 'green',
            'R2': 'blue',
            'R3': 'purple',
            'R4': 'red',
        }
    
    def convert_crs(self, _standard=None):
        self.nairobi.crs = _standard or self.crs
        
    def create_water_choropleth(self, _water_csv=None):
        if _water_csv:
            choropleth = Choropleth(geo_data=self.nairobi.__geo_interface__, 
            data=_water_csv, 
            key_on="feature.id", 
            fill_color='YlGnBu', 
            legend_name='Major criminal incidents (Jan-Aug 2018)'
            )
        else: 
            choropleth = None
        return choropleth
    
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
    