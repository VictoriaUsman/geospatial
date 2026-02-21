from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response
import psycopg2

DB_URL = "postgresql://urban:urban@localhost:5432/urbandb"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_COUNT = Counter("request_count", "Total API Requests")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.get("/traffic/heatmap")
def heatmap():
    REQUEST_COUNT.inc()
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT latitude, longitude, speed
        FROM gps_events
        ORDER BY event_time DESC
        LIMIT 1000
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    max_speed = 60.0
    points = [
        [round(lat, 6), round(lon, 6), round(min(speed / max_speed, 1.0), 3)]
        for lat, lon, speed in rows
    ]
    return {"points": points, "count": len(points)}
