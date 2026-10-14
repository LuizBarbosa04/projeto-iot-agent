
import json
from datetime import datetime, timezone

import boto3

BUCKET = "scopo-estudo-luiz-2026"

session = boto3.Session(
    profile_name="scopo-lab",
    region_name="us-east-2"
)

s3 = session.client("s3")

telemetria = {
    "dispositivo": "esp32-simulado-01",
    "temperatura": 27.5,
    "umidade": 68,
    "status": "online",
    "timestamp": datetime.now(timezone.utc).isoformat()
}

nome_arquivo = "telemetria/esp32-simulado-01.json"

s3.put_object(
    Bucket=BUCKET,
    Key=nome_arquivo,
    Body=json.dumps(telemetria).encode("utf-8"),
    ContentType="application/json"
)

print("Telemetria enviada com sucesso!")
print(f"Destino: s3://{BUCKET}/{nome_arquivo}")
