from typing import List, Optional
from google.adk.agents import LlmAgent, BaseAgent
from google.genai.types import GenerateContentConfig
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH
from google.adk.tools.tool_context import ToolContext

# --- Configuración Global ---
GLOBAL_INSTRUCTION = """
Eres parte de un sistema de atención al cliente de una empresa de servicios.
Sigue estrictamente el protocolo definido para cada agente.
"""

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


# --- Agentes Especializados ---
GreetingAgent = LlmAgent(
    name="GreetingAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Maneja saludos y conversación trivial",
    global_instruction=GLOBAL_INSTRUCTION,
    instruction="""
    [Mantener el mismo contenido del prompt anterior]
    """,
    tools=[handle_general_query_tool],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=150,
        stop_sequences=["\n\nUser:"]
    )
)

ValidationAgent = LlmAgent(
    name="ValidationAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Valida preguntas antes de salir del bucle",
    global_instruction=GLOBAL_INSTRUCTION,
    instruction="""
    [Mantener el mismo contenido del prompt anterior]
    """,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=100
    )
)

# --- Loop Principal Corregido ---
InitialAgent = LlmAgent(
    name="InitialAgent",
    description="Bucle de atención inicial",
    model=MODEL_GEMINI_2_0_FLASH,
    sub_agents=[GreetingAgent, ValidationAgent],
    global_instruction=GLOBAL_INSTRUCTION,
    instruction="""    
    Eres un agente de atención al cliente que maneja saludos y validaciones iniciales.
    Tu tarea es:
    1. Si es un saludo pasa a GreetingAgent y solicitas una que pida algo.
    2. Si y solo si es una pregunta pasa a ValidationAgent y sales de InitialAgent.
    3. Si no ocurre nada de eso, pide una solicitud válida al usuario.
    """,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=100
    ),
)