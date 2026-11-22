
import json

import boto3
from botocore.exceptions import BotoCoreError, ClientError


BUCKET = "scopo-estudo-luiz-2026"
REGIAO = "us-east-2"
PERFIL = "scopo-lab"
PREFIXO = "telemetria/"


def criar_cliente_s3():
    """Cria o cliente AWS S3 somente quando necessário."""

    session = boto3.Session(
        profile_name=PERFIL,
        region_name=REGIAO
    )

    return session.client("s3")


def consultar_telemetria():
    """Retorna a leitura JSON mais recentemente modificada no S3."""

    s3 = criar_cliente_s3()

    try:
        paginador = s3.get_paginator("list_objects_v2")

        paginas = paginador.paginate(
            Bucket=BUCKET,
            Prefix=PREFIXO
        )

        arquivo_recente = None

        for pagina in paginas:
            for arquivo in pagina.get("Contents", []):
                if not arquivo["Key"].endswith(".json"):
                    continue

                if (
                    arquivo_recente is None
                    or arquivo["LastModified"] > arquivo_recente["LastModified"]
                ):
                    arquivo_recente = arquivo

        if arquivo_recente is None:
            raise ValueError(
                "Nenhuma telemetria JSON encontrada no S3."
            )

        resposta = s3.get_object(
            Bucket=BUCKET,
            Key=arquivo_recente["Key"]
        )

        conteudo = resposta["Body"].read()

        dados = json.loads(
            conteudo.decode("utf-8")
        )

        return dados

    except (BotoCoreError, ClientError) as erro:
        print(f"Erro ao consultar o S3: {erro}")
        raise


if __name__ == "__main__":
    print("Consultando telemetria no Amazon S3...\n")

    telemetria = consultar_telemetria()

    print(
        json.dumps(
            telemetria,
            indent=4,
            ensure_ascii=False
        )
    )
