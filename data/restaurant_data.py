from typing import List, Dict, Optional

# Constantes y datos del restaurante
MENU_ITEMS = {
    "paella": {
        "name": "Paella Valenciana",
        "category": "principales",
        "price": 18.50,
        "ingredients": ["arroz", "pollo", "conejo", "judías verdes", "garrofón", "tomate", "azafrán"],
        "dietary": ["sin lácteos"],
        "prep_time": 45,
        "available": True
    },
    "tortilla": {
        "name": "Tortilla Española",
        "category": "entrantes",
        "price": 9.00,
        "ingredients": ["patata", "cebolla", "huevo", "aceite de oliva"],
        "dietary": ["vegetariano", "sin gluten"],
        "prep_time": 25,
        "available": True
    },
    "gazpacho": {
        "name": "Gazpacho Andaluz",
        "category": "entrantes",
        "price": 7.50,
        "ingredients": ["tomate", "pimiento", "pepino", "ajo", "aceite de oliva", "vinagre"],
        "dietary": ["vegano", "sin gluten", "sin lácteos"],
        "prep_time": 15,
        "available": True
    },
    # ... más platos aquí ...
}

TABLES = {
    1: {"capacity": 2, "location": "ventana", "available": True},
    2: {"capacity": 4, "location": "interior", "available": True},
    3: {"capacity": 6, "location": "terraza", "available": True},
    4: {"capacity": 8, "location": "salon_privado", "available": True},
    5: {"capacity": 12, "location": "salon_principal", "available": True},
}

RESERVATIONS = {}  # Almacena las reservas activas

# Funciones para el modelo
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

# Herramientas definidas directamente

def filter_menu_by_dietary_tool(dietary_restriction: str):
    """Filtra el menú por restricciones dietéticas (vegetariano, vegano, sin gluten)."""
    filtered_dishes = []
    for dish_id, details in MENU_ITEMS.items():
        if details.get("available", False) and dietary_restriction.lower() in [d.lower() for d in details.get("dietary", [])]:
            filtered_dishes.append(details["name"])
    
    if not filtered_dishes:
        return f"No encontramos platos que cumplan con la restricción '{dietary_restriction}'."
    
    return filtered_dishes

def find_dishes_by_ingredient_tool(ingredient: str):
    """Encuentra platos que contienen un ingrediente específico."""
    dishes_with_ingredient = []
    for dish_id, details in MENU_ITEMS.items():
        if details.get("available", False) and ingredient.lower() in [i.lower() for i in details.get("ingredients", [])]:
            dishes_with_ingredient.append(details["name"])
    
    if not dishes_with_ingredient:
        return f"No encontramos platos que contengan '{ingredient}'."
    
    return dishes_with_ingredient

def estimate_preparation_time_tool(menu_items: List[str]):
    """Devuelve el tiempo estimado de preparación para los platos indicados."""
    total_time = 0
    not_found = []
    found_dishes = []
    
    for item in menu_items:
        item_found = False
        for dish_id, details in MENU_ITEMS.items():
            if details["name"].lower() == item.lower() or dish_id.lower() == item.lower():
                total_time += details.get("prep_time", 0)
                found_dishes.append(details["name"])
                item_found = True
                break
        
        if not item_found:
            not_found.append(item)
    
    if not found_dishes:
        return "No se encontraron los platos indicados en nuestro menú."
    
    result = f"Tiempo total de preparación: {total_time} minutos para {', '.join(found_dishes)}."
    if not_found:
        result += f" No encontramos: {', '.join(not_found)}."
    
    return result

def list_menu_categories_tool():
    """Lista todas las categorías del menú (entrantes, principales, postres, etc.)."""
    categories = set()
    for dish in MENU_ITEMS.values():
        if "category" in dish:
            categories.add(dish["category"])
    
    return sorted(list(categories))

def get_dishes_by_category_tool(category: str):
    """Obtiene todos los platos de una categoría específica."""
    dishes = []
    for dish_id, details in MENU_ITEMS.items():
        if details.get("category", "").lower() == category.lower() and details.get("available", False):
            dishes.append({
                "name": details["name"],
                "price": details.get("price", "Precio no disponible")
            })
    
    if not dishes:
        return f"No encontramos platos en la categoría '{category}'."
    
    return dishes

def get_dish_details_tool(dish_name: str):
    """Obtiene la información completa de un plato (precio, ingredientes, etc.)"""
    for dish_id, details in MENU_ITEMS.items():
        if details["name"].lower() == dish_name.lower() or dish_id.lower() == dish_name.lower():
            return {
                "name": details["name"],
                "price": details.get("price", "Precio no disponible"),
                "ingredients": details.get("ingredients", []),
                "dietary": details.get("dietary", []),
                "preparation_time": details.get("prep_time", "Tiempo no especificado"),
                "available": details.get("available", False)
            }
    
    return f"No encontramos el plato '{dish_name}' en nuestro menú."

