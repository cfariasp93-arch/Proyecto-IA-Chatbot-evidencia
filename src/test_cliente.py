from unittest.mock import patch, Mock
import pytest
import cliente
from cliente import con_reintento, registrar_costo, consultar_modelo

from consumir_gemini import enviar_peticion

RESPUESTA_GEMINI = {
    "candidates": [{"content": {"parts": [{"text": "respuesta simulada"}]}}],
    "usageMetadata": {"totalTokenCount": 500},
}

@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    cliente.costo_total_sesion = 0.0
    yield

def test_enviar_peticion_credencial_invalida():
    respuesta_falsa = Mock(status_code=401)

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})

def test_enviar_peticion_limite_de_uso():
    respuesta_falsa = Mock(status_code=429)

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion("https://ejemplo.invalid",{"pregunta": "test"})

@pytest.mark.parametrize("codigo", [500, 503])
def test_enviar_peticion_error_del_proveedor(codigo):
    respuesta_falsa = Mock(status_code=codigo)

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})

def test_enviar_peticion_exito():
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})

    assert resultado == {"texto": "respuesta simulada"}

def test_con_reintento_reintenta_tras_timeout():
    funcion = Mock(side_effect=[TimeoutError("429"), "ok"])

    with patch("cliente.time.sleep"):
        resultado = con_reintento(funcion)

    assert resultado == "ok"
    assert funcion.call_count == 2

def test_con_reintento_espera_con_backoff_y_jitter():
    funcion = Mock(side_effect=[TimeoutError(), TimeoutError(), "ok"])

    with patch("cliente.time.sleep") as mock_sleep:
        con_reintento(funcion, intentos=3, espera_base=2)

    esperas = [llamada.args[0] for llamada in mock_sleep.call_args_list]
    assert len(esperas) == 2
    # Backoff de 2s y 4s, con jitter de hasta 10 %
    assert 2 <= esperas[0] <= 2.2
    assert 4 <= esperas[1] <= 4.4

def test_con_reintento_agota_intentos():
    funcion = Mock(side_effect=TimeoutError("429"))

    with patch("cliente.time.sleep"):
        with pytest.raises(TimeoutError):
            con_reintento(funcion, intentos=3)

    assert funcion.call_count == 3

def test_con_reintento_no_reintenta_value_error():
    funcion = Mock(side_effect=ValueError("credencial inválida"))

    with patch("cliente.time.sleep"):
        with pytest.raises(ValueError):
            con_reintento(funcion)

    assert funcion.call_count == 1

def test_registrar_costo_acumula():
    respuesta = {"usageMetadata": {"totalTokenCount": 1000}}

    costo = registrar_costo(respuesta)
    registrar_costo(respuesta)

    assert costo == pytest.approx(0.002)
    assert cliente.costo_total_sesion == pytest.approx(0.004)

def test_consultar_modelo_flujo_completo():
    with patch("cliente.enviar_peticion", return_value=RESPUESTA_GEMINI):
        texto = consultar_modelo("¿Puedo devolver este producto?")

    assert texto == "respuesta simulada"
    assert cliente.costo_total_sesion > 0

def test_consultar_modelo_convierte_timeout_en_runtime_error():
    with patch("cliente.enviar_peticion", side_effect=TimeoutError("429")) as mock_envio:
        with patch("cliente.time.sleep"):
            with pytest.raises(RuntimeError):
                consultar_modelo("¿Puedo devolver este producto?")

    assert mock_envio.call_count == 3