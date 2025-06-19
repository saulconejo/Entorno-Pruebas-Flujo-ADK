from typing import List, Optional, Dict, Any
from google.adk.agents import SequentialAgent, LlmAgent, LoopAgent
from google.genai.types import GenerateContentConfig
from google.adk.tools import ToolContext
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH
from router_agent.agent import RouterAgent

# Configuración del modelo
MODEL_CONFIG = GenerateContentConfig(
    temperature=0.0,
    max_output_tokens=200,
    candidate_count=1
)

# --- Herramienta para salir del bucle ---
def exit_processing_loop(tool_context: ToolContext):
    """Función que se llama cuando la pregunta está validada para salir del bucle"""
    print(f"[Tool Call] exit_processing_loop llamado por {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {"status": "validated"}

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

    4. No respondes con entendido o cosas asi, solo sirves para normalizar la consulta y extraer entidades clave.
    """,
    generate_content_config=MODEL_CONFIG,
    output_key="normalized_data"
)

ValidatorAgent = LlmAgent(
    name="ValidatorAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    instruction="""  
      Validador de Consultas Financieras  
        
      IMPORTANTE: Solo llama a exit_processing_loop() cuando la consulta esté COMPLETAMENTE validada.  
        
      Criterios OBLIGATORIOS para validación:  
      1. Verbo de acción claro (pagar/consultar/anular)    
      2. Datos mínimos requeridos  
        
      FLUJO DE DECISIÓN:  
      - If la pregunta es comprensible:   
        * Llama INMEDIATAMENTE a exit_processing_loop()  
        * Devuelve: {"status": "valid", "entities": {...}}  
        
      - Else:  
        * NO llames a exit_processing_loop()  
        * Devuelve: {"status": "invalid", "error": "criterio_faltante", "suggestion": "texto_mejorado"}  
    """,
    generate_content_config=MODEL_CONFIG,
    tools=[exit_processing_loop],  # Registra la herramienta de salida
    output_key="validation_result"
)

ProcessingAgent = LoopAgent(
    name="ProcessingAgent",
    sub_agents=[NormalizerAgent, ValidatorAgent],
    description="Agente de procesamiento de consultas financieras",
    max_iterations=3,  # Límite de intentos

)

# --- Agente Principal ---
QuestionAgent = SequentialAgent(
    name="QuestionAgent",
    description="Procesamiento y validación de consultas",
    sub_agents=[ProcessingAgent, RouterAgent],
)