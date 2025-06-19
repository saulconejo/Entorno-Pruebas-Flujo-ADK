from factura_data.factura_data import FACTURAS, CLIENTES
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def generar_alertas_credito() -> List[Dict[str, Any]]:
    """
    Identifica clientes que han superado su límite de crédito y tienen facturas vencidas.
    
    Returns:
        List[Dict]: Lista de alertas con información de clientes en situación crítica
    """
    try:
        # Crear diccionario para acumular deudas por cliente
        deudas_por_cliente = {}
        facturas_por_cliente = {}
        
        # Filtrar facturas vencidas y pendientes (estados que representan deuda)
        facturas_con_deuda = [f for f in FACTURAS if f.get("estado") in ["vencida", "pendiente"]]
        
        # Agrupar facturas y acumular deuda por cliente
        for factura in facturas_con_deuda:
            cliente_id = factura.get("cliente_id")
            if cliente_id:
                # Inicializar si es el primer registro para este cliente
                if cliente_id not in deudas_por_cliente:
                    deudas_por_cliente[cliente_id] = 0
                    facturas_por_cliente[cliente_id] = []
                
                # Acumular deuda
                deudas_por_cliente[cliente_id] += factura.get("total", 0)
                
                # Almacenar referencia a la factura
                facturas_por_cliente[cliente_id].append({
                    "id": factura.get("id"),
                    "numero": factura.get("numero"),
                    "fecha_emision": factura.get("fecha_emision"),
                    "fecha_vencimiento": factura.get("fecha_vencimiento"),
                    "total": factura.get("total"),
                    "estado": factura.get("estado")
                })
        
        # Crear diccionario para acceso rápido a información de clientes
        clientes_por_id = {cliente["id"]: cliente for cliente in CLIENTES}
        
        # Generar alertas para clientes que superan su límite de crédito
        alertas = []
        for cliente_id, deuda_total in deudas_por_cliente.items():
            # Verificar que el cliente existe en nuestros registros
            if cliente_id not in clientes_por_id:
                continue
                
            cliente = clientes_por_id[cliente_id]
            limite_credito = cliente.get("limite_credito", 0)
            
            # Verificar si hay facturas vencidas (no solo pendientes)
            tiene_facturas_vencidas = any(f["estado"] == "vencida" for f in facturas_por_cliente[cliente_id])
            
            # Crear alerta si supera el límite y tiene facturas vencidas
            if deuda_total > limite_credito and tiene_facturas_vencidas:
                # Filtrar solo las facturas vencidas para la alerta
                facturas_vencidas = [f for f in facturas_por_cliente[cliente_id] if f["estado"] == "vencida"]
                
                # Calcular días de retraso promedio
                dias_retraso = []
                for factura in facturas_vencidas:
                    if "fecha_vencimiento" in factura and factura["fecha_vencimiento"]:
                        fecha_vencimiento = datetime.fromisoformat(factura["fecha_vencimiento"].replace("Z", "+00:00"))
                        dias = (datetime.now() - fecha_vencimiento).days
                        dias_retraso.append(dias)
                
                dias_promedio = sum(dias_retraso) / len(dias_retraso) if dias_retraso else 0
                
                # Crear la alerta con información detallada
                alertas.append({
                    "cliente_id": cliente_id,
                    "nombre_cliente": cliente.get("nombre", "N/A"),
                    "limite_credito": limite_credito,
                    "deuda_total": deuda_total,
                    "exceso_credito": deuda_total - limite_credito,
                    "porcentaje_exceso": ((deuda_total - limite_credito) / limite_credito) * 100 if limite_credito > 0 else 0,
                    "facturas_vencidas": len(facturas_vencidas),
                    "total_vencido": sum(f["total"] for f in facturas_vencidas),
                    "dias_promedio_retraso": int(dias_promedio),
                    "riesgo_impago": cliente.get("riesgo_impago", 0),
                    "detalle_facturas": facturas_vencidas,
                    "nivel_alerta": "ALTA" if deuda_total > limite_credito * 1.5 else "MEDIA",
                    "fecha_alerta": datetime.now().isoformat()
                })
        
        # Ordenar alertas por porcentaje de exceso (de mayor a menor)
        alertas.sort(key=lambda a: a["porcentaje_exceso"], reverse=True)
        
        return alertas
        
    except Exception as e:
        logger.error(f"Error al generar alertas de crédito: {e}")
        return []

