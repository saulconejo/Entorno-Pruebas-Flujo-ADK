import logging
from factura_data.factura_data import FACTURAS, PAGOS, DEVOLUCIONES, CLIENTES
from datetime import datetime
from typing import Dict, Any
logger = logging.getLogger(__name__)


def resumen_cliente(cliente_id: str) -> Dict[str, Any]:
    """
    Genera un resumen detallado de la situación financiera de un cliente específico.
    
    Args:
        cliente_id (str): ID del cliente a analizar
        
    Returns:
        Dict: Resumen con datos financieros del cliente
    """
    try:
        # Verificar que el cliente existe
        cliente = next((c for c in CLIENTES if c.get("id") == cliente_id), None)
        if not cliente:
            return {
                "error": f"No se encontró el cliente con ID {cliente_id}",
                "cliente_id": cliente_id
            }
        
        # 1. Obtener todas las facturas del cliente
        facturas_cliente = [f for f in FACTURAS if f.get("cliente_id") == cliente_id]
        
        # 2. Calcular total facturado (suma de todas las facturas)
        total_facturado = sum(f.get("total", 0) for f in facturas_cliente)
        
        # 3. Obtener IDs de facturas para búsqueda rápida
        ids_facturas = [f.get("id") for f in facturas_cliente]
        
        # 4. Obtener pagos relacionados con esas facturas
        pagos_cliente = [p for p in PAGOS if p.get("factura_id") in ids_facturas]
        
        # 5. Calcular total pagado
        total_pagado = sum(p.get("monto", 0) for p in pagos_cliente)
        
        # 6. Obtener devoluciones relacionadas con esas facturas
        devoluciones_cliente = [d for d in DEVOLUCIONES if d.get("factura_id") in ids_facturas]
        
        # 7. Calcular total devuelto
        total_devuelto = sum(d.get("total_devuelto", 0) for d in devoluciones_cliente)
        
        # 8. Calcular facturas pendientes (estado "pendiente" o "vencida")
        facturas_pendientes = [f for f in facturas_cliente if f.get("estado") in ["pendiente", "vencida"]]
        
        # 9. Calcular total pendiente de pago
        total_pendiente = sum(f.get("total", 0) for f in facturas_pendientes)
        
        # 10. Organizar facturas por estado
        facturas_por_estado = {
            "pagadas": [f for f in facturas_cliente if f.get("estado") == "pagada"],
            "pendientes": [f for f in facturas_cliente if f.get("estado") == "pendiente"],
            "vencidas": [f for f in facturas_cliente if f.get("estado") == "vencida"]
        }
        
        # Construir el resumen completo
        resumen = {
            "cliente_id": cliente_id,
            "nombre_cliente": cliente.get("nombre", "N/A"),
            "total_facturado": total_facturado,
            "total_pagado": total_pagado,
            "total_devuelto": total_devuelto,
            "deuda_pendiente": total_pendiente,
            "total_facturas": len(facturas_cliente),
            "facturas_pagadas": len(facturas_por_estado["pagadas"]),
            "facturas_pendientes": len(facturas_por_estado["pendientes"]),
            "facturas_vencidas": len(facturas_por_estado["vencidas"]),
            "ultimo_pago": max([p.get("fecha_pago", "1970-01-01T00:00:00Z") for p in pagos_cliente], default="Sin pagos"),
            "devoluciones": [
                {
                    "id": d.get("id"),
                    "fecha": d.get("fecha"),
                    "factura_id": d.get("factura_id"),
                    "monto": d.get("total_devuelto"),
                    "motivo": d.get("motivo")
                } for d in devoluciones_cliente
            ],
            "facturas_detalle": {
                "pendientes": [
                    {
                        "id": f.get("id"),
                        "numero": f.get("numero"),
                        "fecha_emision": f.get("fecha_emision"),
                        "fecha_vencimiento": f.get("fecha_vencimiento"),
                        "total": f.get("total")
                    } for f in facturas_por_estado["pendientes"]
                ],
                "vencidas": [
                    {
                        "id": f.get("id"),
                        "numero": f.get("numero"),
                        "fecha_emision": f.get("fecha_emision"),
                        "fecha_vencimiento": f.get("fecha_vencimiento"),
                        "total": f.get("total"),
                        "dias_retraso": (datetime.now() - datetime.fromisoformat(f.get("fecha_vencimiento", "").replace("Z", "+00:00"))).days if f.get("fecha_vencimiento") else "N/A"
                    } for f in facturas_por_estado["vencidas"]
                ]
            }
        }
        
        return resumen
        
    except Exception as e:
        logger.error(f"Error al generar resumen del cliente {cliente_id}: {e}")
        return {
            "error": f"No se pudo generar el resumen debido a un error: {str(e)}",
            "cliente_id": cliente_id
        }

