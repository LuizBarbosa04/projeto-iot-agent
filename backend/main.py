
import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
logger = logging.getLogger(__name__)

BUCKET = "scopo-estudo-luiz-2026"
REGIAO = "us-east-2"

session = boto3.Session(
    profile_name="scopo-lab",
    region_name=REGIAO
)

s3 = session.client("s3")


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
    momento = datetime.now(timezone.utc)
    identificador = uuid4().hex

    nome_arquivo = (
        f"telemetria/{momento:%Y/%m/%d}/"
        f"{identificador}.json"
    )

    registro = {
        **dados.model_dump(),
        "timestamp": momento.isoformat()
    }

    try:
        s3.put_object(
            Bucket=BUCKET,
            Key=nome_arquivo,
            Body=json.dumps(registro).encode("utf-8"),
            ContentType="application/json"
        )
    except (BotoCoreError, ClientError) as erro:
        logger.exception("Falha ao enviar telemetria ao S3")
        raise HTTPException(
            status_code=503,
            detail="Armazenamento temporariamente indisponivel"
        ) from erro

    telemetrias.append(registro)

    return {
        "mensagem": "Telemetria recebida e salva no S3",
        "dados": registro,
        "arquivo_s3": nome_arquivo
    }


@app.get("/telemetria")
def listar_telemetrias():
    return telemetrias
