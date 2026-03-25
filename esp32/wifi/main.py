import network
import urequests
import dht
import machine
import time

# ── Configurações ──────────────────────────────────────────────
SSID       = "DerkZunguza"
PASSWORD   = "3.141592"
SERVER_URL = "https://irns.eurekaplatformapi.xyz/data"
DEVICE_ID  = "esp32-s3-001"
DHT_PIN    = 4                     # GPIO onde está o DATA do DHT11
INTERVAL   = 10                    # segundos entre leituras
# ───────────────────────────────────────────────────────────────

sensor = dht.DHT11(machine.Pin(DHT_PIN))
wlan   = network.WLAN(network.STA_IF)


def connect_wifi():
    wlan.active(True)
    if wlan.isconnected():
        return
    print("Conectando ao WiFi:", SSID)
    wlan.connect(SSID, PASSWORD)
    timeout = 15
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    if wlan.isconnected():
        print("\nWiFi conectado! IP:", wlan.ifconfig()[0])
    else:
        print("\nFalha ao conectar. Tentando de novo em 5s...")
        time.sleep(5)


def get_timestamp():
    t = time.localtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )


def read_and_send():
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity    = sensor.humidity()
    except Exception as e:
        print("Erro ao ler DHT11:", e)
        return

    payload = {
        "device_id":   DEVICE_ID,
        "temperature": temperature,
        "humidity":    humidity,
        "timestamp":   get_timestamp()
    }

    print("Enviando -> Temp: {}°C | Humidade: {}% | URL: {}".format(
        temperature, humidity, SERVER_URL))

    try:
        response = urequests.post(
            SERVER_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print("Resposta:", response.status_code)
        response.close()
    except Exception as e:
        print("Erro ao enviar dados:", e)


# ── Loop principal ─────────────────────────────────────────────
while True:
    if not wlan.isconnected():
        connect_wifi()

    if wlan.isconnected():
        read_and_send()

    time.sleep(INTERVAL)
