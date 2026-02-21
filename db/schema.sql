CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE road_segments (
    id BIGSERIAL PRIMARY KEY,
    osm_id BIGINT,
    name TEXT,
    road_type TEXT,
    geom GEOMETRY(LINESTRING, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_road_geom ON road_segments USING GIST (geom);

CREATE TABLE gps_events (
    id BIGSERIAL,
    device_id TEXT NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    event_time TIMESTAMP NOT NULL,
    geom GEOMETRY(POINT, 4326)
);
