import dht
import machine
import time
from sim900 import SIM900

# ── Configurações ──────────────────────────────────────────────
APN        = "internet"                              # mCel/Tmcel MZ
# APN      = "internet.movitel.co.mz"               # Movitel MZ
SERVER_URL = "https://irns.eurekaplatformapi.xyz/data"
DEVICE_ID  = "esp32-s3-sim900"
DHT_PIN    = 4                                       # GPIO do DATA do DHT11
INTERVAL   = 10                                      # segundos entre leituras

# Pinos UART do SIM900
SIM_TX     = 17
SIM_RX     = 16
SIM_PWRKEY = 5
# ───────────────────────────────────────────────────────────────

sensor = dht.DHT11(machine.Pin(DHT_PIN))
gsm    = SIM900(uart_id=1, tx_pin=SIM_TX, rx_pin=SIM_RX, pwrkey_pin=SIM_PWRKEY)


def get_timestamp():
    t = time.localtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )


def setup():
    if not gsm.power_on():
        print("Falha ao ligar SIM900. Reiniciando em 10s...")
        time.sleep(10)
        machine.reset()

    if not gsm.check_sim():
        print("SIM card nao detectado. Verifica o cartao.")
        time.sleep(10)
        machine.reset()

    gsm.signal_strength()

    if not gsm.wait_network(timeout=30):
        print("Sem rede GSM. Reiniciando em 10s...")
        time.sleep(10)
        machine.reset()

    if not gsm.gprs_connect(APN):
        print("Falha GPRS. Verifica o APN.")
        time.sleep(10)
        machine.reset()


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

    print("Leitura -> Temp: {}°C | Humidade: {}%".format(temperature, humidity))

    ok = gsm.http_post(SERVER_URL, payload)
    if not ok:
        print("Falha ao enviar. Reconectando GPRS...")
        gsm.gprs_disconnect()
        time.sleep(2)
        gsm.gprs_connect(APN)


# ── Boot ───────────────────────────────────────────────────────
setup()

# ── Loop principal ─────────────────────────────────────────────
while True:
    read_and_send()
    time.sleep(INTERVAL)
