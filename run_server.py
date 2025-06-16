# run_server.py
from google.adk import start_adk_web
from main_orchestator import restaurant_orchestrator  # Tu agente secuencial

if __name__ == "__main__":
    start_adk_web(restaurant_orchestrator)
