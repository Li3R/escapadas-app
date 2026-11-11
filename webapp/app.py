import os
from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/")
client = MongoClient(MONGO_URI)
db = client["escapadas_db"]
collection = db["pueblos"]

@app.route("/", methods=["GET"])
def listar_todos_los_pueblos():
    try:
        # Consulta sin filtro: trae todos los documentos excluyendo el _id
        pueblos = list(collection.find({}, {"_id": 0}))
        
        return jsonify({
            "total": len(pueblos),
            "pueblos": pueblos
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
