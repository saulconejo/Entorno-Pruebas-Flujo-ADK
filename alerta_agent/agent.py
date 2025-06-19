import logging
from typing import Dict, List, Any
from datetime import datetime
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH, FACTURAS, CLIENTES
from alerta_agent.prompts import CREDIT_AGENT_INSTRUCTION
from alerta_agent.tools import (
    generar_alertas_credito,
    formatear_alertas_credito_tool,
    recomendar_acciones_cliente_tool
)   

logger = logging.getLogger(__name__)



# Definición del Credit Agent
CreditAgent = LlmAgent(
    name="CreditAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en control de crédito y gestión de alertas por exceso de límite, devuelve un json con las alertas generadas y recomendaciones de acciones para el cliente",
    instruction=CREDIT_AGENT_INSTRUCTION,
    tools=[
        generar_alertas_credito,
        formatear_alertas_credito_tool,
        recomendar_acciones_cliente_tool
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=2000
    )
)

# Exportar el agente
credit_agent = CreditAgent