# Herramientas personzalizadas
# Intro a memoria

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from pydantic import BaseModel, Field, ValidationError

#configuraciones e inicializaciones

load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

class ArgumentosConsultaEnvio(BaseModel): #class clasehija(clasepadre)
    """
    Esquema para documentar y validar argumentos campo por campo ante el LLM.
    """
    numero_seguimiento: str =Field(
        description="numero de seguimiento del envio, por ejemplo "AR12983"
    )
    incluir_historial: bool = Field(
        default=False,
        description="Si es True, incluye en historial completo de los estados, no solo el actual"
    )
    
ESTADOS = {
    "AR12345":{
        "actual": "en transito, entrega estimada en 2 dias"
        "historial": [
            "Recibido en deposito",
            "En transito"
        ]
    }
}    

#Herramientas
#@tool("nuevo nombre")
@tool(args_schema=ArgumentosConsultaEnvio)# LangChain transforma esta clase en un esquema JSON que se envia al LLM. El modelo lo lee textualmente.
def consultar_estado_envio_detallado(numero_seguimiento:str, incluir_historial: bool=False):
    """
    Consulta el estado de un envio, con la opcion de incluir el historial completo
    """
    envio = ESTADOS.get(numero_seguimiento)
    if envio is None: 
        return f"No se encontro un envio con el numero {numero_seguimiento}."
    
    if not incluir_historial:
        return envio["actual"]
        
    historial = ",".join(envio["historial"])





