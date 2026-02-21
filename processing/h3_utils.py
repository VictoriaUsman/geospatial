import h3

def get_h3_index(lat, lon, resolution=8):
    return h3.geo_to_h3(lat, lon, resolution)
