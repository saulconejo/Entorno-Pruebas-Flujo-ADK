# orchestrator.py
from google.adk.agents import SequentialAgent
from reserva_agent.agent import ReservaAgent
from menu_agent.agent import MenuAgent
from facturacion_agent.agent import FacturacionAgent
from cocina_agent.agent import CocinaAgent

coordinator = SequentialAgent(
    name="RestauranteCoordinator",
    description="Coordina reserva, menú, facturación y cocina",
    sub_agents=[
        ReservaAgent(name="ReservaAgent"),
        MenuAgent(name="MenuAgent"),
        FacturacionAgent(name="FacturacionAgent"),
        CocinaAgent(name="CocinaAgent")
    ]
)
