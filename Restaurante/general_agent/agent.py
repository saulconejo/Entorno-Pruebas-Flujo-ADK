from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool, BaseTool
from google.genai.types import GenerateContentConfig
from data.restaurant_data import MODEL_GEMINI_2_0_FLASH
from general_agent.prompts import GENERAL_INSTRUCTION

# Importar subagentes especializados
from menu_agent.agent import MenuAgent
from reserva_agent.agent import ReservaAgent
from facturacion_agent.agent import FacturacionAgent
from cocina_agent.agent import CocinaAgent

def handle_general_query_tool(query: str):
    """Maneja consultas generales directamente."""
    query_lower = query.lower()
    
    # Saludos
    if any(greeting in query_lower for greeting in ["hola", "buenos días", "buenas tardes", "saludos"]):
        return "¡Hola! Bienvenido a nuestro restaurante. ¿En qué puedo ayudarte hoy?"
    
    # Despedidas
    if any(farewell in query_lower for farewell in ["adiós", "gracias", "hasta luego"]):
        return "¡Gracias por visitarnos! Esperamos verte pronto de nuevo."
    
    # Información general
    if "ubicación" in query_lower or "dirección" in query_lower or "donde" in query_lower:
        return "Estamos ubicados en Calle Principal 123, en el centro de la ciudad."
    
    if "horario" in query_lower or "cuando" in query_lower:
        return "Nuestro horario es de 12:00 a 23:00, todos los días de la semana."
    
    # Consulta ambigua
    return "Para poder ayudarte mejor, ¿podrías proporcionar más detalles sobre tu consulta?"


# Ahora el agente general con todas las herramientas, incluidas las agent_tools
GeneralAgent = LlmAgent(
    name="GeneralAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente general del restaurante: responde preguntas básicas o delega a agentes especializados.",
    instruction=GENERAL_INSTRUCTION,
    sub_agents=[
        MenuAgent,
        ReservaAgent,
        FacturacionAgent,
        CocinaAgent
    ],

    tools=[
        handle_general_query_tool
    ],

    generate_content_config=GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=500
    )
)
