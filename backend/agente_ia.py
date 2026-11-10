
import requests
from detector import detectar_anomalias

OLLAMA_URL = "http://localhost:11434/api/chat"
MODELO = "qwen3:8b"


def analisar_telemetria(temperatura, umidade):
    resultado = detectar_anomalias(temperatura, umidade)

    if resultado["status"] == "NORMAL":
        return {
            "deteccao": resultado,
            "analise_ia": "Leituras dentro dos limites configurados."
        }

    mensagem = f"""
    Você é um assistente técnico de monitoramento IoT.

    Um sistema Python já analisou os sensores e
    identificou os seguintes resultados:

    Temperatura: {resultado['temperatura']} °C
    Umidade: {resultado['umidade']}%
    Status: {resultado['status']}
    Alertas: {', '.join(resultado['alertas'])}

    Explique as anomalias identificadas e apresente
    recomendações objetivas em português.

    Não invente medições ou causas confirmadas.
    """

    resposta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "messages": [
                {"role": "user", "content": mensagem}
            ],
            "stream": False,
            "think": False
        },
        timeout=180
    )

    resposta.raise_for_status()

    return {
        "deteccao": resultado,
        "analise_ia": resposta.json()["message"]["content"]
    }


if __name__ == "__main__":
    print("Iniciando monitoramento inteligente...\n")

    resultado = analisar_telemetria(42, 25)

    print("DETECÇÃO AUTOMÁTICA:")
    print(resultado["deteccao"])

    print("\nANÁLISE DO QWEN3:")
    print(resultado["analise_ia"])
