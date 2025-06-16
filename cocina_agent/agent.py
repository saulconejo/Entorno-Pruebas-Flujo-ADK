# cocina_agent.py
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from data.restaurant_data import RestaurantTools

class CocinaAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext):
        menu_items = ctx.session.state.get("menu_items")
        if not menu_items:
            yield Event(
                author=self.name,
                message="No se han especificado los platos para estimar el tiempo de cocina.",
                final=True
            )
            return

        result = RestaurantTools.estimate_preparation_time(menu_items)
        ctx.session.state["prep_time"] = result
        yield Event(
            author=self.name,
            message=f"Tiempo de cocina estimado: {result} minutos.",
            final=True
        )