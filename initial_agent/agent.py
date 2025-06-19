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

def handle_general_query_tool(user_input: str) -> str:
    """Clasifica el intento del usuario: saludo, pregunta, acción o desconocido."""
    input_lower = user_input.strip().lower()

    # Reglas básicas
    greetings = ["hola", "buenos días", "buenas tardes", "saludos"]
    actions = ["quiero", "necesito", "me gustaría", "hazme", "realizar", "crear", "hacer"]
    question_starts = ["¿", "que", "qué", "cómo", "dónde", "cuándo", "por qué", "cuál"]

    if any(word in input_lower for word in greetings):
        return "saludo"
    
    if any(word in input_lower for word in actions):
        return "acción"
    
    if "?" in input_lower or any(input_lower.startswith(q) for q in question_starts):
        return "pregunta"

    return "desconocido"


# --- Agentes Especializados ---
GreetingAgent = LlmAgent(
    name="GreetingAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Maneja saludos, si no es un saludo no intervienes, siempre pregunta qué necesita el usuario.",
    global_instruction=GLOBAL_INSTRUCTION,
    instruction="""Vas a saludar cordialmente y a solicitar al usuario que realice una solicitud sobre temas de facturación, solicita los datos pertinentes y pasa a ValidatorAgent.
    """,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=150,
        stop_sequences=["\n\nUser:"]
    ),

    output_key="response"
)

ValidationAgent = LlmAgent(
    name="ValidationAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Valida preguntas antes de salir del bucle",
    global_instruction=GLOBAL_INSTRUCTION,
    instruction="""
        Eres un agente de validación de consultas.
        Tu tarea es:
        1. Validar si la consulta es una pregunta o solicitud de acción.
        2. Si es válida, redirigir al agente correspondiente.
        3. Si no es válida, devolver un mensaje de error y sugerencia.
        
        Ejemplos:
        - "¿Cómo puedo pagar mi factura?" -> Redirigir a QuestionAgent
        - "Quiero saber mi saldo" -> Redirigir a QuestionAgent
        - "No entiendo nada" -> Devolver error y sugerencia
    """,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=100
    ),
    output_key="validation_result"
)

# --- Loop Principal Corregido ---
InitialAgent = LlmAgent(
    name="InitialAgent",
    description="Bucle de atención inicial, solo si se saluda usa GreetingAgent o si se solicita o pregunta ValidationAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    sub_agents=[GreetingAgent, ValidationAgent],
    tools=[handle_general_query_tool],
    global_instruction=GLOBAL_INSTRUCTION,
    instruction="""    
        Eres un agente de atención al cliente que maneja saludos y cuestiones iniciales.
        Tu tarea es:
        1. Si el mensaje es un saludo (ej. 'hola', 'buenos días'), pasa a GreetingAgent.
        2. Si el mensaje es una solicitud de acción o contiene verbos como 'quiero', 'necesito', 'me gustaría', etc., pasa a ValidationAgent.
        3. Si es una pregunta, también pasa a ValidationAgent.
        """,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=100
    ),
)