from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Telemetria(BaseModel):
    dispositivo: str
    temperatura: float
    umidade: float

telemetrias = []

@app.get("/")
def home():
    return {"status": "online"}

@app.post("/telemetria")
def receber_telemetria(dados: Telemetria):
    telemetrias.append(dados)

    return {
        "mensagem": "Telemetria recebida",
        "dados": dados
    }

@app.get("/telemetria")
def listar_telemetrias():
    return telemetrias