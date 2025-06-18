from typing import List, Optional
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data.restaurant_data import MODEL_GEMINI_2_0_FLASH
from cocina_agent.prompts import GLOBAL_INSTRUCTION_COCINA, INSTRUCTION_COCINA
from data.restaurant_data import (
    estimate_preparation_time_tool,
    filter_menu_by_dietary_tool,
    find_dishes_by_ingredient_tool
)


# Instancia del agente de cocina usando LlmAgent
CocinaAgent = LlmAgent(
    name="CocinaAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Especialista en lógica de cocina: estima tiempos, sugiere platos por ingredientes, filtra por restricciones dietéticas.",
    tools=[
        estimate_preparation_time_tool,
        filter_menu_by_dietary_tool,
        find_dishes_by_ingredient_tool
    ],
    global_instruction=GLOBAL_INSTRUCTION_COCINA,
    instruction=INSTRUCTION_COCINA,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=200,
        candidate_count=1,
        stop_sequences=["\n\nUser:", "\n\nHuman:"]
    )
)