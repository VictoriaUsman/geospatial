# Urban Intelligence Platform

Production-grade geospatial data platform for real-time urban traffic analysis, built with Python, PostGIS, Docker, and FastAPI.

![Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Stack](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Stack](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Stack](https://img.shields.io/badge/Leaflet-199900?style=flat&logo=leaflet&logoColor=white)

---

## What It Does

A live traffic intelligence dashboard that:
- Displays **real-time traffic flow** from TomTom across 7 cities
- Renders a **PostGIS-backed heatmap** of road activity for Metro Manila
- Exposes a **REST API** for querying geospatial traffic data
- Supports **multi-city navigation** — Manila, Quezon City, Cebu, Davao, Singapore, Bangkok, Tokyo

---

## Architecture

```
OpenStreetMap (Overpass API)
        │
        ▼
db/seed_manila.py  ──► PostGIS (Docker)
                              │
                              ▼
                      api/main.py (FastAPI)  ◄──── Prometheus metrics
                              │
                              ▼
                      ui/index.html
                      ├── TomTom Traffic Tiles (live, global)
                      └── Leaflet Heatmap (PostGIS data, Manila)
```

---

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 15 + PostGIS 3.3 |
| Processing | GeoPandas, Shapely, H3 |
| Streaming | GCP Pub/Sub (configured) |
| Infrastructure | Docker, Terraform (GCP) |
| Monitoring | Prometheus |
| Frontend | Leaflet.js + TomTom Traffic API |

---

## Quick Start

### 1. Start the database

```bash
docker run -d \
  --name urban-postgis \
  -e POSTGRES_USER=urban \
  -e POSTGRES_PASSWORD=urban \
  -e POSTGRES_DB=urbandb \
  -p 5432:5432 \
  postgis/postgis:15-3.3

docker exec -i urban-postgis psql -U urban -d urbandb < db/schema.sql
```

### 2. Seed real Manila traffic data

```bash
pip install -r requirements.txt
python3 db/seed_manila.py
```

Fetches 1,000+ real road nodes from OpenStreetMap (Metro Manila bounding box) via Overpass API and loads them into PostGIS with traffic intensity values derived from known congestion hotspots.

### 3. Start the API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8080
```

### 4. Open the map

```bash
open ui/index.html
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/traffic/heatmap` | Heatmap points from PostGIS |

### Sample response — `/traffic/heatmap`

```json
{
  "points": [
    [14.5547, 121.0244, 0.95],
    [14.5794, 121.0359, 0.72]
  ],
  "count": 1000
}
```

Each point is `[latitude, longitude, intensity]` where intensity is `0.0–1.0`.

---

## Database Schema

```sql
-- Road segments (loaded via ETL pipeline)
CREATE TABLE road_segments (
    id        BIGSERIAL PRIMARY KEY,
    osm_id    BIGINT,
    name      TEXT,
    road_type TEXT,
    geom      GEOMETRY(LINESTRING, 4326)
);

-- GPS events (source for heatmap)
CREATE TABLE gps_events (
    id         BIGSERIAL,
    device_id  TEXT NOT NULL,
    latitude   DOUBLE PRECISION,
    longitude  DOUBLE PRECISION,
    speed      DOUBLE PRECISION,
    event_time TIMESTAMP NOT NULL,
    geom       GEOMETRY(POINT, 4326)
);
```

---

## Cities Supported

| City | TomTom Live Traffic | PostGIS Heatmap |
|---|---|---|
| Metro Manila | Yes | Yes |
| Quezon City | Yes | — |
| Cebu | Yes | — |
| Davao | Yes | — |
| Singapore | Yes | — |
| Bangkok | Yes | — |
| Tokyo | Yes | — |

---

## Running Tests

```bash
pip install pytest httpx
pytest tests/
```

---

## Project Structure

```
urban-intelligence-platform/
├── api/
│   └── main.py          FastAPI app with CORS, Prometheus, PostGIS query
├── db/
│   ├── schema.sql        PostGIS table definitions
│   └── seed_manila.py    OSM data fetcher and loader
├── ingestion/
│   └── batch_etl.py      GeoPandas ETL pipeline
├── processing/
│   ├── h3_utils.py       H3 hexagonal indexing
│   └── spatial_cleaning.py  GeoDataFrame cleaning
├── streaming/            GCP Pub/Sub integration
├── terraform/            GCP infrastructure as code
├── docker/
│   └── Dockerfile        Container definition
├── ui/
│   └── index.html        Leaflet map + TomTom + city selector
└── tests/
    └── test_health.py    API health check test
```
