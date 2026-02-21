from processing.spatial_cleaning import clean_geodata
from sqlalchemy import create_engine

def run_batch_etl(file_path, db_url):
    engine = create_engine(db_url)
    gdf = clean_geodata(file_path)
    gdf.to_postgis("road_segments", engine, if_exists="append", index=False)
