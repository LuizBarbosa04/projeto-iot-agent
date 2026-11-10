
import json

import boto3

BUCKET = "scopo-estudo-luiz-2026"

session = boto3.Session(
    profile_name="scopo-lab",
    region_name="us-east-2"
)

s3 = session.client("s3")


def consultar_historico():
    historico = []

    paginador = s3.get_paginator("list_objects_v2")

    paginas = paginador.paginate(
        Bucket=BUCKET,
        Prefix="telemetria/"
    )

    for pagina in paginas:
        for arquivo in pagina.get("Contents", []):
            chave = arquivo["Key"]

            if not chave.endswith(".json"):
                continue

            resposta = s3.get_object(
                Bucket=BUCKET,
                Key=chave
            )

            conteudo = resposta["Body"].read()
            dados = json.loads(conteudo.decode("utf-8"))

            historico.append(dados)

    return historico


if __name__ == "__main__":
    print("Consultando histórico no Amazon S3...\n")

    leituras = consultar_historico()

    print(f"Total de leituras: {len(leituras)}\n")

    for indice, leitura in enumerate(leituras, start=1):
        print(f"LEITURA {indice}")
        print(json.dumps(
            leitura,
            indent=4,
            ensure_ascii=False
        ))
        print()
