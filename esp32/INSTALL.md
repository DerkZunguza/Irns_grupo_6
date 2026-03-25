# Guia de Instalação — ESP32 S3 + DHT11 (WiFi ou SIM900)

---

## Ligações de Hardware

### DHT11

```
DHT11    →   ESP32 S3 Uno
VCC      →   3.3V
GND      →   GND
DATA     →   GPIO 4
```

### SIM900 (opcional — GSM/GPRS sem WiFi)

```
SIM900   →   ESP32 S3 Uno
VCC      →   5V (fonte externa recomendada — SIM900 consome até 2A)
GND      →   GND
TX       →   GPIO 16 (RX do ESP32)
RX       →   GPIO 17 (TX do ESP32)
PWRKEY   →   GPIO 5
```

> O SIM900 precisa de alimentação estável a 4V–5V com capacidade de 2A.
> Evita alimentar directamente pelo USB do ESP32 — usa uma fonte separada ou LiPo.

---

## 1. Instalar firmware MicroPython no ESP32 S3

### Descarregar o firmware

Vai a https://micropython.org/download/ESP32_GENERIC_S3/ e descarrega o ficheiro `.bin` mais recente.

### Instalar esptool

```bash
pip install esptool
```

### Apagar flash e gravar firmware

```bash
# Apagar a flash
esptool.py --chip esp32s3 --port COM3 erase_flash

# Gravar o firmware (substitui o nome do ficheiro)
esptool.py --chip esp32s3 --port COM3 write_flash -z 0x0 ESP32_GENERIC_S3-20240602-v1.23.0.bin
```

> No Windows: `COM3`, `COM4`, etc. No Linux/Mac: `/dev/ttyUSB0` ou `/dev/tty.usbserial-*`

---

## 2. Carregar os ficheiros para o ESP32

### Opção A — Thonny (recomendado)

1. Descarrega o Thonny em https://thonny.org
2. Menu **Executar** → **Configurar interpretador** → **MicroPython (ESP32)**
3. Selecciona a porta correcta
4. No painel de ficheiros, carrega os ficheiros para `/`

### Opção B — mpremote

```bash
pip install mpremote

# Modo WiFi (pasta esp32/wifi/)
mpremote connect COM3 cp esp32/wifi/boot.py :boot.py
mpremote connect COM3 cp esp32/wifi/main.py :main.py

# Modo SIM900 (pasta esp32/sim900/)
mpremote connect COM3 cp esp32/sim900/boot.py :boot.py
mpremote connect COM3 cp esp32/sim900/sim900.py :sim900.py
mpremote connect COM3 cp esp32/sim900/main.py :main.py

# Monitor serial
mpremote connect COM3 repl
```

---

## 3. Modo WiFi — configurar `esp32/wifi/main.py`

```python
SSID       = "NOME_DA_REDE"
PASSWORD   = "SENHA_DA_REDE"
SERVER_URL = "https://irns.eurekaplatformapi.xyz/data"
```

---

## 4. Modo SIM900 — configurar `esp32/sim900/main.py`

```python
APN        = "internet"           # mCel / Tmcel Moçambique
# APN      = "internet.movitel.co.mz"   # Movitel
SERVER_URL = "https://irns.eurekaplatformapi.xyz/data"
```

APNs comuns em Moçambique:

| Operador | APN                        |
|----------|----------------------------|
| mCel     | `internet`                 |
| Tmcel    | `internet`                 |
| Movitel  | `internet.movitel.co.mz`   |

Depois de configurar, carrega `sim900.py` + `main_sim900.py` (renomeia para `main.py`) para o ESP32.

---

## 5. Verificar funcionamento

### Monitor serial — modo WiFi

```
Conectando ao WiFi: NOME_DA_REDE
WiFi conectado! IP: 192.168.1.105
Enviando -> Temp: 27°C | Humidade: 65%
Resposta: 201
```

### Monitor serial — modo SIM900

```
[SIM900] Ligando modulo...
[SIM900] Modulo respondeu OK
[SIM900] SIM: OK
[SIM900] Registado na rede!
[SIM900] GPRS conectado!
Leitura -> Temp: 27°C | Humidade: 65%
[SIM900] POST https://irns.eurekaplatformapi.xyz/data (91 bytes)
[SIM900] HTTP Status: 201
```

---

## 6. Verificar no servidor

```bash
# Dashboard
https://irns.eurekaplatformapi.xyz

# Última leitura
curl https://irns.eurekaplatformapi.xyz/data/latest

# Status
curl https://irns.eurekaplatformapi.xyz/status
```
