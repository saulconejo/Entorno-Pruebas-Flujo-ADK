from typing import List, Optional
from google.adk.agents import SequentialAgent, LlmAgent
from google.genai.types import GenerateContentConfig
from google.adk.tools import ToolContext
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH

# Configuración del modelo
MODEL_CONFIG = GenerateContentConfig(
    temperature=0.0,
    max_output_tokens=200,
    candidate_count=1
)

# --- Agentes de Procesamiento ---
NormalizerAgent = LlmAgent(
    name="NormalizerAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction="""
    Sistema de Normalización Automática de Consultas Financieras

    Proceso:
    1. Recibe consulta cruda
    2. Aplica transformaciones:
       - Estandariza formatos (IDs, referencias)
       - Corrige errores tipográficos
       - Extrae entidades clave
    3. Devuelve JSON con:
       {
         "normalized": "texto_estandarizado",
         "entities": {"tipo": "pago/factura", "id": "FAC-123"}
       }
    """,
    generate_content_config=MODEL_CONFIG
)

ValidatorAgent = LlmAgent(
    name="ValidatorAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction="""
    Validador de Consultas Financieras

    Criterios de Validación:
    1. Verbo de acción claro (pagar/consultar/anular)
    2. Identificador válido (formato estandarizado)
    3. Datos mínimos requeridos

    Acciones:
    - Si es válida: call transfer_to_general_agent()
    - Si no: Devuelve JSON con:
      {
        "error": "tipo_error",
        "suggestion": "texto_mejorado"
      }
    """,
    generate_content_config=MODEL_CONFIG,
)

# --- Question Agent (Secuencial) ---
QuestionAgent = SequentialAgent(
    name="QuestionAgent",
    description="Procesamiento y validación de consultas",
    sub_agents=[NormalizerAgent, ValidatorAgent]
)