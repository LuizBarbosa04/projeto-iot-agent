
from datetime import datetime
from statistics import mean

from historico_s3 import consultar_historico


def calcular_estatisticas():
    print("Consultando dados históricos...\n")

    leituras = consultar_historico()

    if not leituras:
        print("Nenhuma leitura encontrada.")
        return

    temperaturas = [
        leitura["temperatura"]
        for leitura in leituras
    ]

    umidades = [
        leitura["umidade"]
        for leitura in leituras
    ]

    datas = [
        datetime.fromisoformat(leitura["timestamp"])
        for leitura in leituras
    ]

    print("===== ESTATÍSTICAS HISTÓRICAS =====")
    print(f"Total de leituras: {len(leituras)}")

    print("\nTEMPERATURA")
    print(f"Média: {mean(temperaturas):.2f} °C")
    print(f"Mínima: {min(temperaturas):.2f} °C")
    print(f"Máxima: {max(temperaturas):.2f} °C")

    print("\nUMIDADE")
    print(f"Média: {mean(umidades):.2f}%")
    print(f"Mínima: {min(umidades):.2f}%")
    print(f"Máxima: {max(umidades):.2f}%")

    print("\nPERÍODO MONITORADO")
    print(f"Primeira leitura: {min(datas).isoformat()}")
    print(f"Última leitura: {max(datas).isoformat()}")


if __name__ == "__main__":
    calcular_estatisticas()