def generar_informe_cliente_tool(cliente_id: str) -> str:
    """
    Genera un informe detallado y formateado sobre el estado financiero de un cliente.
    
    Args:
        cliente_id (str): ID del cliente a analizar
        
    Returns:
        str: Informe formateado del cliente
    """
    resumen = resumen_cliente(cliente_id)
    
    if "error" in resumen:
        return f"ERROR: {resumen['error']}"
    
    # Formatear el informe en texto
    informe = f"INFORME FINANCIERO DEL CLIENTE: {resumen['nombre_cliente']}\n"
    informe += "====================================================\n\n"
    
    # Información general
    informe += "INFORMACIÓN GENERAL:\n"
    informe += f"ID Cliente: {resumen['cliente_id']}\n"
    informe += f"Nombre: {resumen['nombre_cliente']}\n"
    
    # Resumen financiero
    informe += "\nRESUMEN FINANCIERO:\n"
    informe += f"Total Facturado: {resumen['total_facturado']:.2f} EUR\n"
    informe += f"Total Pagado: {resumen['total_pagado']:.2f} EUR\n"
    informe += f"Total Devuelto: {resumen['total_devuelto']:.2f} EUR\n"
    informe += f"Deuda Pendiente: {resumen['deuda_pendiente']:.2f} EUR\n"
    
    # Histórico de facturas
    informe += "\nESTADÍSTICAS DE FACTURAS:\n"
    informe += f"Total de facturas: {resumen['total_facturas']}\n"
    informe += f"Facturas pagadas: {resumen['facturas_pagadas']}\n"
    informe += f"Facturas pendientes: {resumen['facturas_pendientes']}\n"
    informe += f"Facturas vencidas: {resumen['facturas_vencidas']}\n"
    
    # Último pago
    informe += f"\nÚltimo pago registrado: {resumen['ultimo_pago']}\n"
    
    # Detalle de facturas pendientes
    if resumen['facturas_pendientes'] > 0:
        informe += "\nDETALLE DE FACTURAS PENDIENTES:\n"
        for i, factura in enumerate(resumen['facturas_detalle']['pendientes'], 1):
            informe += f"{i}. Factura {factura['numero']} - {factura['total']:.2f} EUR\n"
            informe += f"   Emitida: {factura['fecha_emision']}\n"
            informe += f"   Vence: {factura['fecha_vencimiento']}\n"
    
    # Detalle de facturas vencidas
    if resumen['facturas_vencidas'] > 0:
        informe += "\nDETALLE DE FACTURAS VENCIDAS:\n"
        for i, factura in enumerate(resumen['facturas_detalle']['vencidas'], 1):
            informe += f"{i}. Factura {factura['numero']} - {factura['total']:.2f} EUR\n"
            informe += f"   Emitida: {factura['fecha_emision']}\n"
            informe += f"   Venció: {factura['fecha_vencimiento']}\n"
            informe += f"   Días de retraso: {factura.get('dias_retraso', 'N/A')}\n"
    
    # Histórico de devoluciones
    if resumen['devoluciones']:
        informe += "\nHISTÓRICO DE DEVOLUCIONES:\n"
        for i, devolucion in enumerate(resumen['devoluciones'], 1):
            informe += f"{i}. Devolución {devolucion['id']} - {devolucion['monto']:.2f} EUR\n"
            informe += f"   Fecha: {devolucion['fecha']}\n"
            informe += f"   Factura: {devolucion['factura_id']}\n"
            informe += f"   Motivo: {devolucion['motivo']}\n"
    else:
        informe += "\nNo hay devoluciones registradas para este cliente.\n"
    
    # Recomendaciones
    informe += "\nANÁLISIS Y RECOMENDACIONES:\n"
    
    if resumen['deuda_pendiente'] > 0:
        porcentaje_pendiente = (resumen['deuda_pendiente'] / resumen['total_facturado']) * 100 if resumen['total_facturado'] > 0 else 0
        
        if porcentaje_pendiente > 50:
            informe += "⚠️ ALERTA: El cliente tiene un alto porcentaje de deuda pendiente.\n"
            informe += "   Se recomienda contactar con urgencia para gestionar los pagos.\n"
        elif porcentaje_pendiente > 25:
            informe += "⚠️ ATENCIÓN: El cliente tiene un porcentaje moderado de deuda pendiente.\n"
            informe += "   Se recomienda hacer seguimiento de las facturas pendientes.\n"
        else:
            informe += "✓ El cliente tiene un nivel de deuda pendiente bajo.\n"
    else:
        informe += "✓ El cliente no tiene deudas pendientes actualmente.\n"
    
    # Conclusión
    if resumen['facturas_vencidas'] > 0:
        informe += "📉 Situación: Cliente con facturas vencidas que requieren atención inmediata.\n"
    elif resumen['facturas_pendientes'] > 0:
        informe += "🔄 Situación: Cliente con pagos pendientes dentro del plazo establecido.\n"
    else:
        informe += "📈 Situación: Cliente con historial de pagos al día.\n"
    
    return informe

