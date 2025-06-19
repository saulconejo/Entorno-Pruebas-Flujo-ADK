import logging
from datetime import datetime
from typing import List, Dict
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH, PRODUCTOS
from reabastecimiento_agent.prompts import INVENTORY_AGENT_INSTRUCTION
from reabastecimiento_agent.tools import (
    recomendar_reabastecimiento_productos,
    generar_informe_reabastecimiento_tool,
    simular_orden_reabastecimiento_tool
)

logger = logging.getLogger(__name__)

# Definición del Inventory Agent
InventoryAgent = LlmAgent(
    name="InventoryAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en gestión de inventario y recomendaciones de reabastecimiento, devuelve un json con las recomendaciones de reabastecimiento, un informe detallado y simulación de órdenes de reabastecimiento",
    instruction=INVENTORY_AGENT_INSTRUCTION,
    tools=[
        recomendar_reabastecimiento_productos,
        generar_informe_reabastecimiento_tool,
        simular_orden_reabastecimiento_tool
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=2000
    )
)

# Exportar el agente
inventory_agent = InventoryAgent