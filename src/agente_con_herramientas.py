from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

#Tool/herramienta es uan funcion comun de python, Descripción en lenguaje natura sera lo que el model lea  para decidir si elige o no esa herrramienta


@tool
def buscar_en_documentacion(consulta:str) -> str:
    """
    Busca informacion relevante de la documentar interna del producto.
    Usar cuando la pregunta es sobre como funciona algo del sistema.
    """
    documentacion = {
        "reintentos": "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente",
        "costos": "El costo se calcula a partir del totalTokenCount, según la tarifa vigente."
    }
    
    for clave, texto in documentacion.items():
        if clave in consulta.lower():
            return texto
    return "No se encontró información sobre esa consulta en la documentación."

   
@tool
def calcular(expresion: str) -> str:
    """
    Calcula una expresión matemática simple, como '350 + 250'.
    Usar cuando la pregunta es sobre cálculos matemáticos.
    """
    permitido = set("0123456789+-*/(). ")
    if not set(expresion) <= permitido:
        return "Expresión no permitida."
    try:
        return str(eval(expresion))
    except Exception as e:
        return f"Error al evaluar: {e}"
    
herramientas = [buscar_en_documentacion, calcular] # Lista de herramientas

#PLANTILLA,con systemm_instrucions
prompt_agente = ChatPromptTemplate.from_messages([
    (
    "system", "eres un asistente que responde preguntas usando las herramientas disponibles cuando las necesites."
    ),
    (
        "human", "{entrada}"
    ),
    MessagesPlaceholder("agent_scratchpad") #El espacio dodne langchain va anotando, paso/ciclos  razonar-actuar-observar, que herramients llamo y que devolvieron
])

# Agente: modelo, herramients, prompt, formato

agente = create_tool_calling_agent(
    modelo, herramientas, prompt_agente
)

#Orquestador: es el que controla el ciclo entre razonar-actuar-observar
ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=True, #imprimir los pasos que va siguiendo
)

resultado = ejecutor_agente.invoke(
    {"entrada": "¿Cuanatas veces reinte el cliente y cuanto seria eso multiplicado por 2?"}
)

print("Respuesta final:", resultado["output"])

