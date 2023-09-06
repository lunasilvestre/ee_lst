import ee

# Initialize the Earth Engine API
ee.Initialize()

# Define the Landsat LST module (assuming you've refactored it to Python)
from python_modules.Landsat_LST import collection as landsat_collection

# Define parameters
geometry = ee.Geometry.Rectangle([-8.91, 40.0, -8.3, 40.4])
satellite = 'L8'
date_start = '2022-05-15'
date_end = '2022-05-31'
use_ndvi = True

# Get Landsat collection with added variables: NDVI, FVC, TPW, EM, LST
landsat_coll = landsat_collection(satellite, date_start, date_end, geometry, use_ndvi)
print(landsat_coll.getInfo())

# Select the first feature
ex_image = landsat_coll.first()

# Visualization parameters
cmap1 = ['blue', 'cyan', 'green', 'yellow', 'red']
cmap2 = ['F2F2F2','EFC2B3','ECB176','E9BD3A','E6E600','63C600','00A600']

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
my_map = folium.Map(location=[40.2, -8.6], zoom_start=10, height=500)

# Add the Earth Engine layers to the folium map
# my_map.add_ee_layer(ex_image.select('TPW'), {'min': 0, 'max': 60, 'palette': cmap1}, 'TCWV')
# my_map.add_ee_layer(ex_image.select('TPWpos'), {'min': 0, 'max': 9, 'palette': cmap1}, 'TCWVpos')
# my_map.add_ee_layer(ex_image.select('FVC'), {'min': 0, 'max': 1, 'palette': cmap2}, 'FVC')
# my_map.add_ee_layer(ex_image.select('EM'), {'min': 0.9, 'max': 1.0, 'palette': cmap1}, 'Emissivity')
# my_map.add_ee_layer(ex_image.select('B10'), {'min': 290, 'max': 320, 'palette': cmap1}, 'TIR BT')
my_map.add_ee_layer(ex_image.select('LST'), {'min': 290, 'max': 320, 'palette': cmap1}, 'LST')
# my_map.add_ee_layer(ex_image.multiply(0.0000275).add(-0.2), {'bands': ['SR_B4', 'SR_B3', 'SR_B2'], 'min': 0, 'max': 0.3}, 'RGB')

# Display the map
my_map.save('map.html')

# Uncomment the code below to export an image band to your drive
# task = ee.batch.Export.image.toDrive(image=ex_image.select('LST'), description='LST', scale=30, region=geometry, fileFormat='GeoTIFF')
# task.start()
