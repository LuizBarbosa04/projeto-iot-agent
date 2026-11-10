
import json

import boto3
from botocore.exceptions import BotoCoreError, ClientError

BUCKET = "scopo-estudo-luiz-2026"
ARQUIVO = "telemetria/esp32-simulado-01.json"

session = boto3.Session(
    profile_name="scopo-lab",
    region_name="us-east-2"
)

s3 = session.client("s3")


def consultar_telemetria():
    try:
        resposta = s3.get_object(
            Bucket=BUCKET,
            Key=ARQUIVO
        )

        conteudo = resposta["Body"].read()
        dados = json.loads(conteudo.decode("utf-8"))

        return dados

    except (BotoCoreError, ClientError) as erro:
        print(f"Erro ao consultar o S3: {erro}")
        raise


if __name__ == "__main__":
    print("Consultando telemetria no Amazon S3...\n")

    telemetria = consultar_telemetria()

    print(json.dumps(
        telemetria,
        indent=4,
        ensure_ascii=False
    ))
