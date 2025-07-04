import geopandas as gpd
import ee
import pandas as pd
from datetime import datetime
from tqdm import tqdm


# SETTINGS
shape_name = "Cameroon_agro-industrial_zones"
gdf = gpd.read_file(f'Shapefiles/{shape_name}.shp')
CROP_TYPE = "cocoa"

##################################################################
# Get shapefile coordinates

coords = []
for idx, row in gdf.iterrows():
    geometry = row.geometry
    # print(f"Feature {idx} coordinates:")

    # Centroid of the shape
    rep_point = geometry.representative_point()
    coords.append((rep_point.x, rep_point.y))


# Initialize the Earth Engine module
ee.Initialize(project = 'gradient-growers')


# Sentinel-2 surface reflectance collection
collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
    .filterDate("2017-01-01", "2025-06-30") \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))

# List of required bands
bands = {
    "red": "B4",
    "nir": "B8",
    "swir16": "B11",
    "swir22": "B12",
    "blue": "B2",
    "green": "B3",
    "rededge1": "B5",
    "rededge2": "B6",
    "rededge3": "B7",
    "nir08": "B8A",
}


features = []

for pt in tqdm(coords):
    # print(pt)

    point_geom = ee.Geometry.Point([pt[0], pt[1]])

    images = collection.filterBounds(point_geom).sort("CLOUDY_PIXEL_PERCENTAGE").limit(48)

    def map_image(image):
        image = ee.Image(image)
        values = image.select(list(bands.values())).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point_geom.buffer(15),
            scale=10,
            bestEffort=True,
            maxPixels=1e9
        )

        return ee.Feature(None, values
            .set("unique_id", f"{shape_name}_{pt[0]}_{pt[1]}")
            .set("time", image.date().format("YYYY-MM-dd"))
            .set("x", pt[0])
            .set("y", pt[1])
            .set("crop_type", CROP_TYPE)
        )

    point_features = images.map(map_image)
    features.append(point_features)

# Flatten list of FeatureCollections into one
all_features = ee.FeatureCollection(features).flatten()

# print(all_features)

# Export to Drive
task = ee.batch.Export.table.toDrive(
    collection=all_features,
    description=f"{shape_name}",
    fileFormat="CSV"
)
task.start()

print("Export started. Check https://code.earthengine.google.com/tasks for progress.")