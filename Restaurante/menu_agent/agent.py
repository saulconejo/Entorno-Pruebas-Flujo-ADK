from typing import Optional
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from data.restaurant_data import MODEL_GEMINI_2_0_FLASH
from menu_agent.prompts import GLOBAL_INSTRUCTION_MENU, INSTRUCTION_MENU
from data.restaurant_data import (
    list_menu_categories_tool,
    get_dishes_by_category_tool,
    get_dish_details_tool,
    filter_menu_by_dietary_tool,
    find_dishes_by_ingredient_tool
)


# Instancia del agente de menú usando LlmAgent
MenuAgent = LlmAgent(
    name="MenuAgent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Agente que gestiona consultas y navegación del menú del restaurante.",
    tools=[
        list_menu_categories_tool,
        get_dishes_by_category_tool,
        get_dish_details_tool,
        filter_menu_by_dietary_tool,
        find_dishes_by_ingredient_tool
    ],
    global_instruction=GLOBAL_INSTRUCTION_MENU,
    instruction=INSTRUCTION_MENU,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=200,
        candidate_count=1,
        stop_sequences=["\n\nUser:", "\n\nHuman:"]
    )
)