
import json
from statistics import mean

from historico_s3 import consultar_historico
from detector import detectar_anomalias


def gerar_resumo_historico():
    leituras = consultar_historico()

    if not leituras:
        return {
            "total_leituras": 0,
            "mensagem": "Nenhuma leitura encontrada."
        }

    # Organizar as leituras cronologicamente
    leituras.sort(key=lambda item: item["timestamp"])

    temperaturas = []
    umidades = []
    total_alertas = 0
    tipos_alertas = {}
    somente_temperatura = 0
    somente_umidade = 0
    temperatura_e_umidade = 0

    for leitura in leituras:
        temperatura = leitura["temperatura"]
        umidade = leitura["umidade"]

        temperaturas.append(temperatura)
        umidades.append(umidade)

        resultado = detectar_anomalias(
            temperatura,
            umidade
        )
        alertas = resultado["alertas"]

        alerta_temperatura = any(
            "Temperatura" in alerta for alerta in alertas
        )

        alerta_umidade = any(
            "Umidade" in alerta for alerta in alertas
        )

        if alerta_temperatura and alerta_umidade:
            temperatura_e_umidade += 1
        elif alerta_temperatura:
            somente_temperatura += 1
        elif alerta_umidade:
            somente_umidade += 1

        if resultado["status"] == "ALERTA":
            total_alertas += 1

        for alerta in resultado["alertas"]:
            tipos_alertas[alerta] = (
                tipos_alertas.get(alerta, 0) + 1
            )

    total = len(leituras)

    resumo = {
        "total_leituras": total,
        "primeira_leitura": leituras[0]["timestamp"],
        "ultima_leitura": leituras[-1]["timestamp"],
        "temperatura": {
            "media": round(mean(temperaturas), 2),
            "minima": min(temperaturas),
            "maxima": max(temperaturas)
        },
        "umidade": {
            "media": round(mean(umidades), 2),
            "minima": min(umidades),
            "maxima": max(umidades)
        },
        "leituras_normais": total - total_alertas,
        "leituras_com_alerta": total_alertas,
        "percentual_alertas": round(
            (total_alertas / total) * 100, 2
        ),
        "tipos_alertas": tipos_alertas,
        "combinacoes_alertas": {
            "somente_temperatura": somente_temperatura,
            "somente_umidade": somente_umidade,
            "temperatura_e_umidade": temperatura_e_umidade
        },
    }

    return resumo


if __name__ == "__main__":
    print("Gerando resumo histórico do monitoramento...\n")

    resumo = gerar_resumo_historico()

    print(json.dumps(
        resumo,
        indent=4,
        ensure_ascii=False
    ))
