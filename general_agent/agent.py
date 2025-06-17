import logging
from google.adk.agents import LlmAgent, ParallelAgent
from google.genai.types import GenerateContentConfig
from data.restaurant_data import MODEL_GEMINI_2_0_FLASH
from general_agent.prompts import GENERAL_INSTRUCTION

GeneralAgent = LlmAgent(
    name="GeneralAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente principal que analiza solicitudes y las dirige al equipo especializado adecuado",
    instruction=GENERAL_INSTRUCTION,
    generate_content_config=GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=300,
        candidate_count=1
    )
)