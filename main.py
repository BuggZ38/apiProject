from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/sensors", methods=["GET", "POST"])
def sensors_list():
    if request.method == "POST":
        return jsonify({"func": "add sensor to the list of sensors", "data-get": request.get_json()})
    return jsonify({"data-get": "list of sensors"})

@app.route("/api/sensors/data", methods=["GET"])
def sensors_data():
    return jsonify({"func": "data of all sensors"})

@app.route("/api/sensors/data/<sensor_id>", methods=["GET", "POST"])
def sensor_data(sensor_id):
    if request.method == "POST":
        if sensor_id is not None:
            return jsonify({"sensor_id" : sensor_id, "func": "add data for this sensor", "data-get": request.get_json()})
        return jsonify({"data-get": "enter sensor ID"})
    return jsonify({"data-get": "get data of this sensors"})


@app.route("/")
def home():
    return jsonify({"text": "Api pour le projet 2sei bts CIEL"})


if __name__ == "__main__":
    app.run(debug=True, port="57400")