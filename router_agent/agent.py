from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH
from descuento_agent.agent import DiscountAgent
from alerta_agent.agent import CreditAgent
from impago_agent.agent import RiskAgent
from reabastecimiento_agent.agent import InventoryAgent
from resumen_agent.agent import CustomerAgent
from router_agent.prompts import INTENT_CLASSIFIER_PROMPT

RouterAgent = LlmAgent(
    name="RouterAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Redirige al agente adecuado según la intención del usuario",
    instruction=INTENT_CLASSIFIER_PROMPT,
    sub_agents=[
        DiscountAgent,  
        CreditAgent,     
        RiskAgent,      
        InventoryAgent, 
        CustomerAgent
    ],

    output_key="processing_route",  # Almacena resultado sin mostrarlo 
    
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=300
    )
)
