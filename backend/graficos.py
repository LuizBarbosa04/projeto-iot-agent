
from pathlib import Path
from datetime import datetime, timezone

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator

from historico_s3 import consultar_historico


# Configurações
DIRETORIO_BASE = Path(__file__).resolve().parent
DIRETORIO_ASSETS = DIRETORIO_BASE / "assets"
CAMINHO_GRAFICO = DIRETORIO_ASSETS / "historico_sensores.png"

TEMPERATURA_MINIMA = 20
TEMPERATURA_MAXIMA = 35

UMIDADE_MINIMA = 40
UMIDADE_MAXIMA = 80


def converter_data(valor):
    """Converte uma data ISO 8601 para datetime com fuso horário."""

    if isinstance(valor, datetime):
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)

    if not isinstance(valor, str):
        raise ValueError("Data inválida")

    data = datetime.fromisoformat(valor.replace("Z", "+00:00"))

    if data.tzinfo is None:
        data = data.replace(tzinfo=timezone.utc)

    return data.astimezone(timezone.utc)


def gerar_graficos():
    """Consulta o histórico no S3 e gera gráficos de temperatura e umidade."""

    print("Consultando histórico de telemetria no Amazon S3...")

    historico = consultar_historico()

    if not historico:
        print("Nenhum dado de telemetria encontrado.")
        return

    leituras = []

    for registro in historico:
        try:
            data = converter_data(registro["timestamp"])
            temperatura = float(registro["temperatura"])
            umidade = float(registro["umidade"])

            leituras.append(
                {
                    "data": data,
                    "temperatura": temperatura,
                    "umidade": umidade,
                }
            )

        except (KeyError, TypeError, ValueError) as erro:
            print(f"Registro ignorado por dados inválidos: {erro}")

    if not leituras:
        print("Nenhuma leitura válida disponível para gerar gráficos.")
        return

    # Organizar leituras cronologicamente
    leituras.sort(key=lambda registro: registro["data"])

    datas = [registro["data"] for registro in leituras]
    temperaturas = [registro["temperatura"] for registro in leituras]
    umidades = [registro["umidade"] for registro in leituras]

    # Detectar anomalias utilizando os limites de monitoramento
    anomalias_temperatura = [
        valor < TEMPERATURA_MINIMA or valor > TEMPERATURA_MAXIMA
        for valor in temperaturas
    ]

    anomalias_umidade = [
        valor < UMIDADE_MINIMA or valor > UMIDADE_MAXIMA
        for valor in umidades
    ]

    # Criar figura com dois gráficos
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(13, 9),
        sharex=True,
    )

    # Gráfico de temperatura
    ax1.plot(
        datas,
        temperaturas,
        marker="o",
        label="Temperatura",
    )

    ax1.scatter(
        [
            data
            for data, alerta in zip(datas, anomalias_temperatura)
            if alerta
        ],
        [
            valor
            for valor, alerta in zip(temperaturas, anomalias_temperatura)
            if alerta
        ],
        color="red",
        s=100,
        zorder=5,
        label="Anomalia detectada",
    )

    ax1.axhline(
        y=TEMPERATURA_MAXIMA,
        color="red",
        linestyle="--",
        label=f"Limite máximo: {TEMPERATURA_MAXIMA} °C",
    )

    ax1.axhline(
        y=TEMPERATURA_MINIMA,
        color="orange",
        linestyle="--",
        label=f"Limite mínimo: {TEMPERATURA_MINIMA} °C",
    )

    ax1.set_ylabel("Temperatura (°C)")
    ax1.set_title("Histórico de temperatura")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Gráfico de umidade
    ax2.plot(
        datas,
        umidades,
        marker="o",
        label="Umidade",
    )

    ax2.scatter(
        [
            data
            for data, alerta in zip(datas, anomalias_umidade)
            if alerta
        ],
        [
            valor
            for valor, alerta in zip(umidades, anomalias_umidade)
            if alerta
        ],
        color="red",
        s=100,
        zorder=5,
        label="Anomalia detectada",
    )

    ax2.axhline(
        y=UMIDADE_MAXIMA,
        color="red",
        linestyle="--",
        label=f"Limite máximo: {UMIDADE_MAXIMA}%",
    )

    ax2.axhline(
        y=UMIDADE_MINIMA,
        color="orange",
        linestyle="--",
        label=f"Limite mínimo: {UMIDADE_MINIMA}%",
    )

    ax2.set_ylabel("Umidade (%)")
    ax2.set_xlabel("Horário da medição (UTC)")
    ax2.set_title("Histórico de umidade")
    ax2.legend()
    ax2.grid(alpha=0.3)

    # Formatação do eixo temporal
    localizador = AutoDateLocator()

    ax2.xaxis.set_major_locator(localizador)
    ax2.xaxis.set_major_formatter(
        DateFormatter("%H:%M:%S", tz=timezone.utc)
    )

    plt.setp(
        ax2.get_xticklabels(),
        rotation=45,
        ha="right",
    )

    plt.tight_layout()

    # Salvar gráfico em assets/
    DIRETORIO_ASSETS.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        CAMINHO_GRAFICO,
        dpi=150,
        bbox_inches="tight",
    )

    print(f"Gráfico salvo em: {CAMINHO_GRAFICO}")

    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    gerar_graficos()
