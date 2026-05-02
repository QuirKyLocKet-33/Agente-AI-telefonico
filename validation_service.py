"""
Servicio de validación de datos de reserva para agente telefónico AI (restaurante)
"""
import re
from datetime import datetime

class ValidationService:
    @staticmethod
    def validar_email(email):
        """Valida formato básico de email (opcional en llamada)"""
        if not email:
            return True  # Email es opcional
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validar_telefono(telefono):
        """Valida que el teléfono contenga solo números y tenga longitud mínima"""
        telefono_limpio = ''.join(filter(str.isdigit, telefono))
        return len(telefono_limpio) >= 10

    @staticmethod
    def validar_fecha(fecha_str):
        """Valida formato de fecha YYYY-MM-DD y que no sea martes (día de cierre) ni pasada"""
        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha_obj < datetime.now().date():
                return False
            # Día de cierre: martes (1=lunes, 2=martes...)
            if fecha_obj.weekday() == 1:
                return False
            return True
        except ValueError:
            return False

    @staticmethod
    def validar_hora(hora_str):
        """Valida formato de hora HH:MM y rango típico restaurante (12:00-23:00)"""
        try:
            hora = datetime.strptime(hora_str, "%H:%M").time()
            return (hora >= datetime.strptime("12:00", "%H:%M").time() and
                    hora <= datetime.strptime("23:00", "%H:%M").time())
        except ValueError:
            return False

    @staticmethod
    def validar_numero_personas(numero):
        """Valida que sea número positivo y máximo 20 (más de 12 requiere coordinación especial)"""
        try:
            num = int(numero)
            return 1 <= num <= 20
        except ValueError:
            return False

    @staticmethod
    def validar_ocasion(ocasion):
        """Valida que la ocasión especial sea texto o vacío"""
        return isinstance(ocasion, str)

    @staticmethod
    def validar_solicitudes_especiales(solicitudes):
        """Valida que las solicitudes especiales sean texto o vacío"""
        return isinstance(solicitudes, str)