def check_table_availability_tool(party_size: int, date: str, time: str):
    """Verifica la disponibilidad de mesas para un número de personas en una fecha y hora específicas."""
    available_tables = []
    
    # Comprobamos qué mesas pueden acomodar el número de personas
    for table_id, table_details in TABLES.items():
        if table_details["capacity"] >= party_size and table_details.get("available", False):
            # Verificar que no esté reservada para esa fecha y hora
            reservation_key = f"{date}_{time}_{table_id}"
            if reservation_key not in RESERVATIONS:
                available_tables.append({
                    "table_id": table_id,
                    "capacity": table_details["capacity"],
                    "location": table_details.get("location", "No especificada")
                })
    
    if not available_tables:
        return f"Lo sentimos, no hay mesas disponibles para {party_size} personas en {date} a las {time}."
    
    return {
        "available": True,
        "message": f"Tenemos {len(available_tables)} mesa(s) disponible(s) para {party_size} personas en {date} a las {time}.",
        "tables": available_tables
    }

def create_reservation_tool(name: str, party_size: int, date: str, time: str, phone: Optional[str] = None, special_requests: Optional[str] = None):
    """Crea una nueva reserva con los detalles proporcionados."""
    # Buscar mesa disponible
    available_tables_info = check_table_availability_tool(party_size, date, time)
    
    if not isinstance(available_tables_info, dict) or not available_tables_info.get("available", False):
        return "No hay mesas disponibles para esa fecha y hora. Por favor, intente con otro horario."
    
    # Asignar la primera mesa disponible
    selected_table = available_tables_info["tables"][0]["table_id"]
    
    # Generar ID único para la reserva
    import uuid
    reservation_id = str(uuid.uuid4())[:8]  # ID corto para fácil referencia
    
    # Guardar la reserva
    reservation_key = f"{date}_{time}_{selected_table}"
    RESERVATIONS[reservation_key] = {
        "id": reservation_id,
        "name": name,
        "party_size": party_size,
        "date": date,
        "time": time,
        "table": selected_table,
        "phone": phone,
        "special_requests": special_requests
    }
    
    # Añadir referencia para búsqueda por nombre
    if name not in RESERVATIONS:
        RESERVATIONS[name] = []
    RESERVATIONS[name].append(reservation_id)
    
    return {
        "success": True,
        "reservation_id": reservation_id,
        "message": f"Reserva confirmada para {name}, {party_size} personas, el {date} a las {time}. Su código de reserva es: {reservation_id}"
    }

def cancel_reservation_tool(reservation_id: str):
    """Cancela una reserva existente."""
    # Buscar la reserva por ID
    reservation_found = False
    reservation_key_to_remove = None
    
    for key, reservation in RESERVATIONS.items():
        if isinstance(reservation, dict) and reservation.get("id") == reservation_id:
            reservation_found = True
            reservation_key_to_remove = key
            name = reservation["name"]
            break
    
    if not reservation_found:
        return f"No encontramos ninguna reserva con el código {reservation_id}."
    
    # Eliminar la reserva
    del RESERVATIONS[reservation_key_to_remove]
    
    # Eliminar referencia en el índice de nombre
    if name in RESERVATIONS and isinstance(RESERVATIONS[name], list):
        if reservation_id in RESERVATIONS[name]:
            RESERVATIONS[name].remove(reservation_id)
        if not RESERVATIONS[name]:  # Si no quedan reservas para este nombre
            del RESERVATIONS[name]
    
    return {
        "success": True,
        "message": f"Reserva {reservation_id} cancelada correctamente."
    }

def find_reservation_by_name_tool(name: str):
    """Busca reservas existentes por nombre del cliente."""
    if name not in RESERVATIONS or not isinstance(RESERVATIONS[name], list):
        return f"No encontramos reservas a nombre de {name}."
    
    reservation_ids = RESERVATIONS[name]
    if not reservation_ids:
        return f"No encontramos reservas a nombre de {name}."
    
    reservations_info = []
    for res_id in reservation_ids:
        # Buscar los detalles de cada reserva
        for key, reservation in RESERVATIONS.items():
            if isinstance(reservation, dict) and reservation.get("id") == res_id:
                reservations_info.append({
                    "id": res_id,
                    "date": reservation["date"],
                    "time": reservation["time"],
                    "party_size": reservation["party_size"]
                })
                break
    
    return {
        "name": name,
        "reservations_count": len(reservations_info),
        "reservations": reservations_info
    }

