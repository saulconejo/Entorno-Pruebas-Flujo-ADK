from datetime import datetime
from typing import List, Dict
import logging
from factura_data.factura_data import PRODUCTOS

# Configurar el logger
logger = logging.getLogger(__name__)

# Función principal para recomendar reabastecimiento de productos
def recomendar_reabastecimiento_productos() -> List[Dict]:
    """
    Identifica productos que necesitan reabastecimiento basado en stock mínimo y actual.
    Ordena por prioridad calculada con factores estacionales.
    
    Returns:
        List[Dict]: Lista de productos que requieren reabastecimiento, ordenados por prioridad
    """
    try:
        # Obtener el mes actual (en minúsculas)
        mes_actual = datetime.now().strftime("%B").lower()
        
        # Traducir el nombre del mes al español si necesario
        meses_traduccion = {
            "january": "enero", "february": "febrero", "march": "marzo", 
            "april": "abril", "may": "mayo", "june": "junio",
            "july": "julio", "august": "agosto", "september": "septiembre", 
            "october": "octubre", "november": "noviembre", "december": "diciembre"
        }
        mes_actual_es = meses_traduccion.get(mes_actual, "enero")  # Default a enero si hay error
        
        # Filtrar productos activos con stock por debajo del mínimo
        productos_bajo_minimo = [
            producto for producto in PRODUCTOS
            if producto.get("activo", False) and 
               producto.get("stock_actual", 0) < producto.get("stock_minimo", 0)
        ]
        
        # Calcular prioridad con factor estacional y ordenar
        for producto in productos_bajo_minimo:
            factor_estacional = producto.get("datos_estacionales", {}).get(mes_actual_es, 1.0)
            diferencia_stock = producto.get("stock_minimo", 0) - producto.get("stock_actual", 0)
            producto["prioridad_reabastecimiento"] = diferencia_stock * factor_estacional
        
        # Ordenar de mayor a menor prioridad
        productos_bajo_minimo.sort(key=lambda p: p.get("prioridad_reabastecimiento", 0), reverse=True)
        
        return productos_bajo_minimo
        
    except Exception as e:
        logger.error(f"Error al recomendar reabastecimiento de productos: {e}")
        return []

def generar_informe_reabastecimiento_tool():
    """
    Genera un informe detallado de los productos que necesitan reabastecimiento.
    
    Returns:
        str: Informe formateado con las recomendaciones de reabastecimiento
    """
    productos_reabastecimiento = recomendar_reabastecimiento_productos()
    
    if not productos_reabastecimiento:
        return "No se han detectado productos que requieran reabastecimiento en este momento."
    
    # Calcular la cantidad total estimada para reabastecimiento
    total_cantidad = sum(p.get("stock_minimo", 0) - p.get("stock_actual", 0) for p in productos_reabastecimiento)
    total_costo_estimado = sum((p.get("stock_minimo", 0) - p.get("stock_actual", 0)) * p.get("costo", 0) for p in productos_reabastecimiento)
    
    # Construir el informe
    informe = "INFORME DE RECOMENDACIÓN DE REABASTECIMIENTO\n"
    informe += "============================================\n\n"
    informe += f"Total de productos identificados: {len(productos_reabastecimiento)}\n"
    informe += f"Total de unidades a reabastecer: {total_cantidad}\n"
    informe += f"Costo estimado total: {total_costo_estimado:.2f} EUR\n\n"
    
    informe += "PRODUCTOS PRIORITARIOS PARA REABASTECIMIENTO:\n"
    informe += "--------------------------------------------\n\n"
    
    for i, producto in enumerate(productos_reabastecimiento, 1):
        diferencia = producto.get("stock_minimo", 0) - producto.get("stock_actual", 0)
        costo_reabastecimiento = diferencia * producto.get("costo", 0)
        
        informe += f"{i}. {producto.get('nombre', 'N/A')} (ID: {producto.get('id', 'N/A')})\n"
        informe += f"   - Categoría: {producto.get('categoria', 'N/A')}\n"
        informe += f"   - Stock actual: {producto.get('stock_actual', 0)} {producto.get('unidad_medida', 'unidades')}\n"
        informe += f"   - Stock mínimo: {producto.get('stock_minimo', 0)} {producto.get('unidad_medida', 'unidades')}\n"
        informe += f"   - Unidades a reabastecer: {diferencia} {producto.get('unidad_medida', 'unidades')}\n"
        informe += f"   - Costo estimado: {costo_reabastecimiento:.2f} EUR\n"
        informe += f"   - Prioridad: {producto.get('prioridad_reabastecimiento', 0):.2f}\n\n"
    
    informe += "NOTAS:\n"
    informe += "- La prioridad se calcula considerando la diferencia de stock y factores estacionales\n"
    informe += "- Se recomienda revisar productos de alta prioridad a la brevedad\n"
    
    return informe

def simular_orden_reabastecimiento_tool(producto_id: str, cantidad: int = None):
    """
    Simula la creación de una orden de reabastecimiento para un producto específico.
    
    Args:
        producto_id (str): ID del producto a reabastecer
        cantidad (int, opcional): Cantidad a ordenar. Si es None, se calcula automáticamente
                                 como (stock_minimo - stock_actual)
                                 
    Returns:
        str: Confirmación de la orden simulada
    """
    try:
        # Buscar el producto por ID
        producto = next((p for p in PRODUCTOS if p.get("id") == producto_id), None)
        
        if not producto:
            return f"Error: No se encontró el producto con ID {producto_id}"
        
        if producto.get("activo") is False:
            return f"Advertencia: El producto {producto.get('nombre', 'N/A')} está marcado como inactivo"
            
        # Calcular cantidad a ordenar si no se especificó
        if cantidad is None:
            cantidad = producto.get("stock_minimo", 0) - producto.get("stock_actual", 0)
            if cantidad <= 0:
                return f"El producto {producto.get('nombre', 'N/A')} no requiere reabastecimiento en este momento"
        
        # Calcular costo estimado
        costo_estimado = cantidad * producto.get("costo", 0)
        
        # Simular creación de orden
        fecha_estimada_entrega = (datetime.now().replace(microsecond=0) + datetime.timedelta(days=5)).isoformat()
        
        return (
            f"Orden de reabastecimiento simulada:\n"
            f"- Producto: {producto.get('nombre', 'N/A')} (ID: {producto.get('id', 'N/A')})\n"
            f"- Cantidad: {cantidad} {producto.get('unidad_medida', 'unidades')}\n"
            f"- Costo estimado: {costo_estimado:.2f} EUR\n"
            f"- Fecha estimada de entrega: {fecha_estimada_entrega}\n"
            f"- Orden creada con éxito (simulación)"
        )
        
    except Exception as e:
        logger.error(f"Error al simular orden de reabastecimiento: {e}")
        return f"No se pudo crear la orden debido a un error: {str(e)}"


