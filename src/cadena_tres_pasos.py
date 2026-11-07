"""Bloque 18: extraer ideas, simplificarlas y organizarlas en viñetas."""

# import argparse 
# import json
# from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def construir_cadena(modelo):
    plantilla_extraer = PromptTemplate.from_template(
        "Extrae las tres ideas principales del siguiente texto. "
        "No agregues información:\n\n{texto}"
    )

    plantilla_simplificar = PromptTemplate.from_template(
        "Explica estas ideas con palabras sencillas para una "
        "persona sin conocimientos técnicos. "
        "Conserva su significado:\n\n{ideas}"
    )

    plantilla_formatear = PromptTemplate.from_template(
        "Organiza esta explicación en un máximo de tres viñetas. "
        "No agregues información ni introducción:\n\n{explicacion}"
    )

    extraer = plantilla_extraer | modelo | StrOutputParser()
    simplificar =plantilla_simplificar | modelo | StrOutputParser()
    formatear = plantilla_formatear | modelo | StrOutputParser()

    cadena = (
        extraer
        | (lambda resultado: {"ideas": resultado})
        | simplificar
        | (lambda resultado: {"explicacion": resultado})
        | formatear
    )

    return cadena

if __name__ == "__main__":
    load_dotenv()
    
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    cadena = construir_cadena(modelo)

    texto = """
    La tokenización divide un texto en unidades llamadas tokens.
    Un token puede corresponder a una palabra, parte de una palabra
    o un signo de puntuación. Los modelos de lenguaje procesan
    secuencias de tokens y generan su respuesta progresivamente.
    """
    
    resultado = cadena.invoke({"texto": texto})
    print(resultado)


































# Actividad / Pasos a realizar:
# 1) Modelo lea un texto y devuelva las ideas centrales
# 2) Reescribir de manera que sea más fácil de entender
# 3) Formatear en viñetas

# from dotenv import load_dotenv
# import os
# from langchain_google_genai import ChatGoogleGenerativeAI # Modelo
# from langchain_core.prompts import PromptTemplate  #Plantilla -> Prompt dinámico
# from langchain_core.output_parsers import StrOutputParser #Parsea la respuesta y la transforma en solo textos
# from langchain_core.prompts import ChatPromptTemplate

# load_dotenv()

# modelo = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.2, max_output_tokens=256)#temparatura son entre 0 a 1, mientras más alto más creativo y menos preciso, mientras más bajo más preciso y menos creativo

# # Paso 1: Leer un texto y devolver las ideas centrales
# plantilla_extraccion = PromptTemplate.from_template("Lee el siguiente texto y devuelve solo sus 3 puntos claves, uno por linea, sin desarrollarlo: \n \n {texto}")

# paso_extraccion = plantilla_extraccion | modelo | StrOutputParser()

# texto_prueba = (
#     "Los modelos de lenguaje grandes generan texto "

#     "prediciendo un token a la vez, basándose en el "

#     "texto que ya generaron antes. Cada token puede "

#     "ser una palabra completa, parte de una palabra, "

#     "o un signo de puntuación. Antes de que el modelo "

#     "genere una respuesta, el texto de entrada se "

#     "divide en tokens, un proceso llamado tokenización."
# )

# # puntos = paso_extraccion.invoke(
# #      {"texto": texto_prueba}
# #  )

# # print(puntos)

# # Paso 2: Reescribir de manera que sea más fácil de entender

# plantilla_simplificacion = PromptTemplate.from_template("Reescribe estos puntos en lenguaje simple, sin jerga tecnica, para alguien sin conocimientos previos: \n \n {puntos}")

# paso_simplificacion = plantilla_simplificacion | modelo | StrOutputParser()

# # simple = paso_simplificacion.invoke(
# #     {"puntos": puntos}
# # )

# # print(simple)

# # Paso 3: Formatear en viñetas
# plantilla_formato = PromptTemplate.from_template("Convierte este texto en una lista de viñetas markdown de maximo 3 lineas, sin introducción: \n \n {texto_simple}")

# paso_formato = plantilla_formato | modelo | StrOutputParser()

# # formato = paso_formato.invoke(
# #     {"texto_simple": simple}
# # )

# # print(formato)
# # mejor tenerlo en un solo paso o cadena

# #Sintaxis lambda -> lambda argumentos : expresion   

# cadena_tres_pasos = (
#     plantilla_extraccion 
#     | modelo 
#     | StrOutputParser()
#     | (lambda puntos: {"puntos": puntos}) 
#     | plantilla_simplificacion 
#     | modelo 
#     | StrOutputParser() 
#     | (lambda texto_simple: {"texto_simple": texto_simple})
#     | plantilla_formato 
#     | modelo 
#     | StrOutputParser()
# )

# respuesta = cadena_tres_pasos.invoke(
#     {"texto": texto_prueba} # El diccionario que corresponde al primer paso/accion inicial
# )

# print(respuesta)