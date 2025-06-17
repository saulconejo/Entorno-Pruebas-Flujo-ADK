# orchestator.py
import logging
from google.adk.agents import SequentialAgent
from reserva_agent.agent import ReservaAgent
from menu_agent.agent import MenuAgent
from facturacion_agent.agent import FacturacionAgent
from cocina_agent.agent import CocinaAgent
from general_agent.agent import GeneralAgent

logger = logging.getLogger(__name__)

def create_orchestrator_agent():
    """
    Crea un orquestrador secuencial que garantice que el agente general siempre
    se ejecute primero, seguido por los agentes especializados según sea necesario.
    """
    # Crear un SubOrquestador para los agentes especializados
    SpecializedAgents = SequentialAgent(
        name="SpecializedTeam",
        description="Equipo especializado del restaurante",
        sub_agents=[
            ReservaAgent,
            MenuAgent,
            FacturacionAgent,
            CocinaAgent
        ]
    )
    
    # Orquestador principal que ejecuta primero el agente general y luego el equipo especializado
    orchestrator = SequentialAgent(
        name="RestaurantOrchestrator",
        description="Sistema completo del restaurante que coordina todos los servicios",
        sub_agents=[
            GeneralAgent,      # 1. Ejecuta primero el agente general (analiza y delega)
            SpecializedAgents  # 2. Luego los agentes especializados según corresponda
        ]
    )
    
    logger.info("Sistema de orquestación secuencial del restaurante creado con éxito")
    return orchestrator

# Exportar el agente raíz para ADK
root_agent = create_orchestrator_agent()