
from unittest.mock import patch

from resumo_historico import gerar_resumo_historico


def test_resumo_sem_leituras():
    # Simula um histórico vazio, sem acessar o S3.
    with patch(
        "resumo_historico.consultar_historico",
        return_value=[]
    ):
        resultado = gerar_resumo_historico()

    assert resultado["total_leituras"] == 0
    assert resultado["mensagem"] == (
        "Nenhuma leitura encontrada."
    )


def test_resumo_com_anomalias():
    leituras_simuladas = [
        {
            "timestamp": "2026-11-10T10:00:00+00:00",
            "temperatura": 25,
            "umidade": 60
        },
        {
            "timestamp": "2026-11-10T10:01:00+00:00",
            "temperatura": 38,
            "umidade": 60
        },
        {
            "timestamp": "2026-11-10T10:02:00+00:00",
            "temperatura": 25,
            "umidade": 30
        },
        {
            "timestamp": "2026-11-10T10:03:00+00:00",
            "temperatura": 40,
            "umidade": 25
        }
    ]

    with patch(
        "resumo_historico.consultar_historico",
        return_value=leituras_simuladas
    ):
        resultado = gerar_resumo_historico()

    assert resultado["total_leituras"] == 4
    assert resultado["leituras_normais"] == 1
    assert resultado["leituras_com_alerta"] == 3
    assert resultado["percentual_alertas"] == 75.0

    assert resultado["temperatura"]["media"] == 32.0
    assert resultado["temperatura"]["minima"] == 25
    assert resultado["temperatura"]["maxima"] == 40

    assert resultado["umidade"]["media"] == 43.75
    assert resultado["umidade"]["minima"] == 25
    assert resultado["umidade"]["maxima"] == 60

    combinacoes = resultado["combinacoes_alertas"]

    assert combinacoes["somente_temperatura"] == 1
    assert combinacoes["somente_umidade"] == 1
    assert combinacoes["temperatura_e_umidade"] == 1

    assert resultado["tipos_alertas"][
        "Temperatura acima do limite"
    ] == 2

    assert resultado["tipos_alertas"][
        "Umidade abaixo do limite"
    ] == 2


def test_valores_exatamente_nos_limites():
    leituras_simuladas = [
        {
            "timestamp": "2026-11-10T10:00:00+00:00",
            "temperatura": 20,
            "umidade": 40
        },
        {
            "timestamp": "2026-11-10T10:01:00+00:00",
            "temperatura": 35,
            "umidade": 80
        }
    ]

    with patch(
        "resumo_historico.consultar_historico",
        return_value=leituras_simuladas
    ):
        resultado = gerar_resumo_historico()

    assert resultado["total_leituras"] == 2
    assert resultado["leituras_normais"] == 2
    assert resultado["leituras_com_alerta"] == 0
    assert resultado["percentual_alertas"] == 0

    combinacoes = resultado["combinacoes_alertas"]

    assert combinacoes["somente_temperatura"] == 0
    assert combinacoes["somente_umidade"] == 0
    assert combinacoes["temperatura_e_umidade"] == 0

    assert resultado["tipos_alertas"] == {}
