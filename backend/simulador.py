import requests
import random
import time

url = "http://127.0.0.1:8000/telemetria"

while True:
    dados = {
    "dispositivo": "esp32-simulado-01",
    "temperatura": round(random.uniform(20, 35), 1),
    "umidade": round(random.uniform(40, 80), 1)
}

    resposta = requests.post(url, json=dados)
    
    print(resposta.status_code)
    print(resposta.json())
    time.sleep(5)