# Sistema IoT — Projecto Universitário

Sistema IoT com Flask (servidor), sensor simulado (Docker), hardware real ESP32 S3 + DHT11, com suporte a WiFi e SIM900 (GSM/GPRS).

## Estrutura do Projecto

```
iot-project/
├── docker-compose.yml          ← produção (Traefik + VPS)
├── .gitignore
├── README.md
├── server/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── templates/
│       └── index.html          ← dashboard web
├── sensor/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── sensor.py               ← sensor simulado
└── esp32/
    ├── INSTALL.md
    ├── wifi/
    │   ├── boot.py
    │   └── main.py             ← ESP32 via WiFi
    └── sim900/
        ├── boot.py
        ├── sim900.py           ← driver AT commands
        └── main.py             ← ESP32 via GSM/GPRS
```

---

## Produção — Deploy no VPS (Portainer)

### Pré-requisitos no servidor
- Traefik a correr com `traefik-public` network criada
- Portainer instalado

### Deploy

1. Portainer → **Stacks** → **Add Stack**
2. Build method: **Repository**
3. Repository URL: `https://github.com/SEU_USER/iot-project`
4. Compose path: `docker-compose.yml`
5. **Deploy**

Dashboard disponível em: `https://irns.eurekaplatformapi.xyz`

---

## Local — Desenvolvimento com Docker

```bash
docker compose up --build
```

Abre `http://localhost:5000`

---

## Hardware — ESP32 S3 + DHT11

### Ligação DHT11

```
DHT11   →   ESP32 S3
VCC     →   3.3V
GND     →   GND
DATA    →   GPIO 4
```

### Modo WiFi (`esp32/wifi/`)

Edita `esp32/wifi/main.py`:
```python
SSID       = "NOME_DA_REDE"
PASSWORD   = "SENHA_DA_REDE"
SERVER_URL = "https://irns.eurekaplatformapi.xyz/data"
```

Carrega `boot.py` + `main.py` para o ESP32.

### Modo SIM900 (`esp32/sim900/`)

Ligação SIM900:
```
SIM900   →   ESP32 S3
TX       →   GPIO 16
RX       →   GPIO 17
PWRKEY   →   GPIO 5
VCC      →   5V (fonte externa)
GND      →   GND
```

Edita `esp32/sim900/main.py`:
```python
APN        = "internet"    # mCel/Tmcel MZ
SERVER_URL = "https://irns.eurekaplatformapi.xyz/data"
```

Carrega `boot.py` + `sim900.py` + `main.py` para o ESP32.

Ver instruções completas em `esp32/INSTALL.md`.

---

## Endpoints da API

| Método | Endpoint       | Descrição                          |
|--------|----------------|------------------------------------|
| GET    | /              | Dashboard HTML                     |
| POST   | /data          | Recebe leitura do sensor           |
| GET    | /data          | Últimas 50 leituras                |
| GET    | /data/latest   | Leitura mais recente               |
| GET    | /status        | Estado e total de leituras         |

---

## Tecnologias

- **Python 3.11** + **Flask** — API REST + dashboard
- **HTML + CSS + JS** + **Chart.js** — dashboard responsivo
- **Docker** + **Traefik** — deploy em produção
- **MicroPython** — firmware ESP32 S3
- **DHT11** — sensor temperatura/humidade
- **SIM900** — conectividade GSM/GPRS (sem WiFi)
