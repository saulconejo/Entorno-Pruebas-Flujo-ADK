import asyncio
import json
import logging
import os

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Importar agente coordinador principal (tu orquestador)
from main_orchestator.agent import coordinator as agent

# Configuración básica de logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

APP_NAME = "restaurant_flow_app"
USER_ID = "user_123"

# Usaremos una sola sesión para el demo
SESSION_ID = "session_restaurant_flow"

# Crear servicio de sesiones en memoria
session_service = InMemorySessionService()

# Crear Runner con el agente coordinador
runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service
)

# Función para llamar al agente coordinador y mostrar respuesta
async def send_message_and_print(message: str):
    logger.info(f"Enviando mensaje al agente coordinador: {message}")

    user_content = types.Content(role="user", parts=[types.Part(text=message)])

    final_response = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    if final_response:
        logger.info(f"Respuesta del agente coordinador:\n{final_response}")
    else:
        logger.warning("No se recibió respuesta final del agente.")

# Función main async para pruebas
async def main():

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    if not session:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        print(f"Sesión creada: {SESSION_ID}")
    else:
        print(f"Sesión existente recuperada: {SESSION_ID}")
        
    # Mensajes de prueba - simular flujo de conversación con agentes
    mensajes_prueba = [
        "Quiero reservar una mesa para 4 personas mañana a las 8pm.",
        "¿Qué platos tienen disponibles hoy?",
        "Quiero pedir una pizza margarita y una ensalada César.",
        "¿Cuánto tiempo tardará la preparación?",
        "Por favor, genera la factura con un descuento del 10%.",
    ]

    for msg in mensajes_prueba:
        await send_message_and_print(msg)
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(main())
