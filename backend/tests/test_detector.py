
import pytest

from detector import detectar_anomalias


@pytest.mark.parametrize(
    "temperatura, umidade, status, alertas_esperados",
    [
        (25, 60, "NORMAL", []),
        (20, 40, "NORMAL", []),
        (35, 80, "NORMAL", []),
        (19, 60, "ALERTA", ["Temperatura abaixo do limite"]),
        (36, 60, "ALERTA", ["Temperatura acima do limite"]),
        (25, 39, "ALERTA", ["Umidade abaixo do limite"]),
        (25, 81, "ALERTA", ["Umidade acima do limite"]),
        (
            42, 25, "ALERTA",
            [
                "Temperatura acima do limite",
                "Umidade abaixo do limite",
            ],
        ),
        (
            15, 90, "ALERTA",
            [
                "Temperatura abaixo do limite",
                "Umidade acima do limite",
            ],
        ),
    ],
)
def test_detectar_anomalias(
    temperatura,
    umidade,
    status,
    alertas_esperados,
):
    resultado = detectar_anomalias(temperatura, umidade)

    assert resultado["temperatura"] == temperatura
    assert resultado["umidade"] == umidade
    assert resultado["status"] == status
    assert resultado["alertas"] == alertas_esperados
