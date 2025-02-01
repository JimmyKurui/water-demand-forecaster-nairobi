import os
from flask import current_app
import geopandas as gpd
import folium
from folium import Choropleth

file_path = os.path.join(current_app.root_path, 'static/gis/kenya_wards/kenya_wards.shp')

class Map:
    def __init__(self):
        kenya_wards = gpd.read_file(file_path)
        self.nairobi = kenya_wards[kenya_wards['county'] == 'Nairobi']
        self.crs = {'init': 'epsg:4326'}
        # Create only nairobi wards map
    
    def convert_crs(self, _standard=None):
        self.nairobi.crs = _standard or self.crs
        
    def create_choropleth(self, _water_csv=None):
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
        usage_choropleth = self.create_choropleth()
        usage_choropleth.add_to(m) if usage_choropleth else None
        folium.GeoJson(self.nairobi).add_to(m)
        map_path = os.path.join(current_app.root_path, 'static/maps/nairobi_map.html')
        m.save(map_path)
        return "/maps/nairobi_map.html"
    