import logging
from typing import Dict, List, Union, Any
from datetime import datetime, timedelta
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH, FACTURAS, PAGOS, CLIENTES
from descuento_agent.prompts import DISCOUNT_AGENT_INSTRUCTION
from descuento_agent.tools import (
    recomendar_descuento_personalizado,
    explicar_calculo_descuento_tool,
    simular_impacto_descuento_tool
)




# Definición del Discount Agent
DiscountAgent = LlmAgent(
    name="DiscountAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en cálculo y recomendación de descuentos personalizados, devuelve un json con el descuento recomendado, su cálculo y simulación de impacto en las finanzas",
    instruction=DISCOUNT_AGENT_INSTRUCTION,
    tools=[
        recomendar_descuento_personalizado,
        explicar_calculo_descuento_tool,
        simular_impacto_descuento_tool
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=2000
    )
)

# Exportar el agente
discount_agent = DiscountAgent