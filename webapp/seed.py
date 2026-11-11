import json
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/")
client = MongoClient(MONGO_URI)
db = client["escapadas_db"]
collection = db["pueblos"]

# Ruta exacta con el nombre de tu archivo GeoJSON
ruta_json = "/app/data/pueblos-mas-bonitos-de-espana.geojson"

if os.path.exists(ruta_json):
    with open(ruta_json, "r", encoding="utf-8") as f:
        datos = json.load(f)
        
    # Extraemos la lista de pueblos (si es un GeoJSON trae la clave 'features')
    if isinstance(datos, dict) and "features" in datos:
        lista_pueblos = datos["features"]
    else:
        lista_pueblos = datos
        
    collection.delete_many({})
    collection.insert_many(lista_pueblos)
    
    # Creamos el índice geoespacial
    collection.create_index([("geometry", "2dsphere")])
    
    print(f"¡Carga completada! Se han insertado {len(lista_pueblos)} pueblos.")
else:
    print(f"Error: No se encontró el archivo en {ruta_json}")
