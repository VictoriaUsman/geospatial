"""
Fetches real Manila road nodes from OpenStreetMap via Overpass API
and seeds the gps_events table in PostGIS.
No GDAL required — uses only requests and psycopg2.
"""
import random
import requests
import psycopg2
from datetime import datetime, timedelta

DB_URL = "postgresql://urban:urban@localhost:5432/urbandb"

OVERPASS_MIRRORS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

# Smaller bounding box focused on Metro Manila core
QUERY = """
[out:json][timeout:25];
(
  node["highway"~"traffic_signals|crossing|bus_stop"](14.50,120.97,14.65,121.07);
);
out body 1000;
"""

def fetch_manila_nodes():
    print("Fetching Manila road data from OpenStreetMap...")
    for url in OVERPASS_MIRRORS:
        try:
            res = requests.post(url, data={"data": QUERY}, timeout=45)
            res.raise_for_status()
            elements = res.json().get("elements", [])
            print(f"  Got {len(elements)} road nodes from {url}")
            return [(e["lat"], e["lon"]) for e in elements if "lat" in e and "lon" in e]
        except Exception as e:
            print(f"  Mirror {url} failed: {e}, trying next...")
    return []

def assign_intensity(lat, lon):
    """Simulate traffic intensity based on known congested areas."""
    hotspots = [
        (14.5547, 121.0244),  # EDSA-Ortigas
        (14.5794, 121.0359),  # EDSA-Cubao
        (14.6091, 121.0222),  # EDSA-Quezon Ave
        (14.5182, 121.0110),  # EDSA-Magallanes
        (14.5564, 121.0229),  # Shaw Blvd
        (14.5243, 121.0412),  # BGC
        (14.5831, 120.9794),  # Divisoria
        (14.5995, 120.9842),  # Manila City Hall
    ]
    max_intensity = 0.1
    for hlat, hlon in hotspots:
        dist = ((lat - hlat) ** 2 + (lon - hlon) ** 2) ** 0.5
        intensity = max(0, 1.0 - dist * 80)
        max_intensity = max(max_intensity, intensity)
    return round(min(1.0, max_intensity + random.uniform(-0.05, 0.05)), 3)

def seed(nodes):
    print("Inserting into PostGIS...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    base_time = datetime.utcnow() - timedelta(hours=1)
    rows = []
    for i, (lat, lon) in enumerate(nodes):
        speed = assign_intensity(lat, lon) * 60  # km/h, 0-60
        event_time = base_time + timedelta(seconds=i * 2)
        rows.append((f"device_{i % 50}", lat, lon, round(speed, 2), event_time))

    cur.executemany("""
        INSERT INTO gps_events (device_id, latitude, longitude, speed, event_time, geom)
        VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
    """, [(r[0], r[1], r[2], r[3], r[4], r[2], r[1]) for r in rows])

    conn.commit()
    cur.close()
    conn.close()
    print(f"  Inserted {len(rows)} GPS events")

if __name__ == "__main__":
    nodes = fetch_manila_nodes()
    if nodes:
        seed(nodes)
        print("Done! Manila traffic data loaded.")
    else:
        print("No nodes returned. Check your internet connection.")
