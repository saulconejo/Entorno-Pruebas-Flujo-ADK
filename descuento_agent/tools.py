import logging
from factura_data.factura_data import (
    FACTURAS,
    PAGOS,
    CLIENTES
)
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def recomendar_descuento_personalizado(cliente_id: str) -> float:
    """
    Calcula un porcentaje de descuento recomendado para un cliente basado en su
    segmento, historial de pagos y volumen total facturado.
    
    Args:
        cliente_id (str): ID del cliente para el que se recomienda descuento
        
    Returns:
        float: Porcentaje de descuento recomendado (entre 0 y 1)
    """
    try:
        # Verificar que el cliente existe
        cliente = next((c for c in CLIENTES if c.get("id") == cliente_id), None)
        if not cliente:
            logger.warning(f"Cliente con ID {cliente_id} no encontrado")
            return 0.0
        
        # 1. Obtener factores base por segmento
        segmento = cliente.get("segmento", "basic").lower()
        factores_segmento = {
            "premium": 0.15,  # Base máxima 15% para clientes premium
            "standard": 0.08,  # Base máxima 8% para clientes estándar
            "basic": 0.05     # Base máxima 5% para clientes básicos
        }
        
        factor_base = factores_segmento.get(segmento, 0.03)
        
        # 2. Analizar historial de pagos
        facturas_cliente = [f for f in FACTURAS if f.get("cliente_id") == cliente_id]
        
        if not facturas_cliente:
            # Cliente sin facturas, usar solo descuento default
            return cliente.get("descuento_default", 0.0)
        
        # Crear conjunto de IDs de facturas para búsqueda rápida
        ids_facturas = {f.get("id") for f in facturas_cliente}
        
        # Obtener pagos del cliente
        pagos_cliente = [p for p in PAGOS if p.get("factura_id") in ids_facturas]
        
        # 3. Calcular factores de ajuste
        
        # 3.1. Factor por volumen (basado en total facturado)
        total_facturado = sum(f.get("total", 0) for f in facturas_cliente)
        
        factor_volumen = 0.0
        if total_facturado > 50000:
            factor_volumen = 0.05  # +5% para volúmenes muy altos
        elif total_facturado > 20000:
            factor_volumen = 0.03  # +3% para volúmenes altos
        elif total_facturado > 10000:
            factor_volumen = 0.02  # +2% para volúmenes medios
        elif total_facturado > 5000:
            factor_volumen = 0.01  # +1% para volúmenes moderados
        
        # 3.2. Factor por puntualidad de pagos
        facturas_pagadas = [f for f in facturas_cliente if f.get("estado") == "pagada"]
        
        if not facturas_pagadas:
            factor_puntualidad = 0.0
        else:
            # Mapear facturas pagadas con sus pagos
            pagos_por_factura = {}
            for pago in pagos_cliente:
                factura_id = pago.get("factura_id")
                if factura_id not in pagos_por_factura:
                    pagos_por_factura[factura_id] = []
                pagos_por_factura[factura_id].append(pago)
            
            # Contar pagos puntuales vs pagos tardíos
            pagos_puntuales = 0
            pagos_tardios = 0
            
            for factura in facturas_pagadas:
                fecha_vencimiento = factura.get("fecha_vencimiento")
                fecha_pago = factura.get("fecha_pago")
                
                if fecha_vencimiento and fecha_pago:
                    fecha_venc = datetime.fromisoformat(fecha_vencimiento.replace("Z", "+00:00"))
                    fecha_pg = datetime.fromisoformat(fecha_pago.replace("Z", "+00:00"))
                    
                    if fecha_pg <= fecha_venc:
                        pagos_puntuales += 1
                    else:
                        pagos_tardios += 1
            
            # Si hay al menos 3 facturas para estadística relevante
            if (pagos_puntuales + pagos_tardios) >= 3:
                ratio_puntualidad = pagos_puntuales / (pagos_puntuales + pagos_tardios)
                
                # Ajustar factor por puntualidad
                if ratio_puntualidad >= 0.95:  # Excelente puntualidad (>95%)
                    factor_puntualidad = 0.05
                elif ratio_puntualidad >= 0.8:  # Muy buena puntualidad (80-95%)
                    factor_puntualidad = 0.03
                elif ratio_puntualidad >= 0.7:  # Buena puntualidad (70-80%)
                    factor_puntualidad = 0.01
                elif ratio_puntualidad < 0.5:  # Mala puntualidad (<50%)
                    factor_puntualidad = -0.03  # Penalización
                else:
                    factor_puntualidad = 0.0
            else:
                # Datos insuficientes
                factor_puntualidad = 0.0
        
        # 3.3. Factor por antigüedad como cliente
        if "fecha_registro" in cliente:
            try:
                fecha_registro = datetime.fromisoformat(cliente["fecha_registro"].replace("Z", "+00:00"))
                dias_antiguedad = (datetime.now() - fecha_registro).days
                
                if dias_antiguedad > 730:  # Más de 2 años
                    factor_antiguedad = 0.02
                elif dias_antiguedad > 365:  # Más de 1 año
                    factor_antiguedad = 0.01
                else:
                    factor_antiguedad = 0.0
            except:
                factor_antiguedad = 0.0
        else:
            factor_antiguedad = 0.0
        
        # 3.4. Factor de penalización por facturas vencidas actuales
        facturas_vencidas = [f for f in facturas_cliente if f.get("estado") == "vencida"]
        if facturas_vencidas:
            factor_penalizacion = -0.05  # Penalización significativa
        else:
            factor_penalizacion = 0.0
        
        # 4. Calcular descuento final combinando todos los factores
        descuento_recomendado = (
            factor_base + 
            factor_volumen + 
            factor_puntualidad + 
            factor_antiguedad + 
            factor_penalizacion
        )
        
        # 5. Limitar el rango del descuento entre 0 y el máximo permitido según segmento
        descuento_final = max(0.0, min(descuento_recomendado, 
                                       # Máximos absolutos por segmento
                                       0.25 if segmento == "premium" else
                                       0.15 if segmento == "standard" else 0.1))
        
        return round(descuento_final, 2)  # Redondear a 2 decimales
        
    except Exception as e:
        logger.error(f"Error al calcular descuento personalizado para cliente {cliente_id}: {e}")
        # En caso de error, devolver el descuento predeterminado del cliente o 0
        try:
            return next((c.get("descuento_default", 0.0) for c in CLIENTES if c.get("id") == cliente_id), 0.0)
        except:
            return 0.0

