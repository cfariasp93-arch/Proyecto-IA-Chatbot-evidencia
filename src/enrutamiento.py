from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI #Modelo
from langchain_core.prompts import PromptTemplate #Plantilla -> Prompt dinámico
from langchain_core.output_parsers import StrOutputParser #Parsea la respuesta y la transforma en solo textos
from langchain_core.runnables import (RunnableBranch, RunnablePassthrough, RunnableLambda) #Bifurcaciones/Branches/Ramificaciones

import logging # Me permite crea un archivo de log con los errores que se presenten


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="error.log",
    filemode="a",
    encoding="utf-8",
    force=True
)
logger = logging.getLogger(__name__)



load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")#temparatura son entre 0 a 1, mientras más alto más creativo y menos preciso, mientras más bajo más preciso y menos creativo

planilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de soporte en una sola palabra: "
    "pregunta, queja o sugerencia. Responde solo con una palabra: \n \n {mensaje}"
)

paso_clasificacion = (
    planilla_clasificacion 
    | modelo 
    | StrOutputParser()
    | (lambda texto: texto.strip().lower())  # Normaliza la salida a minúsculas y sin espacios
)

# mensaje_prueba = "mi telefono no esta funcionando"

# clasificacion = paso_clasificacion.invoke(
#     {"mensaje": mensaje_prueba}
# )  

# print(clasificacion)

cadena_pregunta = (
    PromptTemplate.from_template("Responde esta pregunta técnica con precisión: \n\n {mensaje}")
    | modelo
    | StrOutputParser()
)

cadena_queja = (
    PromptTemplate.from_template("Responde esta queja con empatía, reconociendo el problema antes de ofrecer una solución: \n\n {mensaje}")
    | modelo
    | StrOutputParser()
)

cadena_sugerencia = (
    PromptTemplate.from_template("Agradee esta sugerencia y explica cómo se evaluara dentro del producto: \n\n {mensaje}")
    | modelo
    | StrOutputParser()
)


# Sintaxis de RunnableBranch
# caminos = (
#     (condicion1, rama_1),#if
#     (condicion2, rama_2),#elif
#     (condicion3, rama_3),#elif
#     rama_por_defecto#else
# ) #Cada condicion debe ser una funcion; suele ser un lambda

bifurcacion = RunnableBranch(
    (lambda x: x["clasificacion"] == "queja", cadena_queja),
    (lambda x: x["clasificacion"] == "sugerencia", cadena_sugerencia),
    cadena_pregunta  # Rama por defecto
)

cadena_con_enrutamiento = (
    RunnablePassthrough.assign(clasificacion=paso_clasificacion) 
    | bifurcacion   
)

# Fallback: Cadena de respald. Ca´tira las caides de mi llm.

def fallback_con_log(x):
    logger.warning("Cadena principal fallo.")
    return "Gracias por tu mensaje. Intenta mas tarde"

respuesta_generica = RunnableLambda(
    fallback_con_log
)

cadena_robusta = cadena_con_enrutamiento.with_fallbacks([respuesta_generica])


def procesar_mensaje_seguro(cadena,mensaje):
    try:
        return cadena. invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error("Error al procesar el mensaje: %s", error)
        return "No pudimos procesar tu mensaje en este momento. Intenta de nuevo más tarde"   
       

if __name__ == "__main__":
    mensaje = "llevo varios dias sin poder entrar a mi cuenta."
    print(procesar_mensaje_seguro(cadena_robusta, mensaje))

# resultado = cadena_con_enrutamiento.invoke(
#     {"mensaje": "deberian de tener más agentes disponibles."}
# )

# print(resultado)


