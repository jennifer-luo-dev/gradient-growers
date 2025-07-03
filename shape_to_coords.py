import geopandas as gpd

# Load the shapefile
gdf = gpd.read_file('Shapefiles/Cameroon_agro-industrial_zones.shp')

# View coordinates
for idx, row in gdf.iterrows():
    geometry = row.geometry
    print(f"Feature {idx} coordinates:")

    if geometry.geom_type == 'Point':
        print(geometry.x, geometry.y)
    elif geometry.geom_type in ['LineString', 'Polygon']:
        coords = list(geometry.exterior.coords if geometry.geom_type == 'Polygon' else geometry.coords)
        for coord in coords:
            print(coord)
