"""
Microservicio de persistencia de datos
"""
import json
import os
from datetime import datetime
from validation_service import ValidationService

class PersistenceService:
    CAMPOS_OBLIGATORIOS = [
        "nombre_completo",
        "correo_electronico", 
        "numero_telefonico",
        "codigo_postal",
        "fecha_reserva",
        "hora_reserva",
        "numero_personas"
    ]
    
    def __init__(self, archivo_json="cliente_reservas.json"):
        self.archivo_json = archivo_json
    
    def validar_datos_reserva(self, datos):
        """Valida todos los campos de la reserva"""
        errores = []
        
        for campo in self.CAMPOS_OBLIGATORIOS:
            if campo not in datos or not str(datos[campo]).strip():
                errores.append(f"Campo obligatorio faltante: {campo}")
                continue
            
            valor = str(datos[campo]).strip()
            
            validaciones = {
                "correo_electronico": (ValidationService.validar_email, "Formato de email inválido"),
                "numero_telefonico": (ValidationService.validar_telefono, "Número telefónico inválido (mínimo 10 dígitos)"),
                "codigo_postal": (ValidationService.validar_codigo_postal, "Código postal inválido (mínimo 5 dígitos)"),
                "fecha_reserva": (ValidationService.validar_fecha, "Fecha inválida o pasada. Use formato YYYY-MM-DD"),
                "hora_reserva": (ValidationService.validar_hora, "Hora inválida. Use formato HH:MM"),
                "numero_personas": (ValidationService.validar_numero_personas, "Número de personas inválido (1-20)")
            }
            
            if campo in validaciones:
                funcion_validacion, mensaje_error = validaciones[campo]
                if not funcion_validacion(valor):
                    errores.append(mensaje_error)
        
        return errores
    
    def guardar_reserva(self, datos_reserva):
        """Guarda la reserva en el archivo JSON"""
        try:
            # Validar datos antes de guardar
            errores = self.validar_datos_reserva(datos_reserva)
            if errores:
                return False, errores
            
            # Añadir metadatos
            datos_reserva["id_reserva"] = f"RES{datetime.now().strftime('%Y%m%d%H%M%S')}"
            datos_reserva["fecha_creacion"] = datetime.now().isoformat()
            
            # Cargar reservas existentes
            reservas = self._cargar_reservas()
            
            # Añadir nueva reserva
            reservas.append(datos_reserva)
            
            # Guardar en archivo
            self._guardar_json(reservas)
            
            return True, datos_reserva["id_reserva"]
        
        except Exception as e:
            return False, [f"Error al guardar: {str(e)}"]
    
    def _cargar_reservas(self):
        """Carga las reservas existentes del archivo JSON"""
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, 'r', encoding='utf-8') as f:
                    reservas = json.load(f)
                    return reservas if isinstance(reservas, list) else []
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _guardar_json(self, datos):
        """Guarda datos en archivo JSON"""
        with open(self.archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    
    def obtener_reservas(self):
        """Obtiene todas las reservas guardadas"""
        return self._cargar_reservas()