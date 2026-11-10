
def detectar_anomalias(temperatura, umidade):
    alertas = []

    if temperatura < 20:
        alertas.append("Temperatura abaixo do limite")
    elif temperatura > 35:
        alertas.append("Temperatura acima do limite")

    if umidade < 40:
        alertas.append("Umidade abaixo do limite")
    elif umidade > 80:
        alertas.append("Umidade acima do limite")

    return {
        "temperatura": temperatura,
        "umidade": umidade,
        "status": "ALERTA" if alertas else "NORMAL",
        "alertas": alertas
    }


if __name__ == "__main__":
    resultado = detectar_anomalias(42, 25)
    print(resultado)
