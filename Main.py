"""
Punto de entrada principal de la aplicación
"""
from chat_service import ChatService
from persistence_service import PersistenceService
from utils import mostrar_banner, mostrar_error, confirmar_salida
from config import RESERVAS_JSON_FILE

class HotelBotApp:
    def __init__(self):
        self.chat_service = ChatService()
        self.persistence_service = PersistenceService(RESERVAS_JSON_FILE)
        self.en_ejecucion = True
    
    def procesar_reserva(self, datos_reserva):
        """Procesa y guarda una reserva"""
        if not datos_reserva:
            return False, "No se encontraron datos de reserva"
        
        exito, resultado = self.persistence_service.guardar_reserva(datos_reserva)
        
        if exito:
            mensaje = f"[✅ RESERVA CONFIRMADA - ID: {resultado}]\n"
            mensaje += "Sus datos han sido guardados exitosamente.\n"
            mensaje += "Recibirá un correo de confirmación pronto."
            return True, mensaje
        else:
            mensaje = "[❌ ERROR EN RESERVA]\n"
            mensaje += "Hubo problemas con los datos proporcionados:\n"
            for error in resultado:
                mensaje += f"• {error}\n"
            mensaje += "\nPor favor, proporcione la información corregida."
            return False, mensaje
    
    def ejecutar(self):
        """Método principal de ejecución"""
        mostrar_banner()
        
        while self.en_ejecucion:
            try:
                mensaje = input("Cliente: ").strip()
                
                # Comandos de salida
                if mensaje.lower() in {"exit", "quit", "salir"}:
                    if confirmar_salida():
                        print("\nBot: Gracias por su visita. Le deseamos una estancia maravillosa.")
                        break
                    continue
                
                # Procesar mensaje
                respuesta, datos_reserva = self.chat_service.enviar_mensaje(mensaje)
                
                # Si hay datos de reserva, procesarlos
                if datos_reserva:
                    exito, mensaje_reserva = self.procesar_reserva(datos_reserva)
                    if exito:
                        respuesta += f"\n\n{mensaje_reserva}"
                        self.chat_service.limpiar_historial()  # Reiniciar para nueva conversación
                    else:
                        respuesta += f"\n\n{mensaje_reserva}"
                
                print("\nBot:", respuesta)
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\nBot: Sesión interrumpida. Hasta pronto.")
                break
            except Exception as e:
                mostrar_error(f"Error en la aplicación: {str(e)}", "main.ejecutar")

def main():
    """Función principal"""
    try:
        app = HotelBotApp()
        app.ejecutar()
    except Exception as e:
        mostrar_error(f"Error al iniciar la aplicación: {str(e)}", "main")
        print("\nPosibles soluciones:")
        print("1. Verifica tu API key de OpenAI")
        print("2. Asegúrate de que el modelo esté disponible")
        print("3. Verifica tu conexión a internet")

if __name__ == "__main__":
    main()