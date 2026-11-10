
from consultar_s3 import consultar_telemetria
from agente_ia import analisar_telemetria


def executar_monitoramento():
    print("Consultando dados no Amazon S3...\n")

    dados = consultar_telemetria()

    print(f"Dispositivo: {dados['dispositivo']}")
    print(f"Temperatura: {dados['temperatura']} °C")
    print(f"Umidade: {dados['umidade']}%")

    print("\nAnalisando telemetria...\n")

    resultado = analisar_telemetria(
        temperatura=dados["temperatura"],
        umidade=dados["umidade"]
    )

    print("DETECÇÃO AUTOMÁTICA:")
    print(resultado["deteccao"])

    print("\nANÁLISE DA IA:")
    print(resultado["analise_ia"])


if __name__ == "__main__":
    executar_monitoramento()
