from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import asyncio

app = FastAPI(
    title="🌊 Beach API Brasil",
    description="API de condições climáticas das praias brasileiras",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Banco de dados ────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect("beaches.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS beach_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            beach_name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            temperature REAL,
            wind_speed REAL,
            wind_direction REAL,
            wave_height REAL,
            wave_period REAL,
            condition TEXT,
            score INTEGER,
            fetched_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ─── Praias cadastradas ────────────────────────────────────────────────────────

BEACHES = [
    {"name": "Santos", "city": "Santos", "state": "SP", "lat": -23.9618, "lon": -46.3322},
    {"name": "Guarujá", "city": "Guarujá", "state": "SP", "lat": -23.9929, "lon": -46.2564},
    {"name": "Ubatuba", "city": "Ubatuba", "state": "SP", "lat": -23.4336, "lon": -45.0838},
    {"name": "Florianópolis", "city": "Florianópolis", "state": "SC", "lat": -27.5954, "lon": -48.5480},
    {"name": "Balneário Camboriú", "city": "Balneário Camboriú", "state": "SC", "lat": -26.9906, "lon": -48.6348},
    {"name": "Arraial do Cabo", "city": "Arraial do Cabo", "state": "RJ", "lat": -22.9735, "lon": -42.0272},
    {"name": "Búzios", "city": "Búzios", "state": "RJ", "lat": -22.7469, "lon": -41.8819},
    {"name": "Porto Seguro", "city": "Porto Seguro", "state": "BA", "lat": -16.4460, "lon": -39.0647},
    {"name": "Jericoacoara", "city": "Jijoca de Jericoacoara", "state": "CE", "lat": -2.7975, "lon": -40.5137},
    {"name": "Maragogi", "city": "Maragogi", "state": "AL", "lat": -9.0103, "lon": -35.2225},
]

# ─── Lógica de condição ────────────────────────────────────────────────────────

def evaluate_condition(wave_height: float, wind_speed: float, temp: float) -> tuple[str, int]:
    score = 100

    # Ondas
    if wave_height < 0.5:
        score -= 10
    elif wave_height > 2.5:
        score -= 40
    elif wave_height > 1.5:
        score -= 20

    # Vento
    if wind_speed > 30:
        score -= 30
    elif wind_speed > 20:
        score -= 15
    elif wind_speed > 10:
        score -= 5

    # Temperatura
    if temp < 18:
        score -= 20
    elif temp < 22:
        score -= 10
    elif temp > 35:
        score -= 10

    score = max(0, min(100, score))

    if score >= 80:
        condition = "Excelente"
    elif score >= 60:
        condition = "Boa"
    elif score >= 40:
        condition = "Regular"
    else:
        condition = "Ruim"

    return condition, score

# ─── Fetch de dados externos ───────────────────────────────────────────────────

async def fetch_beach_data(beach: dict) -> dict:
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={beach['lat']}&longitude={beach['lon']}"
        f"&current=temperature_2m,wind_speed_10m,wind_direction_10m"
        f"&daily=wave_height_max,wave_period_max"
        f"&timezone=America/Sao_Paulo"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

    temp = data["current"]["temperature_2m"]
    wind_speed = data["current"]["wind_speed_10m"]
    wind_dir = data["current"]["wind_direction_10m"]
    wave_height = data["daily"].get("wave_height_max", [None])[0] or 1.0
    wave_period = data["daily"].get("wave_period_max", [None])[0] or 8.0

    condition, score = evaluate_condition(wave_height, wind_speed, temp)

    return {
        "beach_name": beach["name"],
        "city": beach["city"],
        "state": beach["state"],
        "latitude": beach["lat"],
        "longitude": beach["lon"],
        "temperature": temp,
        "wind_speed": wind_speed,
        "wind_direction": wind_dir,
        "wave_height": wave_height,
        "wave_period": wave_period,
        "condition": condition,
        "score": score,
        "fetched_at": datetime.now().isoformat(),
    }

def save_to_db(data: dict):
    conn = sqlite3.connect("beaches.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO beach_data
        (beach_name, city, state, latitude, longitude, temperature,
         wind_speed, wind_direction, wave_height, wave_period, condition, score, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["beach_name"], data["city"], data["state"],
        data["latitude"], data["longitude"], data["temperature"],
        data["wind_speed"], data["wind_direction"], data["wave_height"],
        data["wave_period"], data["condition"], data["score"], data["fetched_at"]
    ))
    conn.commit()
    conn.close()

# ─── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("index.html")

@app.get("/praias", summary="Lista todas as praias com condição atual")
async def list_beaches():
    """Retorna todas as praias com dados climáticos em tempo real."""
    tasks = [fetch_beach_data(b) for b in BEACHES]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    beaches = []
    for r in results:
        if isinstance(r, Exception):
            continue
        save_to_db(r)
        beaches.append(r)

    return {"total": len(beaches), "updated_at": datetime.now().isoformat(), "data": beaches}

@app.get("/praias/{nome}", summary="Dados de uma praia específica")
async def get_beach(nome: str):
    """Retorna dados climáticos de uma praia pelo nome."""
    beach = next((b for b in BEACHES if b["name"].lower() == nome.lower()), None)
    if not beach:
        raise HTTPException(status_code=404, detail=f"Praia '{nome}' não encontrada.")
    data = await fetch_beach_data(beach)
    save_to_db(data)
    return data

@app.get("/praias/{nome}/historico", summary="Histórico de uma praia")
async def get_history(nome: str, dias: int = 7):
    """Retorna histórico de condições dos últimos N dias."""
    conn = sqlite3.connect("beaches.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    since = (datetime.now() - timedelta(days=dias)).isoformat()
    c.execute("""
        SELECT * FROM beach_data
        WHERE beach_name = ? AND fetched_at >= ?
        ORDER BY fetched_at DESC
    """, (nome, since))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail=f"Sem histórico para '{nome}'.")
    return {"beach": nome, "days": dias, "records": len(rows), "data": rows}

@app.get("/ranking", summary="Ranking das melhores praias do dia")
async def ranking():
    """Retorna as praias ordenadas pela melhor condição atual."""
    tasks = [fetch_beach_data(b) for b in BEACHES]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    beaches = [r for r in results if not isinstance(r, Exception)]
    beaches.sort(key=lambda x: x["score"], reverse=True)

    return {
        "generated_at": datetime.now().isoformat(),
        "ranking": [
            {"position": i + 1, **b}
            for i, b in enumerate(beaches)
        ]
    }
