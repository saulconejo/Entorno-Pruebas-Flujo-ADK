import logging
from google.adk.agents import LlmAgent, SequentialAgent
from initial_agent.agent import InitialAgent
from question_agent.agent import QuestionAgent
from factura_data.factura_data import MODEL_GEMINI_2_0_FLASH
from orchestator_agent.prompts import GENERAL_AGENT_PROMPT
from general_agent.agent import GeneralAgent
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def create_orchestrator_agent():
    """
    Orquestador mejorado para gestión de flujo conversacional
    """
    orchestrator = SequentialAgent(
        name="FacturacionOrchestrator",
        sub_agents=[
            InitialAgent,   # Agente de primer contacto
            QuestionAgent,  # Refinamiento de consultas
            GeneralAgent    # Procesamiento final
        ]
    )
    return orchestrator

# Exportar el agente raíz
root_agent = create_orchestrator_agent()