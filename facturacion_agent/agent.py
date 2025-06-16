# facturacion_agent.py
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from data.restaurant_data import RestaurantTools

class FacturacionAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext):
        state = ctx.session.state
        result = RestaurantTools.calculate_order_price(
            items=state["menu_items"],
            party_size=state["party_size"],
            time=state["time"],
            date=state["date"]
        )
        state["order_price"] = result
        yield Event(author=self.name, message="Precio calculado", final=True)
