
import random
import time
import requests

URL = "http://127.0.0.1:8000/telemetria"
DISPOSITIVO = "esp32-simulado-01"

print("=== SIMULADOR DE SENSOR IoT ===")
print("1 - Leituras normais")
print("2 - Leituras com anomalias")
print("3 - Modo misto")

modo = input("\nEscolha o modo (1, 2 ou 3): ").strip()

if modo not in ("1", "2", "3"):
    raise SystemExit("Modo inválido.")

print("\nIniciando transmissão. Pressione Ctrl+C para parar.\n")

try:
    while True:
        tipo = modo

        if modo == "3":
            tipo = random.choice(["1", "2"])

        if tipo == "1":
            temperatura = round(random.uniform(22, 34), 1)
            umidade = round(random.uniform(45, 75), 1)
        else:
            temperatura = round(random.uniform(38, 48), 1)
            umidade = round(random.uniform(15, 35), 1)

        dados = {
            "dispositivo": DISPOSITIVO,
            "temperatura": temperatura,
            "umidade": umidade
        }

        try:
            resposta = requests.post(
                URL,
                json=dados,
                timeout=15
            )
            resposta.raise_for_status()

            print(
                f"[{tipo}] "
                f"Temperatura: {temperatura} °C | "
                f"Umidade: {umidade}% | "
                f"HTTP {resposta.status_code}"
            )

        except requests.RequestException as erro:
            print(f"Erro ao enviar telemetria: {erro}")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nSimulação encerrada.")
