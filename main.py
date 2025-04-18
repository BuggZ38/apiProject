from flask import Flask, request, jsonify, render_template
# from db import DB

from dbt import *

from datetime import datetime


# Configuration InfluxDB
INFLUX_URL = "http://localhost:8086"  # URL du serveur InfluxDB
INFLUX_TOKEN = "ton_token_influxdb"  # Token d'authentification
INFLUX_ORG = "ton_organisation"  # Organisation InfluxDB
INFLUX_BUCKET = "ton_bucket"  # Bucket de stockage

# db = DB(INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET)

db = Db()


alerts = []

app = Flask(__name__)

# A changer quand la bdd sera co
def find_sensor(sensor_id):
    return next((sensor for sensor in db.get_sensor() if sensor["id"] == sensor_id), None)

# API Sensors
@app.route("/api/sensors", methods=["GET", "POST"])
def sensors():
    if request.method == "GET":
        return jsonify(db.get_sensor()) # return les devices connu
    elif request.method == "POST":
        new_sensor = request.json['sensor']
        db.add_sensor(new_sensor) # ajout d'un device dans la bdd
        return jsonify({"message": "Capteur ajouté", "sensor": new_sensor}), 201

@app.route("/api/sensors/<int:sensor_id>", methods=["GET"])
def get_sensor(sensor_id):
    sensor = [d for d in db.get_sensor() if d["id"] == sensor_id]
    if sensor:
        return jsonify(sensor)
    return jsonify({"error": "Capteur non trouvé"}), 404

# API Data
@app.route("/api/data", methods=["GET", "POST"])
def all_data():
    if request.method == "GET":
        return jsonify(db.get_data())
    elif request.method == "POST":
        new_data = request.json
        db.add_data(new_data)
        return jsonify({"message": "Donnée ajoutée", "data": new_data}), 201

@app.route("/api/data/<int:sensor_id>", methods=["GET"])
def get_sensor_data(sensor_id):
    sensor_data = [d for d in db.get_data() if d["sender_id"] == sensor_id]
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


#Dashboard

@app.route("/")
def home_page():
    return render_template("sensors.html", sensors=db.get_sensor(), title="Capteurs")

@app.route("/sensors")
def sensors_page():
    return render_template("sensors.html", sensors=db.get_sensor(), title="Capteurs")

@app.route("/data")
def data_page():
    raw_data = db.get_data()
    data_by_sensor = {}
    filtered_data = []

    sensor_filter = request.args.get("sensor_id")
    all_sensor_ids = set()

    for d in raw_data:
        try:
            sensor_id = d["sender_id"]
            all_sensor_ids.add(sensor_id)

            # Ne pas traiter si on filtre un autre capteur
            if sensor_filter and str(sensor_id) != sensor_filter:
                continue

            timestamp = d["timestamp"]
            hex_parts = d["data"].split(":")
            value_lux = None

            if len(hex_parts) == 4 and hex_parts[3].lower() == "09":
                a, b, _, _ = hex_parts
                value_lux = convert_to_lux(a, b)

            elif len(hex_parts) == 1:
                a = hex_parts[0]
                value_lux = convert_to_lux(a, "00")

            if value_lux is not None:
                if sensor_id not in data_by_sensor:
                    data_by_sensor[sensor_id] = []

                entry = {"timestamp": timestamp, "value": value_lux}
                data_by_sensor[sensor_id].append(entry)
                filtered_data.append({
                    "sender_id": sensor_id,
                    "data": d["data"],
                    "timestamp": timestamp
                })

        except Exception as e:
            print(f"Erreur de parsing ({d.get('value', '?')}) : {e}")

    return render_template(
        "data.html",
        data=filtered_data,
        chart_data=data_by_sensor,
        all_sensor_ids=sorted(all_sensor_ids),
        title="Données"
    )


@app.route("/alerts", methods=["GET", "POST"])
def alerts_page():
    if request.method == "POST":
        alert_id = int(request.form.get("alert_id"))
        alert = next((a for a in alerts if a["id"] == alert_id), None)
        if alert:
            alert["acknowledged"] = True
    return render_template("alerts.html", alerts=alerts, title="Alertes")

@app.route("/historique")
def historique_page():
    # Récupère les valeurs des filtres
    date_str = request.args.get("date")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    # Récupération brute de l'historique
    raw_history = db.get_history()

    filtered = []
    for line in raw_history:
        try:
            # Extraction du datetime au début de la ligne
            date_part = line.split(" ---")[0]
            log_datetime = datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S.%f")

            # Filtrage si une date est sélectionnée
            if date_str:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if log_datetime.date() != selected_date:
                    continue

                if start_time and end_time:
                    start_dt = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
                    end_dt = datetime.strptime(f"{date_str} {end_time}", "%Y-%m-%d %H:%M")
                    if not (start_dt <= log_datetime <= end_dt):
                        continue

            # Si la ligne passe tous les filtres, on la garde
            filtered.append(line)

        except Exception as e:
            print(f"Erreur parsing ligne: {line} -> {e}")
            continue

    return render_template("historique.html", historique=filtered, title="Historique")

#utils

def convert_to_lux(a, b):
    if b == "00":
        return int(a, 16)  # Octet 1 : 0–100 directement
    else:
        val_b = int(b, 16)
        # Octet 2 : map 0x00–0xFF vers 30–30000
        return int((val_b / 255) * (30000 - 30) + 30)

@app.template_filter("datetimeformat")
def datetimeformat(value):
    return datetime.fromtimestamp(float(value)).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    app.run(debug=True, port="57400", host="172.16.25.22")