def formatear_alertas_credito_tool() -> str:
    """
    Formatea las alertas de crédito para presentación detallada.
    
    Returns:
        str: Informe formateado con alertas de crédito
    """
    alertas = generar_alertas_credito()
    
    if not alertas:
        return "No se han detectado alertas de crédito en este momento. Todos los clientes se encuentran dentro de sus límites de crédito o no tienen facturas vencidas."
    
    # Formatear informe de alertas
    informe = "ALERTA DE CRÉDITO: CLIENTES QUE SUPERAN SU LÍMITE\n"
    informe += "==============================================\n\n"
    informe += f"Total de alertas identificadas: {len(alertas)}\n"
    informe += f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for i, alerta in enumerate(alertas, 1):
        informe += f"ALERTA {i} - NIVEL: {alerta['nivel_alerta']}\n"
        informe += f"Cliente: {alerta['nombre_cliente']} (ID: {alerta['cliente_id']})\n"
        informe += f"Límite de crédito: {alerta['limite_credito']:.2f} EUR\n"
        informe += f"Deuda total: {alerta['deuda_total']:.2f} EUR\n"
        informe += f"Exceso: {alerta['exceso_credito']:.2f} EUR ({alerta['porcentaje_exceso']:.1f}%)\n"
        informe += f"Facturas vencidas: {alerta['facturas_vencidas']}\n"
        informe += f"Promedio de días de retraso: {alerta['dias_promedio_retraso']} días\n"
        informe += f"Riesgo de impago registrado: {alerta['riesgo_impago'] * 100:.1f}%\n"
        
        # Detallar facturas vencidas
        informe += "\nDetalle de facturas vencidas:\n"
        for j, factura in enumerate(alerta['detalle_facturas'], 1):
            informe += f"  {j}. Factura {factura['numero']} - {factura['total']:.2f} EUR\n"
            informe += f"     Vencimiento: {factura['fecha_vencimiento']}\n"
        
        # Añadir recomendaciones basadas en la severidad
        informe += "\nRECOMENDACIONES:\n"
        
        if alerta['nivel_alerta'] == "ALTA":
            informe += "- ACCIÓN INMEDIATA: Contactar al cliente para regularización urgente\n"
            informe += "- Suspender nuevos créditos hasta regularización\n"
            informe += "- Considerar plan de pago escalonado\n"
            if alerta['riesgo_impago'] > 0.5:
                informe += "- ALERTA DE RIESGO: Evaluar acciones de cobro preventivas\n"
        else:
            informe += "- Contactar al cliente para verificar situación de pago\n"
            informe += "- Monitorear actividad en próximos 7 días\n"
            informe += "- Evaluar ajuste temporal de límite de crédito\n"
        
        informe += "\n" + "-" * 50 + "\n\n"
    
    return informe

