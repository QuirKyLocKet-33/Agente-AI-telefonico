"""
Funciones utilitarias
"""
import sys

def mostrar_banner():
    """Muestra el banner de bienvenida para agente telefónico AI"""
    print("=" * 50)
    print("RESTAURANTE CASA LAGUNA - Agente Telefónico AI")
    print("=" * 50)
    print("\nGracias por llamar a CASA LAGUNA, le habla Sofía. ¿En qué le puedo ayudar el día de hoy?\n")
    print("Puedo ayudarle con:")
    print("• Información general del restaurante")
    print("• Realizar una reservación (le guiaré paso a paso)")
    print("• Consultas sobre servicios o eventos")
    print("\nDiga 'salir' o presione Ctrl+C para finalizar la llamada.\n")

def mostrar_error(error, contexto=""):
    """Muestra mensajes de error formateados para agente telefónico"""
    print(f"\n{'='*30}")
    print(f"[SISTEMA] Ha ocurrido un error: {error}")
    if contexto:
        print(f"[Contexto]: {contexto}")
    print(f"{'='*30}\n")

def confirmar_salida():
    """Confirma si el usuario desea finalizar la llamada"""
    respuesta = input("\n¿Desea finalizar la llamada? (s/n): ").strip().lower()
    return respuesta in ['s', 'si', 'sí', 'yes', 'y']