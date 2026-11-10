
from datetime import datetime

import matplotlib.pyplot as plt

from historico_s3 import consultar_historico

from detector import detectar_anomalias


def gerar_graficos():
    print("Consultando histórico no Amazon S3...")

    leituras = consultar_historico()

    if not leituras:
        print("Nenhuma leitura encontrada.")
        return

    # Ordenar os registros pela data da medição
    leituras.sort(key=lambda item: item["timestamp"])

    datas = [
        datetime.fromisoformat(item["timestamp"])
        for item in leituras
    ]

    temperaturas = [
        item["temperatura"]
        for item in leituras
    ]

    umidades = [
        item["umidade"]
        for item in leituras
    ]

    anomalias_temperatura = []
    anomalias_umidade = []

    for leitura in leituras:
        resultado = detectar_anomalias(
            leitura["temperatura"],
            leitura["umidade"]
        )

        anomalias_temperatura.append(
            any("Temperatura" in alerta for alerta in resultado["alertas"])
        )

        anomalias_umidade.append(
            any("Umidade" in alerta for alerta in resultado["alertas"])
        )

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 7), sharex=True
    )

    # Gráfico de temperatura
    ax1.plot(datas, temperaturas, marker="o")
    ax1.scatter(
        [data for data, alerta in zip(datas, anomalias_temperatura) if alerta],
        [valor for valor, alerta in zip(temperaturas, anomalias_temperatura) if alerta],
        color="red",
        s=100,
        zorder=5,
        label="Anomalia detectada"
    )
    ax1.axhline(
        y=35,
        color="red",
        linestyle="--",
        label="Limite máximo: 35 °C"
    )
    ax1.axhline(
        y=20,
        color="orange",
        linestyle="--",
        label="Limite mínimo: 20 °C"
    )
    ax1.set_ylabel("Temperatura (°C)")
    ax1.set_title("Histórico de temperatura")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Gráfico de umidade
    ax2.plot(datas, umidades, marker="o")
    ax2.scatter(
        [data for data, alerta in zip(datas, anomalias_umidade) if alerta],
        [valor for valor, alerta in zip(umidades, anomalias_umidade) if alerta],
        color="red",
        s=100,
        zorder=5,
        label="Anomalia detectada"
    )
    ax2.axhline(
        y=80,
        color="red",
        linestyle="--",
        label="Limite máximo: 80%"
    )
    ax2.axhline(
        y=40,
        color="orange",
        linestyle="--",
        label="Limite mínimo: 40%"
    )
    ax2.set_ylabel("Umidade (%)")
    ax2.set_xlabel("Data e hora (UTC)")
    ax2.set_title("Histórico de umidade")
    ax2.legend()
    ax2.grid(alpha=0.3)


    from matplotlib.dates import DateFormatter, AutoDateLocator

    localizador = AutoDateLocator()

    ax2.xaxis.set_major_locator(localizador)
    ax2.xaxis.set_major_formatter(
        DateFormatter("%H:%M:%S", tz=datas[0].tzinfo)
    )

    plt.setp(
        ax2.get_xticklabels(),
        rotation=45,
        ha="right"
    )

    ax2.set_xlabel("Horário da medição (UTC)")

    plt.tight_layout()

    plt.savefig("historico_sensores.png", dpi=150)
    print("Gráfico salvo em historico_sensores.png")

    plt.show()


if __name__ == "__main__":
    gerar_graficos()

