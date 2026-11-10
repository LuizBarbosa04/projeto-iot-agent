
import json

import requests
from pathlib import Path
from datetime import datetime, timezone

from resumo_historico import gerar_resumo_historico


OLLAMA_URL = "http://localhost:11434/api/chat"
MODELO = "qwen3:8b"


def gerar_relatorio_ia():
    print("Consultando histórico no Amazon S3...")

    resumo = gerar_resumo_historico()

    if resumo["total_leituras"] == 0:
        return "Não existem leituras para análise."

    combinacoes = resumo["combinacoes_alertas"]

    # Parte numérica: produzida exclusivamente pelo Python
    relatorio_dados = f"""
# RELATÓRIO TÉCNICO DE MONITORAMENTO IoT

## 1. Dados verificados pelo Python

Período:
{resumo["primeira_leitura"]}
até {resumo["ultima_leitura"]}

Total de leituras: {resumo["total_leituras"]}
Leituras normais: {resumo["leituras_normais"]}
Leituras com alerta: {resumo["leituras_com_alerta"]}
Percentual de alertas: {resumo["percentual_alertas"]}%

Temperatura:
- Média: {resumo["temperatura"]["media"]} °C
- Mínima: {resumo["temperatura"]["minima"]} °C
- Máxima: {resumo["temperatura"]["maxima"]} °C
- Acima do limite: {resumo["tipos_alertas"].get("Temperatura acima do limite", 0)}

Umidade:
- Média: {resumo["umidade"]["media"]}%
- Mínima: {resumo["umidade"]["minima"]}%
- Máxima: {resumo["umidade"]["maxima"]}%
- Abaixo do limite: {resumo["tipos_alertas"].get("Umidade abaixo do limite", 0)}

Combinações:
- Somente temperatura: {combinacoes["somente_temperatura"]}
- Somente umidade: {combinacoes["somente_umidade"]}
- Ambas simultaneamente: {combinacoes["temperatura_e_umidade"]}
"""

    prompt = f"""
Você é um analista técnico especializado em IoT.

Os dados abaixo foram calculados e validados pelo Python:

{json.dumps(resumo, indent=2, ensure_ascii=False)}

Produza APENAS as seguintes seções:

## 2. Interpretação técnica
## 3. Limitações da análise
## 4. Recomendações técnicas
## 5. Conclusão

REGRAS:
- Não reproduza tabelas ou estatísticas numéricas.
- Não informe novas quantidades ou percentuais.
- Não invente tendências, correlações ou causas.
- Não afirme problemas reais de hardware.
- Os sensores são simulados.
- Os limites de alerta são demonstrativos.
- Utilize português brasileiro.
- Seja objetivo e profissional.
"""

    print("Solicitando interpretação ao Qwen3 8B...\n")

    resposta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "think": False
        },
        timeout=180
    )

    resposta.raise_for_status()

    interpretacao = resposta.json()["message"]["content"]

    return relatorio_dados + "\n" + interpretacao


if __name__ == "__main__":
    try:
        relatorio = gerar_relatorio_ia()

        print("===== RELATÓRIO INTELIGENTE =====\n")
        print(relatorio)

        pasta_relatorios = (
            Path(__file__).resolve().parent / "relatorios"
        )

        pasta_relatorios.mkdir(
            parents=True,
            exist_ok=True
        )

        data_geracao = datetime.now(
            timezone.utc
        ).strftime("%Y-%m-%d_%H-%M-%S")

        arquivo = (
            pasta_relatorios /
            f"relatorio_{data_geracao}.md"
        )

        arquivo.write_text(
            relatorio,
            encoding="utf-8"
        )

        print(f"\nRelatório salvo em: {arquivo}")

    except requests.RequestException as erro:
        print(f"Erro de comunicação com o Ollama: {erro}")
