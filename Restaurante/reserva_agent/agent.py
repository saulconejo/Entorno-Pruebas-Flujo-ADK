from typing import Optional  # Añade esta importación al principio del archivo
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data.restaurant_data import MODEL_GEMINI_2_0_FLASH
from reserva_agent.prompts import GLOBAL_INSTRUCTION_RESERVA, INSTRUCTION_RESERVA
from data.restaurant_data import (
    check_table_availability_tool,
    create_reservation_tool,
    update_reservation_tool,
    cancel_reservation_tool,
    find_reservation_by_name_tool
)

# Instancia del agente de reservas usando LlmAgent
ReservaAgent = LlmAgent(
    name="ReservaAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente que gestiona el sistema de reservas del restaurante.",
    tools=[
        check_table_availability_tool,
        create_reservation_tool,
        update_reservation_tool,
        cancel_reservation_tool,
        find_reservation_by_name_tool
    ],
    global_instruction=GLOBAL_INSTRUCTION_RESERVA,
    instruction=INSTRUCTION_RESERVA,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=200,
        candidate_count=1,
        stop_sequences=["\n\nUser:", "\n\nHuman:"]
    )
)