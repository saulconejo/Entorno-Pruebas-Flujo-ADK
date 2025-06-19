from factura_data.factura_data import FACTURAS, CLIENTES
import logging
from datetime import datetime
from typing import Dict, List

# Configurar el logger
logger = logging.getLogger(__name__)

# Herramienta para detectar facturas con riesgo de impago
def detectar_facturas_riesgo_impago() -> List[Dict]:
    """
    Identifica facturas pendientes de clientes con alto riesgo de impago.
    
    Returns:
        List[Dict]: Lista de facturas con alto riesgo de impago
    """
    try:
        # Filtrar facturas pendientes
        facturas_pendientes = [f for f in FACTURAS if f.get("estado") == "pendiente"]
        
        # Crear un diccionario para acceso rápido a los clientes por ID
        clientes_por_id = {cliente["id"]: cliente for cliente in CLIENTES}
        
        # Filtrar facturas de clientes con alto riesgo de impago (>0.7)
        facturas_riesgosas = [
            factura for factura in facturas_pendientes
            if factura.get("cliente_id") in clientes_por_id and 
            clientes_por_id[factura.get("cliente_id")].get("riesgo_impago", 0) > 0.7
        ]
        
        # Ordenar por fecha de vencimiento (más próximas primero)
        facturas_riesgosas.sort(
            key=lambda f: datetime.fromisoformat(f.get("fecha_vencimiento", "9999-12-31T23:59:59Z").replace("Z", "+00:00")),
            reverse=False
        )
        
        return facturas_riesgosas
        
    except Exception as e:
        logger.error(f"Error al detectar facturas con riesgo de impago: {e}")
        return []

def generar_informe_riesgo_impago_tool():
    """
    Genera un informe detallado de las facturas con alto riesgo de impago.
    
    Returns:
        str: Informe formateado con las facturas de riesgo
    """
    facturas_riesgosas = detectar_facturas_riesgo_impago()
    
    if not facturas_riesgosas:
        return "No se han detectado facturas con alto riesgo de impago en este momento."
    
    # Crear un diccionario para acceso rápido a los clientes por ID
    clientes_por_id = {cliente["id"]: cliente for cliente in CLIENTES}
    
    # Construir el informe
    informe = "INFORME DE FACTURAS CON ALTO RIESGO DE IMPAGO\n"
    informe += "===========================================\n\n"
    informe += f"Total de facturas identificadas: {len(facturas_riesgosas)}\n\n"
    
    for i, factura in enumerate(facturas_riesgosas, 1):
        cliente = clientes_por_id.get(factura.get("cliente_id", ""), {})
        
        informe += f"FACTURA {i}: {factura.get('numero', 'N/A')}\n"
        informe += f"  - ID: {factura.get('id', 'N/A')}\n"
        informe += f"  - Cliente: {cliente.get('nombre', 'N/A')} (ID: {cliente.get('id', 'N/A')})\n"
        informe += f"  - Riesgo de impago: {cliente.get('riesgo_impago', 0) * 100:.1f}%\n"
        informe += f"  - Fecha vencimiento: {factura.get('fecha_vencimiento', 'N/A')}\n"
        informe += f"  - Monto total: {factura.get('total', 0):.2f} EUR\n"
        informe += f"  - Días de retraso: {(datetime.now() - datetime.fromisoformat(factura.get('fecha_vencimiento', '').replace('Z', '+00:00'))).days if 'fecha_vencimiento' in factura and factura['fecha_vencimiento'] else 'N/A'}\n\n"
    
    informe += "ACCIONES RECOMENDADAS:\n"
    informe += "- Contactar a los clientes con facturas próximas a vencer\n"
    informe += "- Considerar restricciones de crédito para clientes con alto riesgo\n"
    informe += "- Programar seguimiento para facturas vencidas\n"
    
    return informe


