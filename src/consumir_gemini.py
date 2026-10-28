import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = "gemini-3.6-flash"


def obtener_dato_de_prueba(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-3.6-flash"
    
    
    
    url =f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
    body = {
    "contents": [
      {
        "parts": [
          {
            "text": pregunta
          }
        ]
      }
    ]
}
    respuesta = requests.post(url, json=body)
    #print(respuesta)
    datos = respuesta.json()
    return datos["candidates"][0]["content"]["parts"][0]["text"]
    
print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona"))

def armar_peticion(pregunta):
     API_KEY = os.getenv("GEMINI_API_KEY")
     url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={API_KEY}"
     body = {"contents": [{"parts": [{"text": pregunta}]}]}
     return url, body
  
def enviar_peticion(url, body):
     respuesta = requests.post(url, json=body)
     return respuesta.json()
  
def extraer_texto(datos):
     return datos["candidates"][0]["content"]["parts"][0]["text"]
  
def obtener_dato_de_prueba(pregunta):
     url, body = armar_peticion(pregunta)
     datos = enviar_peticion(url, body)
     return extraer_texto(datos)


print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona"))

    
    
    
