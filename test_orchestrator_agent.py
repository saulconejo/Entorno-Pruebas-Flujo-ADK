import asyncio  
from google.adk.runners import InMemoryRunner  
from google.genai.types import Part, UserContent  
from orchestator_agent.agent import root_agent  
  
test_inputs = [  
    "Necesito un resumen del cliente CLT-004",  
    "Qué descuentos tengo disponibles como CLT-003",   
    "Tengo impagos en mi cuenta CLT-001?",  
    "Hay alertas o bloqueos para el cliente CLT-002",  
    "Recomienden reabastecimiento para CLT-005",  
]  
  
async def run_orchestrator_tests():  
    runner = InMemoryRunner(agent=root_agent)  
      
    # Await the session creation  
    session = await runner.session_service.create_session(  
        app_name=runner.app_name,   
        user_id="test_user"  
    )  
      
    for i, input_text in enumerate(test_inputs, 1):  
        print(f"\n--- Test #{i}: \"{input_text}\" ---")  
        try:  
            content = UserContent(parts=[Part(text=input_text)])  
            events = list(runner.run(  
                user_id=session.user_id,   
                session_id=session.id,   
                new_message=content  
            ))  
              
            if events:  
                response = events[-1].content.parts[0].text  
                print("🔹 Resultado:", response)  
                  
        except Exception as e:  
            print(f"❌ Error en test #{i}:", e)  
  
if __name__ == "__main__":  
    asyncio.run(run_orchestrator_tests())