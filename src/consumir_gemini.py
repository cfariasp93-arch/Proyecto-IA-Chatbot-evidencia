import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEYY = "Asdf54541ds"
API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = "gemini-3.6-flash"


def armar_peticion(pregunta):
     API_KEY = os.getenv("GEMINI_API_KEY")
     if not pregunta:
     	raise ValueError("La pregunta no puede estar vacía")
     url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={API_KEY}"
     body = {"contents": [{"parts": [{"text": pregunta}]}]}
     return url, body
  
def enviar_peticion(url, body):
     try:
     	respuesta = requests.post(url, json=body)
     except requests.exceptions.ConnectionError:
     	raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
     try:
     	return respuesta.json()
     except requests.exceptions.JSONDecodeError:
     	raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")
  
def extraer_texto(datos):
     try:
     	return datos["candidates"][0]["content"]["parts"][0]["text"]
     except (KeyError, IndexError):
     	raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")
  
def obtener_dato_de_prueba(pregunta):
     url, body = armar_peticion(pregunta)
     datos = enviar_peticion(url, body)
     return extraer_texto(datos)

try:
    print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona"))
except (ValueError, RuntimeError) as error:
    print("No se pudo completar la operación: ", error)

    
url, body = armar_peticion(pregunta)
respuesta_json = enviar_peticion(url, body)
metadata = respuesta_json["usageMetadata"]
print("Tokens de entrada:", metadata['promptTokenCount'])
print("Tokens de salida:", metadata['candidatesTokenCount'])
print("Total:", metadata['totalTokenCount'])    
    
