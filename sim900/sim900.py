"""
SIM900 GPRS driver para MicroPython (ESP32 S3)
Comunicação via UART usando AT commands
"""
import machine
import time
import json


class SIM900:
    def __init__(self, uart_id=1, tx_pin=17, rx_pin=16, pwrkey_pin=5, baudrate=9600):
        self.uart = machine.UART(uart_id, baudrate=baudrate,
                                 tx=machine.Pin(tx_pin),
                                 rx=machine.Pin(rx_pin))
        self.pwrkey = machine.Pin(pwrkey_pin, machine.Pin.OUT)
        self.pwrkey.value(1)

    # ── AT helpers ─────────────────────────────────────────────

    def _send(self, cmd, wait=1, expect=None):
        self.uart.write((cmd + "\r\n").encode())
        time.sleep(wait)
        resp = b""
        while self.uart.any():
            resp += self.uart.read()
        decoded = resp.decode(errors="ignore")
        if expect:
            return expect in decoded, decoded
        return decoded

    def _wait_for(self, text, timeout=10):
        start = time.time()
        buf = b""
        while time.time() - start < timeout:
            if self.uart.any():
                buf += self.uart.read()
                if text.encode() in buf:
                    return True
            time.sleep(0.2)
        return False

    # ── Power ──────────────────────────────────────────────────

    def power_on(self):
        print("[SIM900] Ligando modulo...")
        self.pwrkey.value(0)
        time.sleep(1)
        self.pwrkey.value(1)
        time.sleep(3)
        ok, _ = self._send("AT", wait=2, expect="OK")
        if ok:
            print("[SIM900] Modulo respondeu OK")
            return True
        print("[SIM900] Sem resposta. Verifica ligacao.")
        return False

    def power_off(self):
        self._send("AT+CPOWD=1", wait=2)

    # ── SIM / Rede ─────────────────────────────────────────────

    def check_sim(self):
        ok, resp = self._send("AT+CPIN?", wait=2, expect="READY")
        print("[SIM900] SIM:", "OK" if ok else "ERRO -" + resp.strip())
        return ok

    def signal_strength(self):
        resp = self._send("AT+CSQ", wait=1)
        print("[SIM900] Sinal:", resp.strip())
        return resp

    def wait_network(self, timeout=30):
        print("[SIM900] Aguardando registo na rede...")
        start = time.time()
        while time.time() - start < timeout:
            ok, resp = self._send("AT+CREG?", wait=1, expect=",1")
            if ok:
                print("[SIM900] Registado na rede!")
                return True
            time.sleep(2)
        print("[SIM900] Timeout: sem rede.")
        return False

    # ── GPRS ───────────────────────────────────────────────────

    def gprs_connect(self, apn):
        print("[SIM900] Conectando GPRS (APN={})...".format(apn))
        cmds = [
            ('AT+SAPBR=3,1,"Contype","GPRS"', 1),
            ('AT+SAPBR=3,1,"APN","{}"'.format(apn), 1),
            ('AT+SAPBR=1,1', 5),
        ]
        for cmd, wait in cmds:
            ok, resp = self._send(cmd, wait=wait, expect="OK")
            if not ok:
                print("[SIM900] Falhou:", cmd, "|", resp.strip())
                return False
        print("[SIM900] GPRS conectado!")
        return True

    def gprs_disconnect(self):
        self._send("AT+SAPBR=0,1", wait=2)

    # ── HTTP POST ──────────────────────────────────────────────

    def http_post(self, url, payload_dict):
        body = json.dumps(payload_dict)
        body_len = len(body)

        print("[SIM900] POST {} ({} bytes)".format(url, body_len))

        steps = [
            ("AT+HTTPINIT", 1, "OK"),
            ('AT+HTTPPARA="CID",1', 1, "OK"),
            ('AT+HTTPPARA="URL","{}"'.format(url), 1, "OK"),
            ('AT+HTTPPARA="CONTENT","application/json"', 1, "OK"),
        ]

        for cmd, wait, exp in steps:
            ok, resp = self._send(cmd, wait=wait, expect=exp)
            if not ok:
                print("[SIM900] Erro em:", cmd)
                self._send("AT+HTTPTERM", wait=1)
                return False

        # Enviar dados
        self.uart.write("AT+HTTPDATA={},5000\r\n".format(body_len).encode())
        if not self._wait_for("DOWNLOAD", timeout=5):
            print("[SIM900] Timeout aguardando DOWNLOAD")
            self._send("AT+HTTPTERM", wait=1)
            return False

        self.uart.write(body.encode())
        time.sleep(2)

        # Executar POST
        ok, resp = self._send("AT+HTTPACTION=1", wait=6, expect="+HTTPACTION")
        if not ok:
            print("[SIM900] Sem resposta do POST")
            self._send("AT+HTTPTERM", wait=1)
            return False

        # Extrair status HTTP
        status_code = "?"
        for part in resp.split(","):
            part = part.strip()
            if part.isdigit():
                status_code = part
                break

        print("[SIM900] HTTP Status:", status_code)
        self._send("AT+HTTPTERM", wait=1)
        return status_code in ("200", "201")
