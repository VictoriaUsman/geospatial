import geopandas as gpd

def clean_geodata(path):
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(epsg=4326)
    gdf = gdf[gdf.geometry.is_valid]
    return gdf