def recomendar_acciones_cliente_tool(cliente_id: str) -> str:
    """
    Genera recomendaciones específicas para un cliente con problemas de crédito.
    
    Args:
        cliente_id (str): ID del cliente a analizar
        
    Returns:
        str: Recomendaciones personalizadas
    """
    try:
        # Obtener todas las alertas
        todas_alertas = generar_alertas_credito()
        
        # Buscar si el cliente específico tiene una alerta
        alerta = next((a for a in todas_alertas if a["cliente_id"] == cliente_id), None)
        
        if not alerta:
            # Verificar que el cliente existe
            cliente = next((c for c in CLIENTES if c["id"] == cliente_id), None)
            
            if not cliente:
                return f"Error: No se encontró el cliente con ID {cliente_id}"
            
            # Si el cliente existe pero no tiene alertas, verificar su situación
            facturas_cliente = [f for f in FACTURAS if f.get("cliente_id") == cliente_id]
            facturas_vencidas = [f for f in facturas_cliente if f.get("estado") == "vencida"]
            facturas_pendientes = [f for f in facturas_cliente if f.get("estado") == "pendiente"]
            
            deuda_total = sum(f.get("total", 0) for f in facturas_vencidas + facturas_pendientes)
            limite_credito = cliente.get("limite_credito", 0)
            
            if not facturas_cliente:
                return f"El cliente {cliente.get('nombre', 'N/A')} no tiene facturas registradas en el sistema."
            
            if not facturas_vencidas and not facturas_pendientes:
                return f"El cliente {cliente.get('nombre', 'N/A')} no tiene facturas pendientes ni vencidas. Situación de crédito: NORMAL."
            
            if deuda_total <= limite_credito * 0.7:
                return f"El cliente {cliente.get('nombre', 'N/A')} tiene una deuda de {deuda_total:.2f} EUR, que está dentro de límites aceptables (límite: {limite_credito:.2f} EUR). No requiere acciones especiales."
            
            if deuda_total > limite_credito * 0.7 and deuda_total <= limite_credito:
                return f"ATENCIÓN: El cliente {cliente.get('nombre', 'N/A')} está utilizando un {(deuda_total/limite_credito)*100:.1f}% de su límite de crédito. Se recomienda monitoreo para evitar excesos."
            
            return f"El cliente {cliente.get('nombre', 'N/A')} tiene deuda acumulada pero no facturas vencidas. Situación a monitorear pero no requiere acciones inmediatas."
        
        # Si el cliente tiene una alerta, generar recomendaciones personalizadas
        recomendaciones = f"PLAN DE ACCIÓN PARA CLIENTE: {alerta['nombre_cliente']}\n"
        recomendaciones += "=================================================\n\n"
        
        recomendaciones += "SITUACIÓN ACTUAL:\n"
        recomendaciones += f"- Límite de crédito: {alerta['limite_credito']:.2f} EUR\n"
        recomendaciones += f"- Deuda actual: {alerta['deuda_total']:.2f} EUR\n"
        recomendaciones += f"- Exceso: {alerta['exceso_credito']:.2f} EUR ({alerta['porcentaje_exceso']:.1f}%)\n"
        recomendaciones += f"- Facturas vencidas: {alerta['facturas_vencidas']}\n"
        recomendaciones += f"- Días promedio de retraso: {alerta['dias_promedio_retraso']}\n\n"
        
        recomendaciones += "ACCIONES RECOMENDADAS:\n"
        
        # Plan personalizado según la severidad
        if alerta['porcentaje_exceso'] > 50:
            recomendaciones += "1. URGENTE: Contacto telefónico inmediato con responsable de pagos\n"
            recomendaciones += "2. Suspensión temporal de nuevos servicios/productos\n"
            recomendaciones += "3. Solicitar pago del 50% del exceso en próximos 7 días\n"
            recomendaciones += "4. Proponer plan de pago estructurado para el saldo restante\n"
            recomendaciones += "5. Registro en sistema de seguimiento especial\n"
            recomendaciones += "6. Revisión de términos de crédito para futuras operaciones\n"
        elif alerta['porcentaje_exceso'] > 20:
            recomendaciones += "1. Contacto con responsable de pagos en próximas 24 horas\n"
            recomendaciones += "2. Limitación temporal de nuevos pedidos al 50% del límite habitual\n"
            recomendaciones += "3. Solicitar cronograma de pagos para regularización\n"
            recomendaciones += "4. Seguimiento semanal hasta regularización\n"
            recomendaciones += "5. Evaluar ajustes al límite de crédito\n"
        else:
            recomendaciones += "1. Enviar comunicación formal recordando situación de crédito\n"
            recomendaciones += "2. Solicitar confirmación de fechas de pago\n"
            recomendaciones += "3. Monitoreo quincenal de la situación\n"
            recomendaciones += "4. Considerar ajustes preventivos al límite de crédito\n"
        
        # Añadir consideraciones basadas en el historial del cliente
        if alerta['riesgo_impago'] > 0.6:
            recomendaciones += "\nCONSIDERACIONES ADICIONALES POR ALTO RIESGO:\n"
            recomendaciones += "- Evaluar garantías adicionales para operaciones futuras\n"
            recomendaciones += "- Revisar historial completo de pagos de los últimos 12 meses\n"
            recomendaciones += "- Considerar cambio a modalidad de prepago para próximos servicios\n"
        
        recomendaciones += "\nSEGUIMIENTO:\n"
        recomendaciones += "- Programar revisión de estado en 7 días\n"
        recomendaciones += "- Documentar todas las comunicaciones con el cliente\n"
        recomendaciones += f"- Responsable sugerido: Gestor de cuentas asignado al segmento {alerta.get('segmento', 'estándar')}\n"
        
        return recomendaciones
        
    except Exception as e:
        logger.error(f"Error al generar recomendaciones para cliente {cliente_id}: {e}")
        return f"No se pudieron generar recomendaciones debido a un error: {str(e)}"
