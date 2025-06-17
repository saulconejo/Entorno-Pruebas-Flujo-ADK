from typing import Optional, List
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data.restaurant_data import MODEL_GEMINI_2_0_FLASH
from facturacion_agent.prompts import GLOBAL_INSTRUCTION_FACTURACION, INSTRUCTION_FACTURACION
from data.restaurant_data import (
    calculate_order_price_tool,
    generate_order_summary_tool,
    apply_specific_discount_tool
)

# Instancia del agente de facturación usando LlmAgent
FacturacionAgent = LlmAgent(
    name="FacturacionAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente que gestiona la facturación, precios y descuentos del restaurante.",
    tools=[
        calculate_order_price_tool,
        generate_order_summary_tool,
        apply_specific_discount_tool
    ],
    global_instruction=GLOBAL_INSTRUCTION_FACTURACION,
    instruction=INSTRUCTION_FACTURACION,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=200,
        candidate_count=1,
        stop_sequences=["\n\nUser:", "\n\nHuman:"]
    )
)
