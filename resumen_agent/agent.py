import logging
from typing import Dict, List, Any
from datetime import datetime
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH, FACTURAS, PAGOS, DEVOLUCIONES, CLIENTES
from resumen_agent.prompts import CUSTOMER_AGENT_INSTRUCTION
from resumen_agent.tools import (
    resumen_cliente,
    generar_informe_cliente_tool,
    comparar_comportamiento_pago_tool
)   

logger = logging.getLogger(__name__)



# Definición del Customer Agent
CustomerAgent = LlmAgent(
    name="CustomerAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente especializado en análisis financiero y comportamiento de clientes, devuelve un json con el resumen del cliente, un informe detallado de su situación financiera y comparación de su comportamiento de pago con otros clientes similares",
    instruction=CUSTOMER_AGENT_INSTRUCTION,
    tools=[
        resumen_cliente,
        generar_informe_cliente_tool,
        comparar_comportamiento_pago_tool
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=2000
    )
)

# Exportar el agente
customer_agent = CustomerAgent