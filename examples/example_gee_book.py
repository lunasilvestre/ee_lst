import ee
import geopandas as gpd

# Initialize the Earth Engine API
ee.Initialize()

# Load the KML file using geopandas
gdf = gpd.read_file('path_to_your_kml_file.kml')
geometry = ee.Geometry.Polygon(gdf.geometry[0].exterior.coords[:])

# Define the Landsat LST module (assuming you've refactored it to Python)
from python_modules.Landsat_LST import collection as landsat_collection

# Define parameters
satellite = 'L8'
date_start = '2014-01-01'
date_end = '2019-01-01'
use_ndvi = True

# Define the summer filter
sum_filter = ee.Filter.dayOfYear(152, 243)

# Get Landsat collection with additional necessary variables
landsat_coll = landsat_collection(satellite, date_start, date_end, geometry, use_ndvi)

# Create composite, clip, filter to summer, mask, and convert to degree Celsius
landsat_comp = (landsat_coll
                .select('LST')
                .filter(sum_filter)
                .median()
                .clip(geometry)
                .updateMask(not_water)  # Define the not_water mask
                .subtract(273.15))

# To visualize the result on a map, you'd typically use a library like folium or ipyleaflet
# Here's a basic example using folium:

import folium

# Define a method to display Earth Engine image tiles
def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; Google Earth Engine',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)

# Add EE drawing method to folium
folium.Map.add_ee_layer = add_ee_layer

# Create a folium map object
my_map = folium.Map(location=[20, 0], zoom_start=3, height=500)

# Add the Earth Engine layer to the folium map
vis_params = {
    'min': 25,
    'max': 38,
    'palette': ['blue', 'white', 'red']
}
my_map.add_ee_layer(landsat_comp, vis_params, 'LST_SMW')

# Display the map
my_map.save('map.html')
