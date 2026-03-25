import random
import time
import requests
from datetime import datetime

SERVER_URL = "https://irns.eurekaplatformapi.xyz/data"
DEVICE_ID = "sensor-001"

def generate_reading():
    return {
        'temperature': round(random.uniform(15.0, 45.0), 2),
        'humidity': round(random.uniform(20.0, 90.0), 2),
        'device_id': DEVICE_ID,
        'timestamp': datetime.utcnow().isoformat()
    }

def wait_for_server():
    print("Aguardando servidor ficar disponivel...", flush=True)
    while True:
        try:
            requests.get("https://irns.eurekaplatformapi.xyz/data", timeout=5)
            print("Servidor disponivel!", flush=True)
            break
        except Exception:
            time.sleep(2)

if __name__ == '__main__':
    wait_for_server()
    while True:
        reading = generate_reading()
        try:
            response = requests.post(SERVER_URL, json=reading, timeout=5)
            print(f"Enviado -> Temp: {reading['temperature']}°C | "
                  f"Humidade: {reading['humidity']}% | Status: {response.status_code}", flush=True)
        except Exception as e:
            print(f"Erro ao enviar: {e}", flush=True)
        time.sleep(5)
