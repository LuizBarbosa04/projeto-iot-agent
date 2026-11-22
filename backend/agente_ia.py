
import requests

from detector import detectar_anomalias
from gerenciador_ollama import iniciar_ollama, modelo_disponivel


# CONFIGURAÇÕES DO OLLAMA
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODELO = "qwen3:8b"

# LIMITES DOS SENSORES
TEMP_MIN = 20
TEMP_MAX = 35
UMIDADE_MIN = 40
UMIDADE_MAX = 80


def analisar_telemetria(temperatura, umidade):
    """
    Analisa a telemetria utilizando regras Python
    e interpretação do modelo Qwen3 via Ollama.
    """

    # 1. DETECÇÃO AUTOMÁTICA
    resultado = detectar_anomalias(
        temperatura,
        umidade
    )

    # 2. LEITURAS NORMAIS
    if resultado["status"] == "NORMAL":
        return {
            "deteccao": resultado,
            "analise_ia": (
                "Leituras dentro dos limites configurados."
            ),
            "ia_disponivel": None
        }

    # 3. PREPARAÇÃO DO PROMPT
    mensagem = f"""
Você é um assistente técnico de monitoramento IoT.

O detector Python já identificou as anomalias.
Sua função é interpretar os alertas e recomendar
ações de verificação.

LIMITES CONFIGURADOS:
Temperatura mínima: {TEMP_MIN} °C
Temperatura máxima: {TEMP_MAX} °C
Umidade mínima: {UMIDADE_MIN}%
Umidade máxima: {UMIDADE_MAX}%

LEITURA RECEBIDA:
Temperatura: {resultado['temperatura']} °C
Umidade: {resultado['umidade']}%
Status: {resultado['status']}
Alertas: {', '.join(resultado['alertas'])}

INSTRUÇÕES:
- Responda em português.
- Explique somente as anomalias identificadas.
- Utilize os limites informados.
- Não invente medições ou limites.
- Não apresente hipóteses como causas confirmadas.
- Forneça recomendações objetivas.
- Seja breve e técnico.
"""

    # 4. INICIALIZAÇÃO AUTOMÁTICA DO OLLAMA
    try:
        if not iniciar_ollama(timeout=30):
            raise RuntimeError(
                "Não foi possível iniciar o servidor Ollama."
            )

        # 5. VERIFICAÇÃO DO MODELO
        if not modelo_disponivel():
            raise RuntimeError(
                f"O modelo {MODELO} não está instalado."
            )

        # 6. ANÁLISE COM QWEN3
        resposta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "messages": [
                    {
                        "role": "user",
                        "content": mensagem
                    }
                ],
                "stream": False,
                "think": False
            },
            timeout=180
        )

        resposta.raise_for_status()

        analise = resposta.json()["message"]["content"]

        return {
            "deteccao": resultado,
            "analise_ia": analise,
            "ia_disponivel": True
        }

    # 7. TRATAMENTO DE FALHAS
    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
        RuntimeError
    ) as erro:

        return {
            "deteccao": resultado,
            "analise_ia": (
                "Análise generativa indisponível. "
                "Os alertas foram identificados "
                "pelo detector Python. "
                f"Alertas: {', '.join(resultado['alertas'])}."
            ),
            "ia_disponivel": False,
            "erro_ia": str(erro)
        }


# 8. EXECUÇÃO DIRETA
if __name__ == "__main__":

    print("Iniciando monitoramento inteligente...\n")

    resultado = analisar_telemetria(
        temperatura=42,
        umidade=25
    )

    print("\nDETECÇÃO AUTOMÁTICA:")
    print(resultado["deteccao"])

    print("\nSTATUS DA IA:")
    print(resultado["ia_disponivel"])

    print("\nANÁLISE:")
    print(resultado["analise_ia"])

    if resultado["ia_disponivel"] is False:
        print("\nDETALHES DA FALHA:")
        print(resultado.get("erro_ia"))
