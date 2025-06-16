# restaurant_data.py - Base de datos simulada del restaurante

# Datos de mesas
TABLES = {
    1: {"capacity": 2, "location": "ventana", "available": True},
    2: {"capacity": 4, "location": "interior", "available": True},
    3: {"capacity": 6, "location": "terraza", "available": True},
    4: {"capacity": 8, "location": "salon_privado", "available": True},
    5: {"capacity": 12, "location": "salon_principal", "available": True},
    # ... más mesas
}

# Menú con restricciones dietéticas
MENU_ITEMS = {
    "ensalada_mediterranea": {
        "name": "Ensalada Mediterránea",
        "price": 12.50,
        "category": "entrante",
        "dietary": ["vegetarian", "vegan", "gluten_free"],
        "ingredients": ["lechuga", "tomate", "aceitunas", "aceite"],
        "prep_time": 10,
        "available": True
    },
    "paella_valenciana": {
        "name": "Paella Valenciana",
        "price": 18.00,
        "category": "principal",
        "dietary": ["gluten_free"],
        "ingredients": ["arroz", "pollo", "conejo", "verduras"],
        "prep_time": 45,
        "available": True
    },
    "pasta_carbonara": {
        "name": "Pasta Carbonara",
        "price": 14.00,
        "category": "principal", 
        "dietary": ["vegetarian"],
        "ingredients": ["pasta", "huevos", "queso", "panceta"],
        "prep_time": 20,
        "available": True
    },
    "tarta_chocolate": {
        "name": "Tarta de Chocolate",
        "price": 6.50,
        "category": "postre",
        "dietary": ["vegetarian"],
        "ingredients": ["chocolate", "harina", "huevos", "mantequilla"],
        "prep_time": 5,
        "available": True
    }
    # ... más platos
}

# Reservas existentes
RESERVATIONS = {
    "2025-06-16": {
        "12:00": {"table": 1, "party_size": 2, "name": "García"},
        "13:30": {"table": 3, "party_size": 4, "name": "López"},
        "20:00": {"table": 5, "party_size": 8, "name": "Martínez"}
    },
    "2025-06-17": {
        "19:30": {"table": 2, "party_size": 4, "name": "Rodríguez"}
    }
}

# Precios y descuentos
PRICING_RULES = {
    "group_discount": {
        "min_people": 8,
        "discount_percent": 10
    },
    "early_bird": {
        "before_time": "19:00",
        "discount_percent": 5
    },
    "weekend_surcharge": {
        "days": ["saturday", "sunday"],
        "surcharge_percent": 15
    }
}

# Tiempos de cocina por categoría
KITCHEN_TIMES = {
    "entrante": {"base": 10, "max_parallel": 6},
    "principal": {"base": 25, "max_parallel": 4}, 
    "postre": {"base": 8, "max_parallel": 8}
}

# Tools para cada agente
class RestaurantTools:
    
    @staticmethod
    def get_available_tables(date: str, time: str, party_size: int):
        """Encuentra mesas disponibles para fecha, hora y número de personas"""
        available_tables = []
        
        # Verificar reservas existentes
        day_reservations = RESERVATIONS.get(date, {})
        reserved_tables = [res["table"] for res in day_reservations.values()]
        
        # Buscar mesas con capacidad suficiente y disponibles
        for table_id, table_info in TABLES.items():
            if (table_info["capacity"] >= party_size and 
                table_id not in reserved_tables):
                available_tables.append({
                    "table_id": table_id,
                    "capacity": table_info["capacity"],
                    "location": table_info["location"]
                })
        
        return {
            "date": date,
            "time": time,
            "party_size": party_size,
            "available_tables": available_tables,
            "total_available": len(available_tables)
        }
    
    @staticmethod
    def filter_menu_by_dietary(restrictions: list = None):
        """Filtra menú por restricciones dietéticas"""
        if not restrictions:
            return MENU_ITEMS
            
        filtered_menu = {}
        for item_id, item_info in MENU_ITEMS.items():
            # Verificar si el plato cumple TODAS las restricciones
            if all(restriction in item_info["dietary"] for restriction in restrictions):
                filtered_menu[item_id] = item_info
                
        return filtered_menu
    
    @staticmethod
    def calculate_order_price(items: list, party_size: int, time: str, date: str):
        """Calcula precio total con descuentos"""
        base_price = 0
        
        # Calcular precio base
        for item_id in items:
            if item_id in MENU_ITEMS:
                base_price += MENU_ITEMS[item_id]["price"]
        
        total_price = base_price
        applied_discounts = []
        
        # Aplicar descuento de grupo
        if party_size >= PRICING_RULES["group_discount"]["min_people"]:
            discount = PRICING_RULES["group_discount"]["discount_percent"]
            total_price *= (1 - discount/100)
            applied_discounts.append(f"Descuento grupo: {discount}%")
        
        # Aplicar descuento early bird
        if time < PRICING_RULES["early_bird"]["before_time"]:
            discount = PRICING_RULES["early_bird"]["discount_percent"] 
            total_price *= (1 - discount/100)
            applied_discounts.append(f"Descuento early bird: {discount}%")
        
        # Aplicar recargo de fin de semana (simplificado)
        import datetime
        day_name = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A").lower()
        if day_name in PRICING_RULES["weekend_surcharge"]["days"]:
            surcharge = PRICING_RULES["weekend_surcharge"]["surcharge_percent"]
            total_price *= (1 + surcharge/100)
            applied_discounts.append(f"Recargo fin de semana: {surcharge}%")
        
        return {
            "base_price": round(base_price, 2),
            "final_price": round(total_price, 2),
            "applied_discounts": applied_discounts,
            "savings": round(base_price - total_price, 2) if base_price > total_price else 0
        }
    
    @staticmethod
    def estimate_preparation_time(items: list):
        """Estima tiempo total de preparación"""
        category_items = {"entrante": [], "principal": [], "postre": []}
        
        # Agrupar por categoría
        for item_id in items:
            if item_id in MENU_ITEMS:
                category = MENU_ITEMS[item_id]["category"]
                prep_time = MENU_ITEMS[item_id]["prep_time"]
                category_items[category].append(prep_time)
        
        # Calcular tiempo por categoría (considerando paralelización)
        total_time = 0
        for category, times in category_items.items():
            if times:
                max_parallel = KITCHEN_TIMES[category]["max_parallel"]
                # Tiempo = max(tiempos) si hay paralelización
                category_time = max(times) if len(times) <= max_parallel else sum(times)
                total_time += category_time
        
        return {
            "total_time_minutes": total_time,
            "category_breakdown": category_items,
            "estimated_ready": f"{total_time} minutos"
        }

# Función helper para crear reserva
def create_reservation(date: str, time: str, table_id: int, party_size: int, name: str):
    """Crea una nueva reserva"""
    if date not in RESERVATIONS:
        RESERVATIONS[date] = {}
    
    RESERVATIONS[date][time] = {
        "table": table_id,
        "party_size": party_size, 
        "name": name
    }
    
    return {
        "success": True,
        "reservation": {
            "date": date,
            "time": time,
            "table": table_id,
            "party_size": party_size,
            "name": name
        }
    }