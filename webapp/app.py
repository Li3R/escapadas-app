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
        
@app.route('/')
def show_template():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
