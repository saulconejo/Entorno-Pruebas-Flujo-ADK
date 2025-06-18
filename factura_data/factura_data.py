import os
import json
from google.genai.types import GenerationConfig

# Definir la ruta al archivo JSON
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "factura_data.json")

# Cargar los datos del archivo JSON
try:
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    # Extraer las secciones del JSON
    DEVOLUCIONES = data.get("DEVOLUCIONES", [])
    PAGOS = data.get("PAGOS", [])
    CLIENTES = data.get("CLIENTES", [])
    PRODUCTOS = data.get("PRODUCTOS", [])  # Usamos .get() para evitar KeyError
    FACTURAS = data.get("FACTURAS", [])
    
except Exception as e:
    print(f"Error al cargar el archivo JSON: {e}")
    # Proporcionar datos vacíos como fallback
    DEVOLUCIONES = []
    PAGOS = []
    CLIENTES = []
    PRODUCTOS = []
    FACTURAS = []

# Definir el modelo a utilizar
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

# Configuración estándar para generación de contenido
DEFAULT_GENERATION_CONFIG = GenerationConfig(
    temperature=0.2,
    top_p=0.8,
    top_k=40,
    max_output_tokens=1024,
)

# Exportar variables para uso en otros módulos
__all__ = [
    "DEVOLUCIONES", 
    "PAGOS", 
    "CLIENTES", 
    "PRODUCTOS", 
    "FACTURAS", 
    "MODEL_GEMINI_2_0_FLASH",
    "DEFAULT_GENERATION_CONFIG"
]