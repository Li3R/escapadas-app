import json
import os
from pymongo import MongoClient

def get_database():
    # Usamos os.getenv para flexibilidad y conectamos a la DB del proyecto
    connection_string = os.getenv("MONGO_URI", "mongodb://db:27017/")
    client = MongoClient(connection_string)
    
    # Nombre estandarizado sin caracteres especiales (ñ/tildes)
    return client["escapadas_db"]
   
def import_geojson_into_db():
    # 1. Reutilizamos la función get_database()
    db = get_database()
    locations = db["pueblos"]

    # 2. Leemos el archivo GeoJSON
    with open("/app/data/pueblos-mas-bonitos-de-espana.geojson", "r", encoding="utf-8") as f:
        datos = json.load(f)

    # 3. Limpiamos por si el script se vuelve a ejecutar
    locations.delete_many({})

    # 4. Insertamos la lista completa
    features = datos.get("features", [])
    if features:
        locations.insert_many(features)
        
        locations.create_index([("geometry", "2dsphere")])
        
        print(f"¡Éxito! Se han importado {len(features)} pueblos.")

if __name__ == "__main__":
    import_geojson_into_db()
