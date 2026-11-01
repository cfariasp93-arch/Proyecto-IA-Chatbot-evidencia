import os
import requests
from dotenv import load_dotenv
 
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY2")
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
MODELO = "gemini-3.6-flash"
 
 
def calcular_costo(datos, precio_entrada, precio_salida):
    uso = datos["usageMetadata"]
    tokens_entrada = uso["promptTokenCount"]
    # CAMBIO: los tokens de razonamiento se cobran como salida y vienen aparte
    tokens_salida = uso.get("candidatesTokenCount", 0) + uso.get("thoughtsTokenCount", 0)
    return (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)
 
 
def armar_peticion(pregunta, modelo=MODELO, *, system_instruction=None, response_schema=None):
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía")
    url = f"{URL_BASE}{modelo}:generateContent?key={API_KEY}"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if response_schema:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return url, body
 
 
def enviar_peticion(url, body):
    try:
        respuesta = requests.post(url, json=body)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")

    # NUEVO: traducir códigos HTTP a las excepciones que el resto del código ya maneja
    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permisos. Revisa tu GEMINI_API_KEY.")
    if respuesta.status_code == 429 or respuesta.status_code >= 500:
        raise TimeoutError(f"El servicio no está disponible (HTTP {respuesta.status_code}). Se reintentará.")

    try:
        datos = respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")
    if isinstance(datos, dict) and "error" in datos:
        error = datos["error"]
        mensaje = error.get("message", error) if isinstance(error, dict) else error
        raise RuntimeError(f"El servicio devolvió un error: {mensaje}")
    return datos
 
 
def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")
 
 
def obtener_dato_de_prueba(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)
 
 
# CAMBIO: la prueba de conexión solo corre si ejecutas este archivo directamente
if __name__ == "__main__":
    try:
        print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona"))
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación: ", error)
