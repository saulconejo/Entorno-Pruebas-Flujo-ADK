# reserva_agent.py
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from data.restaurant_data import RestaurantTools

class ReservaAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext):
        data = ctx.session.state
        result = RestaurantTools.get_available_tables(
            date=data["date"],
            time=data["time"],
            party_size=data["party_size"]
        )
        ctx.session.state["available_tables"] = result
        yield Event(author=self.name, message="Mesas consultadas", final=True)
