
from historico_s3 import consultar_historico
from detector import detectar_anomalias


def analisar_historico():
    print("Consultando histórico no Amazon S3...\n")

    leituras = consultar_historico()

    total = len(leituras)
    normais = 0
    alertas = 0

    for indice, leitura in enumerate(leituras, start=1):
        resultado = detectar_anomalias(
            temperatura=leitura["temperatura"],
            umidade=leitura["umidade"]
        )

        print(f"LEITURA {indice}")
        print(f"Dispositivo: {leitura['dispositivo']}")
        print(f"Data: {leitura['timestamp']}")
        print(f"Temperatura: {leitura['temperatura']} °C")
        print(f"Umidade: {leitura['umidade']}%")
        print(f"Classificação: {resultado['status']}")

        if resultado["status"] == "ALERTA":
            alertas += 1

            for alerta in resultado["alertas"]:
                print(f"  - {alerta}")
        else:
            normais += 1

        print()

    print("===== RESUMO DO MONITORAMENTO =====")
    print(f"Total de leituras: {total}")
    print(f"Leituras normais: {normais}")
    print(f"Leituras com alerta: {alertas}")

    if total > 0:
        percentual = (alertas / total) * 100
        print(f"Percentual de alertas: {percentual:.2f}%")


if __name__ == "__main__":
    analisar_historico()