def calculate_order_price_tool(items: List[str], party_size: int, time: str, date: str):
    """Calcula el precio final de un pedido con descuentos aplicables."""
    total_price = 0
    not_found = []
    found_items = []
    
    # Calcular precio base de todos los items
    for item in items:
        item_found = False
        for dish_id, details in MENU_ITEMS.items():
            if details["name"].lower() == item.lower() or dish_id.lower() == item.lower():
                total_price += details.get("price", 0)
                found_items.append({
                    "name": details["name"],
                    "price": details.get("price", 0)
                })
                item_found = True
                break
        
        if not item_found:
            not_found.append(item)
    
    # Aplicar descuentos
    discount_percent = 0
    discount_reason = ""
    
    # Ejemplo: descuento por hora no pico (antes de las 19:00)
    hour = int(time.split(":")[0])
    if hour < 19:
        discount_percent += 10
        discount_reason = "Horario anticipado (antes de las 19:00)"
    
    # Descuento para grupos grandes
    if party_size >= 6:
        discount_percent += 5
        discount_reason += ", Grupo grande" if discount_reason else "Grupo grande"
    
    # Cálculo del precio final
    discount_amount = total_price * (discount_percent / 100)
    final_price = total_price - discount_amount
    
    result = {
        "items": found_items,
        "subtotal": round(total_price, 2),
        "discount_percent": discount_percent,
        "discount_reason": discount_reason if discount_percent > 0 else "Sin descuentos aplicables",
        "discount_amount": round(discount_amount, 2),
        "total": round(final_price, 2)
    }
    
    if not_found:
        result["not_found"] = not_found
    
    return result

def generate_order_summary_tool(items: List[str]):
    """Genera un resumen detallado de un pedido con nombres y precios individuales."""
    found_items = []
    not_found = []
    total = 0
    
    for item in items:
        item_found = False
        for dish_id, details in MENU_ITEMS.items():
            if details["name"].lower() == item.lower() or dish_id.lower() == item.lower():
                price = details.get("price", 0)
                found_items.append({
                    "name": details["name"],
                    "price": price,
                    "category": details.get("category", "No especificada")
                })
                total += price
                item_found = True
                break
        
        if not item_found:
            not_found.append(item)
    
    result = {
        "items": found_items,
        "total": round(total, 2)
    }
    
    if not_found:
        result["not_found"] = not_found
    
    return result

def apply_specific_discount_tool(current_price: float, discount_percent: float):
    """Aplica un descuento específico (descuento promocional o cortesía)."""
    if discount_percent < 0 or discount_percent > 100:
        return "El porcentaje de descuento debe estar entre 0 y 100."
    
    final_price = current_price * (1 - discount_percent/100)
    discount_amount = current_price - final_price
    
    return {
        "original_price": round(current_price, 2),
        "discount_percent": discount_percent,
        "final_price": round(final_price, 2),
        "discount_amount": round(discount_amount, 2)
    }

def update_reservation_tool(reservation_id: str, new_date: Optional[str] = None, new_time: Optional[str] = None, 
                          new_party_size: Optional[int] = None, special_requests: Optional[str] = None):
    """Modifica una reserva existente."""
    # Buscar la reserva por ID
    reservation_found = False
    reservation_key = None
    old_reservation = None
    
    for key, reservation in RESERVATIONS.items():
        if isinstance(reservation, dict) and reservation.get("id") == reservation_id:
            reservation_found = True
            reservation_key = key
            old_reservation = reservation.copy()
            break
    
    if not reservation_found:
        return f"No encontramos ninguna reserva con el código {reservation_id}."
    
    # Verificar disponibilidad si cambia fecha, hora o tamaño de grupo
    if (new_date and new_date != old_reservation["date"]) or \
       (new_time and new_time != old_reservation["time"]) or \
       (new_party_size and new_party_size != old_reservation["party_size"]):
        
        date_to_check = new_date if new_date else old_reservation["date"]
        time_to_check = new_time if new_time else old_reservation["time"]
        party_size_to_check = new_party_size if new_party_size else old_reservation["party_size"]
        
        # Verificar disponibilidad
        availability = check_table_availability_tool(party_size_to_check, date_to_check, time_to_check)
        
        if not isinstance(availability, dict) or not availability.get("available", False):
            return f"No podemos modificar la reserva porque no hay disponibilidad para {party_size_to_check} personas en {date_to_check} a las {time_to_check}."
        
        # Si hay disponibilidad, eliminar la reserva anterior
        del RESERVATIONS[reservation_key]
        
        # Crear nueva reserva con los datos actualizados
        new_reservation = {
            "id": reservation_id,
            "name": old_reservation["name"],
            "party_size": party_size_to_check,
            "date": date_to_check,
            "time": time_to_check,
            "table": availability["tables"][0]["table_id"],
            "phone": old_reservation.get("phone"),
            "special_requests": special_requests if special_requests is not None else old_reservation.get("special_requests")
        }
        
        # Guardar la nueva reserva
        new_key = f"{date_to_check}_{time_to_check}_{new_reservation['table']}"
        RESERVATIONS[new_key] = new_reservation
        
    else:
        # Solo actualizamos peticiones especiales
        if special_requests is not None:
            RESERVATIONS[reservation_key]["special_requests"] = special_requests
    
    return {
        "success": True,
        "message": f"Reserva {reservation_id} modificada correctamente."
    }