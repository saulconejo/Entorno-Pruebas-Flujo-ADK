import logging
from datetime import datetime
from typing import List, Dict
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH, FACTURAS, CLIENTES
from impago_agent.prompts import RISK_AGENT_INSTRUCTION
from impago_agent.tools import (
    detectar_facturas_riesgo_impago,
    generar_informe_riesgo_impago_tool
)

logger = logging.getLogger(__name__)

# Definición del Risk Agent
RiskAgent = LlmAgent(
    name="RiskAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en detectar y gestionar facturas con riesgo de impago, devuelve un json con las facturas identificadas y un informe detallado de riesgo de impago",
    instruction=RISK_AGENT_INSTRUCTION,
    tools=[
        detectar_facturas_riesgo_impago,
        generar_informe_riesgo_impago_tool,
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=2000
    )
)