def explicar_calculo_descuento_tool(cliente_id: str) -> str:
    """
    Genera una explicación detallada del cálculo de descuento recomendado para un cliente.
    
    Args:
        cliente_id (str): ID del cliente
        
    Returns:
        str: Explicación detallada del cálculo
    """
    try:
        # Verificar que el cliente existe
        cliente = next((c for c in CLIENTES if c.get("id") == cliente_id), None)
        if not cliente:
            return f"No se encontró el cliente con ID {cliente_id}"
        
        # Calcular el descuento recomendado
        descuento = recomendar_descuento_personalizado(cliente_id)
        
        # Obtener datos para explicación
        segmento = cliente.get("segmento", "basic")
        
        # Factores por segmento
        factores_segmento = {
            "premium": 0.15,
            "standard": 0.08,
            "basic": 0.05
        }
        
        factor_base = factores_segmento.get(segmento.lower(), 0.03)
        
        # Calcular el total facturado
        facturas_cliente = [f for f in FACTURAS if f.get("cliente_id") == cliente_id]
        total_facturado = sum(f.get("total", 0) for f in facturas_cliente)
        
        # Obtener facturas pagadas y calcular puntualidad
        facturas_pagadas = [f for f in facturas_cliente if f.get("estado") == "pagada"]
        pagos_puntuales = 0
        pagos_tardios = 0
        
        for factura in facturas_pagadas:
            fecha_vencimiento = factura.get("fecha_vencimiento")
            fecha_pago = factura.get("fecha_pago")
            
            if fecha_vencimiento and fecha_pago:
                fecha_venc = datetime.fromisoformat(fecha_vencimiento.replace("Z", "+00:00"))
                fecha_pg = datetime.fromisoformat(fecha_pago.replace("Z", "+00:00"))
                
                if fecha_pg <= fecha_venc:
                    pagos_puntuales += 1
                else:
                    pagos_tardios += 1
        
        # Calcular ratio de puntualidad
        total_pagos = pagos_puntuales + pagos_tardios
        ratio_puntualidad = pagos_puntuales / total_pagos if total_pagos > 0 else 0
        
        # Calcular antigüedad
        if "fecha_registro" in cliente:
            try:
                fecha_registro = datetime.fromisoformat(cliente["fecha_registro"].replace("Z", "+00:00"))
                dias_antiguedad = (datetime.now() - fecha_registro).days
                antiguedad_anios = dias_antiguedad / 365.0
            except:
                antiguedad_anios = 0
        else:
            antiguedad_anios = 0
        
        # Facturas vencidas actuales
        facturas_vencidas = len([f for f in facturas_cliente if f.get("estado") == "vencida"])
        
        # Generar la explicación
        explicacion = f"EXPLICACIÓN DEL DESCUENTO RECOMENDADO: {descuento*100:.1f}%\n"
        explicacion += f"Cliente: {cliente.get('nombre', 'N/A')} (ID: {cliente_id})\n"
        explicacion += "===========================================================\n\n"
        
        explicacion += "FACTORES CONSIDERADOS:\n\n"
        
        # 1. Factor por segmento
        explicacion += f"1. SEGMENTO DEL CLIENTE: {segmento.upper()}\n"
        explicacion += f"   Base de descuento para segmento {segmento}: {factor_base*100:.1f}%\n\n"
        
        # 2. Factor por volumen
        explicacion += f"2. VOLUMEN DE FACTURACIÓN\n"
        explicacion += f"   Total facturado: {total_facturado:.2f} EUR\n"
        
        if total_facturado > 50000:
            explicacion += "   Volumen muy alto → +5% adicional\n\n"
        elif total_facturado > 20000:
            explicacion += "   Volumen alto → +3% adicional\n\n"
        elif total_facturado > 10000:
            explicacion += "   Volumen medio → +2% adicional\n\n"
        elif total_facturado > 5000:
            explicacion += "   Volumen moderado → +1% adicional\n\n"
        else:
            explicacion += "   Volumen bajo → Sin ajuste adicional\n\n"
        
        # 3. Factor por puntualidad
        explicacion += f"3. HISTORIAL DE PAGOS\n"
        explicacion += f"   Total facturas pagadas analizadas: {total_pagos}\n"
        explicacion += f"   Pagos puntuales: {pagos_puntuales}\n"
        explicacion += f"   Pagos tardíos: {pagos_tardios}\n"
        explicacion += f"   Ratio de puntualidad: {ratio_puntualidad*100:.1f}%\n"
        
        if total_pagos < 3:
            explicacion += "   Datos insuficientes para análisis estadístico → Sin ajuste\n\n"
        elif ratio_puntualidad >= 0.95:
            explicacion += "   Excelente puntualidad → +5% adicional\n\n"
        elif ratio_puntualidad >= 0.8:
            explicacion += "   Muy buena puntualidad → +3% adicional\n\n"
        elif ratio_puntualidad >= 0.7:
            explicacion += "   Buena puntualidad → +1% adicional\n\n"
        elif ratio_puntualidad < 0.5:
            explicacion += "   Mala puntualidad → -3% (penalización)\n\n"
        else:
            explicacion += "   Puntualidad media → Sin ajuste\n\n"
        
        # 4. Factor por antigüedad
        explicacion += f"4. ANTIGÜEDAD COMO CLIENTE\n"
        explicacion += f"   Tiempo como cliente: {antiguedad_anios:.1f} años\n"
        
        if antiguedad_anios > 2:
            explicacion += "   Cliente de larga relación → +2% adicional\n\n"
        elif antiguedad_anios > 1:
            explicacion += "   Cliente consolidado → +1% adicional\n\n"
        else:
            explicacion += "   Cliente reciente → Sin ajuste adicional\n\n"
        
        # 5. Penalizaciones
        explicacion += f"5. FACTURAS VENCIDAS ACTUALES\n"
        if facturas_vencidas > 0:
            explicacion += f"   {facturas_vencidas} factura(s) vencida(s) → -5% (penalización)\n\n"
        else:
            explicacion += "   Sin facturas vencidas → Sin penalización\n\n"
        
        # Resumen final
        explicacion += "RESULTADO FINAL:\n"
        explicacion += f"Descuento recomendado: {descuento*100:.1f}%\n"
        
        if descuento == 0:
            explicacion += "\nOBSERVACIONES: No se recomienda aplicar descuento debido a factores negativos presentes."
        elif descuento >= 0.2:
            explicacion += "\nOBSERVACIONES: Cliente de alto valor con excelente historial. Se recomienda mantener este descuento preferencial."
        elif descuento >= 0.1:
            explicacion += "\nOBSERVACIONES: Cliente con buen desempeño. El descuento refleja su valor para la empresa."
        else:
            explicacion += "\nOBSERVACIONES: Se recomienda un descuento moderado basado en los factores analizados."
        
        return explicacion
        
    except Exception as e:
        logger.error(f"Error al explicar cálculo de descuento para cliente {cliente_id}: {e}")
        return f"No se pudo generar la explicación del descuento debido a un error: {str(e)}"

