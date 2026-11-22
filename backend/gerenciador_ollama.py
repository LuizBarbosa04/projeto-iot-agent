
import shutil
import subprocess
import time

import requests


OLLAMA_URL = "http://127.0.0.1:11434"
MODELO = "qwen3:8b"


def ollama_disponivel():
    """Verifica se o servidor Ollama está respondendo."""
    try:
        resposta = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=2
        )
        resposta.raise_for_status()
        return True
    except requests.RequestException:
        return False


def iniciar_ollama(timeout=30):
    """Inicia o servidor Ollama se ele não estiver ativo."""

    if ollama_disponivel():
        print("Ollama já está funcionando.")
        return True

    executavel = shutil.which("ollama")

    if not executavel:
        print("Executável do Ollama não encontrado.")
        return False

    print("Ollama está desligado. Iniciando automaticamente...")

    try:
        processo = subprocess.Popen(
            [executavel, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(
                subprocess,
                "CREATE_NO_WINDOW",
                0
            )
        )
    except OSError as erro:
        print(f"Não foi possível iniciar o Ollama: {erro}")
        return False

    inicio = time.monotonic()

    while time.monotonic() - inicio < timeout:
        if ollama_disponivel():
            print("Ollama iniciado com sucesso.")
            return True

        if processo.poll() is not None:
            print("O processo Ollama encerrou durante a inicialização.")
            return False

        time.sleep(1)

    print("Tempo limite excedido ao iniciar o Ollama.")
    return False


def modelo_disponivel():
    """Confirma que o modelo já está instalado localmente."""
    try:
        resposta = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=5
        )
        resposta.raise_for_status()

        modelos = resposta.json().get("models", [])

        return any(
            modelo.get("name") == MODELO
            for modelo in modelos
        )

    except (requests.RequestException, ValueError, TypeError):
        return False


if __name__ == "__main__":
    if iniciar_ollama():
        if modelo_disponivel():
            print(f"Modelo {MODELO} disponível.")
        else:
            print(f"Modelo {MODELO} não encontrado localmente.")