def comparar_comportamiento_pago_tool(cliente_id: str) -> str:
    """
    Compara el comportamiento de pago de un cliente con respecto al promedio.
    
    Args:
        cliente_id (str): ID del cliente a analizar
    
    Returns:
        str: Análisis comparativo del comportamiento de pago
    """
    try:
        # Obtener resumen del cliente
        resumen = resumen_cliente(cliente_id)
        
        if "error" in resumen:
            return f"ERROR: {resumen['error']}"
        
        # Calcular estadísticas globales
        total_facturas_sistema = len(FACTURAS)
        total_pagos_sistema = len(PAGOS)
        
        facturas_pagadas_sistema = len([f for f in FACTURAS if f.get("estado") == "pagada"])
        facturas_vencidas_sistema = len([f for f in FACTURAS if f.get("estado") == "vencida"])
        
        # Calcular promedios
        if total_facturas_sistema > 0:
            porcentaje_pagadas_global = (facturas_pagadas_sistema / total_facturas_sistema) * 100
            porcentaje_vencidas_global = (facturas_vencidas_sistema / total_facturas_sistema) * 100
        else:
            porcentaje_pagadas_global = 0
            porcentaje_vencidas_global = 0
        
        # Calcular estadísticas del cliente
        if resumen['total_facturas'] > 0:
            porcentaje_pagadas_cliente = (resumen['facturas_pagadas'] / resumen['total_facturas']) * 100
            porcentaje_vencidas_cliente = (resumen['facturas_vencidas'] / resumen['total_facturas']) * 100
        else:
            porcentaje_pagadas_cliente = 0
            porcentaje_vencidas_cliente = 0
        
        # Preparar análisis comparativo
        comparativa = f"ANÁLISIS COMPARATIVO DE COMPORTAMIENTO DE PAGO\n"
        comparativa += f"Cliente: {resumen['nombre_cliente']} (ID: {cliente_id})\n"
        comparativa += "===================================================\n\n"
        
        comparativa += "COMPARATIVA DE PAGOS:\n"
        comparativa += f"- Facturas pagadas (cliente): {porcentaje_pagadas_cliente:.1f}%\n"
        comparativa += f"- Facturas pagadas (promedio global): {porcentaje_pagadas_global:.1f}%\n"
        
        if porcentaje_pagadas_cliente > porcentaje_pagadas_global:
            comparativa += "✓ Cliente con comportamiento de pago SUPERIOR al promedio\n"
        else:
            comparativa += "⚠️ Cliente con comportamiento de pago INFERIOR al promedio\n"
            
        comparativa += "\nCOMPARATIVA DE VENCIMIENTOS:\n"
        comparativa += f"- Facturas vencidas (cliente): {porcentaje_vencidas_cliente:.1f}%\n"
        comparativa += f"- Facturas vencidas (promedio global): {porcentaje_vencidas_global:.1f}%\n"
        
        if porcentaje_vencidas_cliente < porcentaje_vencidas_global:
            comparativa += "✓ Cliente con tasa de vencimiento MENOR al promedio\n"
        else:
            comparativa += "⚠️ Cliente con tasa de vencimiento MAYOR al promedio\n"
            
        # Añadir conclusión general
        comparativa += "\nCONCLUSIÓN:\n"
        
        if porcentaje_pagadas_cliente > porcentaje_pagadas_global and porcentaje_vencidas_cliente < porcentaje_vencidas_global:
            comparativa += "📈 EXCELENTE: Cliente con comportamiento de pago superior a la media.\n"
            comparativa += "   Recomendación: Considerar aumento de límite de crédito o descuentos adicionales.\n"
        elif porcentaje_pagadas_cliente < porcentaje_pagadas_global and porcentaje_vencidas_cliente > porcentaje_vencidas_global:
            comparativa += "📉 PROBLEMÁTICO: Cliente con comportamiento de pago inferior a la media.\n"
            comparativa += "   Recomendación: Revisión del límite de crédito y condiciones de pago.\n"
        else:
            comparativa += "🔄 NEUTRAL: Comportamiento de pago dentro de parámetros normales.\n"
            comparativa += "   Recomendación: Mantener condiciones actuales y monitoreo regular.\n"
        
        return comparativa
        
    except Exception as e:
        logger.error(f"Error al comparar comportamiento de pago del cliente {cliente_id}: {e}")
        return f"No se pudo realizar el análisis comparativo debido a un error: {str(e)}"