from typing import Optional

def simular_impacto_descuento_tool(cliente_id: str, descuento: Optional[float] = None) -> str:
    """
    Simula el impacto financiero de aplicar un descuento específico a un cliente.
    
    Args:
        cliente_id (str): ID del cliente
        descuento (Optional[float]): Descuento a simular (si None, usa el recomendado)
        
    Returns:
        str: Análisis del impacto financiero
    """
    try:
        # Verificar que el cliente existe
        cliente = next((c for c in CLIENTES if c.get("id") == cliente_id), None)
        if not cliente:
            return f"No se encontró el cliente con ID {cliente_id}"
        
        # Si no se especifica descuento, usar el recomendado
        if descuento is None:
            descuento = recomendar_descuento_personalizado(cliente_id)
        
        # Obtener facturas pendientes del cliente
        facturas_pendientes = [f for f in FACTURAS 
                              if f.get("cliente_id") == cliente_id and f.get("estado") == "pendiente"]
        
        # Si no hay facturas pendientes, simular con datos históricos
        if not facturas_pendientes:
            # Usar datos de los últimos 6 meses para proyección
            seis_meses_atras = datetime.now() - timedelta(days=180)
            
            facturas_ultimos_6_meses = [
                f for f in FACTURAS 
                if f.get("cliente_id") == cliente_id and 
                datetime.fromisoformat(f.get("fecha_emision", "").replace("Z", "+00:00")) > seis_meses_atras
            ]
            
            if not facturas_ultimos_6_meses:
                return f"No hay datos suficientes para simular el impacto del descuento para el cliente {cliente.get('nombre', 'N/A')}"
            
            # Calcular promedio mensual de facturación
            total_facturado_6_meses = sum(f.get("total", 0) for f in facturas_ultimos_6_meses)
            promedio_mensual = total_facturado_6_meses / 6
            
            # Proyectar para próximos 3 meses
            proyeccion_3_meses = promedio_mensual * 3
            
            # Calcular impacto del descuento
            descuento_actual = cliente.get("descuento_default", 0)
            
            impacto_mensual = promedio_mensual * (descuento - descuento_actual)
            impacto_trimestral = proyeccion_3_meses * (descuento - descuento_actual)
            
            # Generar informe
            informe = f"SIMULACIÓN DE IMPACTO DE DESCUENTO PARA CLIENTE: {cliente.get('nombre', 'N/A')}\n"
            informe += "==================================================================\n\n"
            
            informe += "DATOS DE REFERENCIA (ÚLTIMOS 6 MESES):\n"
            informe += f"Total facturado: {total_facturado_6_meses:.2f} EUR\n"
            informe += f"Promedio mensual: {promedio_mensual:.2f} EUR\n\n"
            
            informe += "SIMULACIÓN DE DESCUENTO:\n"
            informe += f"Descuento actual: {descuento_actual*100:.1f}%\n"
            informe += f"Descuento propuesto: {descuento*100:.1f}%\n"
            informe += f"Diferencia: {(descuento-descuento_actual)*100:.1f} puntos porcentuales\n\n"
            
            informe += "IMPACTO FINANCIERO PROYECTADO:\n"
            informe += f"Impacto mensual estimado: {abs(impacto_mensual):.2f} EUR {'menos' if impacto_mensual > 0 else 'más'} de margen\n"
            informe += f"Impacto trimestral estimado: {abs(impacto_trimestral):.2f} EUR {'menos' if impacto_trimestral > 0 else 'más'} de margen\n\n"
            
            # Análisis de rentabilidad
            if impacto_trimestral > 500:
                informe += "⚠️ ADVERTENCIA: El impacto financiero es significativo. Reconsiderar el aumento de descuento.\n"
            elif impacto_mensual < 0:
                informe += "✓ El cambio representa un incremento en el margen. Recomendable.\n"
            else:
                informe += "ℹ️ El impacto financiero es moderado y puede compensarse con mayor fidelización del cliente.\n"
            
        else:
            # Simulación con facturas pendientes reales
            total_pendiente = sum(f.get("total", 0) for f in facturas_pendientes)
            descuento_actual = cliente.get("descuento_default", 0)
            
            # Calcular el impacto en facturas pendientes
            impacto_inmediato = total_pendiente * (descuento - descuento_actual)
            
            # Generar informe
            informe = f"SIMULACIÓN DE IMPACTO DE DESCUENTO PARA CLIENTE: {cliente.get('nombre', 'N/A')}\n"
            informe += "==================================================================\n\n"
            
            informe += "FACTURAS PENDIENTES ACTUALES:\n"
            informe += f"Total de facturas pendientes: {len(facturas_pendientes)}\n"
            informe += f"Monto total pendiente: {total_pendiente:.2f} EUR\n\n"
            
            informe += "SIMULACIÓN DE DESCUENTO:\n"
            informe += f"Descuento actual: {descuento_actual*100:.1f}%\n"
            informe += f"Descuento propuesto: {descuento*100:.1f}%\n"
            informe += f"Diferencia: {(descuento-descuento_actual)*100:.1f} puntos porcentuales\n\n"
            
            informe += "IMPACTO FINANCIERO INMEDIATO:\n"
            informe += f"Reducción de margen en facturas pendientes: {abs(impacto_inmediato):.2f} EUR\n\n"
            
            # Análisis de rentabilidad
            if impacto_inmediato > 500:
                informe += "⚠️ ADVERTENCIA: El impacto financiero inmediato es significativo.\n"
                informe += "   Considerar implementación gradual del nuevo descuento.\n"
            elif descuento < descuento_actual:
                informe += "✓ La reducción del descuento mejorará los márgenes inmediatos.\n"
                informe += "   Monitorear posible impacto en satisfacción del cliente.\n"
            else:
                informe += "ℹ️ El impacto inmediato es aceptable considerando el valor del cliente.\n"
            
        # Añadir recomendación final
        informe += "\nRECOMENDACIÓN FINAL:\n"
        
        if descuento > descuento_actual + 0.05:
            informe += "Implementar el aumento de descuento de forma gradual:\n"
            informe += f"1. Inmediato: {(descuento_actual + 0.02)*100:.1f}%\n"
            informe += f"2. En 3 meses: {(descuento_actual + 0.04)*100:.1f}%\n"
            informe += f"3. En 6 meses (si se mantiene el buen historial): {descuento*100:.1f}%\n"
        elif descuento < descuento_actual - 0.03:
            informe += "Reducir el descuento de forma gradual para evitar impacto negativo:\n"
            informe += f"1. Notificar al cliente con 30 días de antelación\n"
            informe += f"2. Aplicar descuento intermedio de {(descuento_actual - 0.015)*100:.1f}% durante 2 meses\n"
            informe += f"3. Finalmente aplicar el {descuento*100:.1f}% recomendado\n"
        else:
            informe += f"Aplicar el descuento recomendado de {descuento*100:.1f}% en próxima facturación.\n"
            informe += "Revisar impacto en 3 meses.\n"
        
        return informe
        
    except Exception as e:
        logger.error(f"Error al simular impacto de descuento para cliente {cliente_id}: {e}")
        return f"No se pudo realizar la simulación debido a un error: {str(e)}"
