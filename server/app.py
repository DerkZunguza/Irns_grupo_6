from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

readings = []


@app.route('/', methods=['GET'])
def dashboard():
    return render_template('index.html')


@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'}), 400

    reading = {
        'temperature': data.get('temperature'),
        'humidity': data.get('humidity'),
        'device_id': data.get('device_id'),
        'timestamp': data.get('timestamp', datetime.utcnow().isoformat())
    }

    readings.append(reading)
    if len(readings) > 50:
        readings.pop(0)

    print(f"[{reading['timestamp']}] Device: {reading['device_id']} | "
          f"Temp: {reading['temperature']}°C | Humidity: {reading['humidity']}%", flush=True)

    return jsonify({'status': 'ok', 'received': reading}), 201


@app.route('/data', methods=['GET'])
def get_all():
    return jsonify(readings[-50:]), 200


@app.route('/data/latest', methods=['GET'])
def get_latest():
    if not readings:
        return jsonify({'error': 'No data yet'}), 404
    return jsonify(readings[-1]), 200


@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'ok', 'total_readings': len(readings)}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
