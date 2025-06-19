import logging
from google.adk.agents import LlmAgent, LlmAgent, Agent
from initial_agent.agent import InitialAgent
from question_agent.agent import QuestionAgent
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH
from orchestator_agent.prompts import GENERAL_AGENT_PROMPT

logger = logging.getLogger(__name__)


def create_orchestrator_agent():
    """
    Orquestador mejorado para gestión de flujo conversacional
    """
    orchestrator = LlmAgent(
        name="FacturacionOrchestrator",
        model=MODEL_GEMINI_2_0_FLASH,
        description="Agente orquestador para gestionar el flujo de conversación en el sistema de atención al cliente.",
        global_instruction=GENERAL_AGENT_PROMPT,
        sub_agents=[
            InitialAgent,   # Agente de primer contacto
            QuestionAgent,  # Refinamiento de consultas
        ],

        output_key="validacion_mensaje_recibido"  # Almacena resultado sin mostrarlo 
    )
    return orchestrator

# Exportar el agente raíz
root_agent = create_orchestrator_agent()