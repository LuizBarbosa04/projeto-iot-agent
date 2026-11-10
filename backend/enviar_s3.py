
import json
from datetime import datetime, timezone
from uuid import uuid4
import random

import boto3

BUCKET = "scopo-estudo-luiz-2026"

session = boto3.Session(
    profile_name="scopo-lab",
    region_name="us-east-2"
)

s3 = session.client("s3")

telemetria = {
    "dispositivo": "esp32-simulado-01",
    "temperatura": round(random.uniform(18, 43), 2),
    "umidade": round(random.uniform(25, 85), 2),
    "status": "online",
    "timestamp": datetime.now(timezone.utc).isoformat()
}

momento = datetime.now(timezone.utc)
identificador = uuid4().hex

nome_arquivo = (
    f"telemetria/{momento:%Y/%m/%d}/"
    f"esp32-simulado-01_{identificador}.json"
)

s3.put_object(
    Bucket=BUCKET,
    Key=nome_arquivo,
    Body=json.dumps(telemetria).encode("utf-8"),
    ContentType="application/json"
)

print("Telemetria enviada com sucesso!")
print(f"Destino: s3://{BUCKET}/{nome_arquivo}")
