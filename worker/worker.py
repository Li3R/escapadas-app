import json
import os
import time
import urllib.request
from pymongo import MongoClient

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/")
client = MongoClient(MONGO_URI)
db = client["escapadas_db"]
pueblos_col = db["pueblos"]
visitas_col = db["visitas"]
estadisticas_col = db["estadisticas"]


def procesar_visitas():
    pendientes = list(visitas_col.find({"procesado": False}))
    for visita in pendientes:
        pueblos_col.update_one(
            {"properties.slug": visita["slug"]},
            {"$inc": {"visitas": 1}}
        )
        visitas_col.update_one(
            {"_id": visita["_id"]},
            {"$set": {"procesado": True}}
        )
    if pendientes:
        print(f"Procesadas {len(pendientes)} visitas nuevas.", flush=True)


def actualizar_ranking():
    top = list(
        pueblos_col.find(
            {"visitas": {"$gt": 0}},
            {"_id": 0, "properties.nombre": 1, "properties.slug": 1, "visitas": 1}
        )
        .sort("visitas", -1)
        .limit(5)
    )
    estadisticas_col.update_one(
        {"_id": "top_5"},
        {"$set": {"ranking": top}},
        upsert=True
    )


def actualizar_tiempo():
    hace_una_hora = time.time() - 3600
    pueblo = pueblos_col.find_one({
        "$or": [
            {"temperatura": {"$exists": False}},
            {"tiempo_actualizado": {"$lt": hace_una_hora}}
        ]
    })

    if not pueblo:
        return

    coords = pueblo["geometry"]["coordinates"]
    lon, lat = coords[0], coords[1]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    req = urllib.request.Request(url, headers={"User-Agent": "escapadas-worker"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        datos = json.loads(resp.read().decode())
        temp = datos["current_weather"]["temperature"]

    pueblos_col.update_one(
        {"_id": pueblo["_id"]},
        {"$set": {"temperatura": temp, "tiempo_actualizado": time.time()}}
    )
    print(f"Tiempo actualizado para {pueblo['properties']['nombre']}: {temp} °C", flush=True)


if __name__ == "__main__":
    print("Worker iniciado...", flush=True)
    while True:
        try:
            procesar_visitas()
            actualizar_ranking()
            actualizar_tiempo()
        except Exception as e:
            print(f"Error en worker: {e}", flush=True)
        time.sleep(5)
