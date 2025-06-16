# menu_agent.py
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from data.restaurant_data import RestaurantTools

class MenuAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext):
        restrictions = ctx.session.state["dietary_restrictions"]
        result = RestaurantTools.filter_menu_by_dietary(restrictions)
        ctx.session.state["filtered_menu"] = result
        yield Event(author=self.name, message="Menú filtrado", final=True)
