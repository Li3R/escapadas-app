import os, random
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/")
client = MongoClient(MONGO_URI)
db = client["escapadas_db"]
collection = db["pueblos"]

@app.route("/listar_pueblos", methods=["GET"])
def listar_todos_los_pueblos():
    try:
        # Consulta sin filtro: trae todos los documentos excluyendo el _id
        resultado_db = list(collection.find({}, {"_id": 0}))
        return render_template("pueblos.html", pueblos=resultado_db)
        
    except Exception as e:
        return f"Error al cargar los pueblos: {e}", 500
        
@app.route("/pueblo_random", methods=["GET", "POST"])
def pueblo_random():
    pueblo_db = None
    if request.method == "POST":
        try:
            resultado_db = list(collection.find({}, {"_id": 0}))
            pueblo_db = random.choice(resultado_db)
        except Exception as e:
            return f"Error al cargar el pueblo: {e}", 500

    return render_template("rand_pueblo.html", pueblo=pueblo_db)
    
@app.route("/pueblos_mas_cercanos", methods=["GET", "POST"])
def pueblos_mas_cercanos():
    pueblos_db = None
    if request.method == "POST":
        try:
            lat = float(request.form.get("lat"))
            long = float(request.form.get("long"))
            km = float(request.form.get("km"))

            masCercanos = {
                "geometry": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [long, lat]
                        },
                        "$maxDistance": km * 1000,
                        "$minDistance": 0
                    }
                }
            }
            pueblos_db = list(collection.find(masCercanos, {"_id": 0}))
        except Exception as e:
            return f"Error al cargar los pueblos más cercanos: {e}", 500

    return render_template("pueblos_cercanos.html", pueblos=pueblos_db)
    
@app.route("/pueblo/<slug>")
def detalle_pueblo(slug):
    pueblo_db = collection.find_one({"properties.slug": slug}, {"_id": 0})
    if not pueblo_db:
        return "Pueblo no encontrado", 404

    db["visitas"].insert_one({
        "slug": slug,
        "procesado": False
    })

    return render_template("detalle_pueblo.html", pueblo=pueblo_db)


@app.route("/top_pueblos")
def top_pueblos():
    doc = db["estadisticas"].find_one({"_id": "top_5"})
    ranking = doc["ranking"] if doc else []
    return render_template("top_pueblos.html", ranking=ranking)
        
@app.route('/')
def show_template():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
