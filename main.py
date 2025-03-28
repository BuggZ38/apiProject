from flask import Flask, request, jsonify
# from db import DB


# Configuration InfluxDB
INFLUX_URL = "http://localhost:8086"  # URL du serveur InfluxDB
INFLUX_TOKEN = "ton_token_influxdb"  # Token d'authentification
INFLUX_ORG = "ton_organisation"  # Organisation InfluxDB
INFLUX_BUCKET = "ton_bucket"  # Bucket de stockage

# db = DB(INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET)

app = Flask(__name__)

# Simulations des bases de données
devices = []  # Liste des capteurs
data = []  # Liste des données enregistrées
alerts = []  # Liste des alertes

# A changer quand la bdd sera co
def find_sensor(sensor_id):
    return next((sensor for sensor in devices if sensor["id"] == sensor_id), None)

# API Sensors
@app.route("/api/sensors", methods=["GET", "POST"])
def sensors():
    if request.method == "GET":
        return jsonify(devices) # return les devices connu
    elif request.method == "POST":
        new_sensor = request.json
        devices.append(new_sensor) # ajout d'un device dans la bdd
        return jsonify({"message": "Capteur ajouté", "sensor": new_sensor}), 201

@app.route("/api/sensors/<int:sensor_id>", methods=["GET"])
def get_sensor(sensor_id):
    sensor = find_sensor(sensor_id)
    if sensor:
        return jsonify(sensor)
    return jsonify({"error": "Capteur non trouvé"}), 404

# API Data
@app.route("/api/data", methods=["GET", "POST"])
def all_data():
    if request.method == "GET":
        return jsonify(data)
    elif request.method == "POST":
        new_data = request.json
        data.append(new_data)
        return jsonify({"message": "Donnée ajoutée", "data": new_data}), 201

@app.route("/api/data/<int:sensor_id>", methods=["GET"])
def get_sensor_data(sensor_id):
    sensor_data = [d for d in data if d["sensor_id"] == sensor_id]
    return jsonify(sensor_data)

# API Alerts
@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    return jsonify(alerts)

@app.route("/api/alerts/<int:alert_id>/acknowledge", methods=["POST"])
def acknowledge_alert(alert_id):
    alert = next((a for a in alerts if a["id"] == alert_id), None)
    if alert:
        alert["acknowledged"] = True
        return jsonify({"message": "Alerte reconnue", "alert": alert})
    return jsonify({"error": "Alerte non trouvée"}), 404


if __name__ == "__main__":
    app.run(debug=True, port="57400")