import os
import json
from datetime import datetime
from openai import OpenAI
import re
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# =======================
# CONFIGURACIÓN CLIENTE
# =======================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY no está configurada. Por favor, crea un archivo .env con tu clave API.")

client = OpenAI(api_key=OPENAI_API_KEY)

# =======================
# MICROSERVICIO DE PERSISTENCIA
# =======================
class ReservaMicroservicio:
    ARCHIVO_JSON = "cliente_reservas.json"
    
    # Campos obligatorios para la reserva
    CAMPOS_OBLIGATORIOS = [
        "nombre_completo",
        "correo_electronico", 
        "numero_telefonico",
        "codigo_postal",
        "fecha_reserva",
        "hora_reserva",
        "numero_personas"
    ]
    
    @staticmethod
    def validar_email(email):
        """Valida formato básico de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validar_telefono(telefono):
        """Valida que el teléfono contenga solo números y tenga longitud mínima"""
        telefono_limpio = ''.join(filter(str.isdigit, telefono))
        return len(telefono_limpio) >= 10
    
    @staticmethod
    def validar_codigo_postal(codigo_postal):
        """Valida código postal (5 dígitos para mayoría de países)"""
        codigo_limpio = ''.join(filter(str.isdigit, codigo_postal))
        return len(codigo_limpio) >= 5
    
    @staticmethod
    def validar_fecha(fecha_str):
        """Valida formato de fecha YYYY-MM-DD"""
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            # Verificar que no sea fecha pasada
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            return fecha_obj >= datetime.now().date()
        except ValueError:
            return False
    
    @staticmethod
    def validar_hora(hora_str):
        """Valida formato de hora HH:MM"""
        try:
            datetime.strptime(hora_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_numero_personas(numero):
        """Valida que sea número positivo"""
        try:
            num = int(numero)
            return 1 <= num <= 20  # Límite razonable
        except ValueError:
            return False
    
    @staticmethod
    def validar_datos_reserva(datos):
        """Valida todos los campos de la reserva"""
        errores = []
        
        # Verificar campos obligatorios
        for campo in ReservaMicroservicio.CAMPOS_OBLIGATORIOS:
            if campo not in datos or not str(datos[campo]).strip():
                errores.append(f"Campo obligatorio faltante: {campo}")
                continue
            
            valor = str(datos[campo]).strip()
            
            # Validaciones específicas por campo
            if campo == "correo_electronico":
                if not ReservaMicroservicio.validar_email(valor):
                    errores.append("Formato de email inválido")
            
            elif campo == "numero_telefonico":
                if not ReservaMicroservicio.validar_telefono(valor):
                    errores.append("Número telefónico inválido (mínimo 10 dígitos)")
            
            elif campo == "codigo_postal":
                if not ReservaMicroservicio.validar_codigo_postal(valor):
                    errores.append("Código postal inválido (mínimo 5 dígitos)")
            
            elif campo == "fecha_reserva":
                if not ReservaMicroservicio.validar_fecha(valor):
                    errores.append("Fecha inválida o pasada. Use formato YYYY-MM-DD")
            
            elif campo == "hora_reserva":
                if not ReservaMicroservicio.validar_hora(valor):
                    errores.append("Hora inválida. Use formato HH:MM")
            
            elif campo == "numero_personas":
                if not ReservaMicroservicio.validar_numero_personas(valor):
                    errores.append("Número de personas inválido (1-20)")
        
        return errores
    
    @staticmethod
    def guardar_reserva(datos_reserva):
        """Guarda la reserva en el archivo JSON"""
        try:
            # Validar datos antes de guardar
            errores = ReservaMicroservicio.validar_datos_reserva(datos_reserva)
            if errores:
                return False, errores
            
            # Añadir timestamp y ID único
            datos_reserva["id_reserva"] = f"RES{datetime.now().strftime('%Y%m%d%H%M%S')}"
            datos_reserva["fecha_creacion"] = datetime.now().isoformat()
            
            # Cargar reservas existentes o crear lista vacía
            if os.path.exists(ReservaMicroservicio.ARCHIVO_JSON):
                with open(ReservaMicroservicio.ARCHIVO_JSON, 'r', encoding='utf-8') as f:
                    try:
                        reservas = json.load(f)
                        if not isinstance(reservas, list):
                            reservas = []
                    except json.JSONDecodeError:
                        reservas = []
            else:
                reservas = []
            
            # Añadir nueva reserva
            reservas.append(datos_reserva)
            
            # Guardar en archivo
            with open(ReservaMicroservicio.ARCHIVO_JSON, 'w', encoding='utf-8') as f:
                json.dump(reservas, f, indent=2, ensure_ascii=False)
            
            return True, datos_reserva["id_reserva"]
        
        except Exception as e:
            return False, [f"Error al guardar: {str(e)}"]

# =======================
# PROMPT DE SISTEMA MEJORADO
# =======================
SYSTEM_PROMPT = """
Eres Sofía, una agente de voz con IA del Restaurante [CASA LAGUNA].
Atiendes llamadas entrantes de forma profesional, cálida y eficiente.

═══════════════════════════════════════════
IDENTIDAD Y COMPORTAMIENTO DE VOZ
═══════════════════════════════════════════
- Tu nombre es Sofía. Eres la recepcionista virtual del Restaurante [CASA LAGUNA].
- Estás atendiendo una LLAMADA TELEFÓNICA, no un chat. Actúa en consecuencia:
  • Oraciones cortas y claras (máximo 2-3 oraciones por turno).
  • Nunca uses viñetas, markdown, emojis ni listas — solo lenguaje hablado natural.
  • Deletrea números y fechas: "quince de marzo" no "15/03", "cuatro personas" no "4".
  • Evita frases robóticas como "¡Por supuesto!", "¡Claro que sí!", "¡Absolutamente!" en exceso.
- Tono: cálido, tranquilo, profesional — como la recepcionista de un restaurante de alto nivel.
- Si el cliente habla en inglés, responde en inglés automáticamente.

═══════════════════════════════════════════
APERTURA DE LLAMADA
═══════════════════════════════════════════
Siempre abre la llamada con:
"Gracias por llamar a [CASA LAGUNA], le habla Sofía. ¿En qué le puedo ayudar el día de hoy?"

═══════════════════════════════════════════
INFORMACIÓN GENERAL — Responde directamente
═══════════════════════════════════════════
Daras informacion general sobre el restaurante de forma concisa y amable. Ejemplos: Horarios, ubicación, tipo de cocina, servicios generales (wifi, estacionamiento, accesibilidad), políticas de mascotas, etc.

═══════════════════════════════════════════
FLUJO DE RESERVACIÓN — Recolecta esta información
═══════════════════════════════════════════
Cuando el cliente quiera hacer una reservación, guíalo de forma natural y conversacional
recolectando estos datos en orden lógico. No hagas todas las preguntas a la vez.

DATOS A RECOLECTAR:
1. Nombre completo del titular
2. Número de teléfono de contacto
3. Correo electrónico (opcional, para confirmación)
4. Fecha de la reservación
5. Hora deseada
6. Número de personas
7. Ocasión especial (cumpleaños, aniversario, etc.) — preguntar siempre
8. Alguna solicitud especial (alergias, silla de bebé, zona preferida, etc.)

REGLAS DEL FLUJO:
- Haz una pregunta a la vez, espera la respuesta antes de continuar.
- Si la hora solicitada no está disponible, ofrece la opción más cercana disponible.
- Si la fecha cae en día de cierre (martes), informa amablemente y sugiere otra fecha.
- Valida el número de personas contra la disponibilidad antes de confirmar.
- Si el grupo es mayor a 12 personas, indica que se requiere coordinación especial
  y ofrece transferir la llamada o tomar un mensaje para el coordinador de eventos.

CONFIRMACIÓN FINAL:
Antes de cerrar la reservación, confirma todos los datos en voz alta:
"Permítame confirmar su reservación: a nombre de [nombre], el [fecha] a las [hora],
para [número] personas. ¿Es correcto?"

FORMATO DE SALIDA — Cuando todos los datos estén confirmados:
RESERVACION_CONFIRMADA:nombre=[...];telefono=[...];correo=[...];fecha=YYYY-MM-DD;hora=HH:MM;personas=[...];ocasion=[...];solicitudes_especiales=[...]

═══════════════════════════════════════════
MANEJO DE SITUACIONES ESPECIALES
═══════════════════════════════════════════
- CLIENTE MOLESTO: Mantén la calma, valida su molestia, ofrece solución o escala.
  Nunca respondas con defensividad. Frase útil: "Entiendo perfectamente su situación,
  permítame ayudarle a resolverlo."

- SILENCIO LARGO: Si no hay respuesta en 5 segundos, di: "¿Me escucha? ¿Siguen en línea?"

- NO ENTENDISTE: "Disculpe, ¿podría repetirme eso? Quiero asegurarme de entenderle bien."

- SOLICITUD FUERA DE ALCANCE: "Eso está fuera de lo que puedo gestionar por este medio,
  pero con gusto le comunico con alguien de nuestro equipo que podrá ayudarle mejor."

- TRANSFERENCIA DE LLAMADA: "Voy a transferirle con [gerente/coordinador/cocina].
  Un momento, por favor."

- CIERRE DE LLAMADA: Siempre despide con calidez:
  "Fue un placer atenderle. Le esperamos en [NOMBRE_RESTAURANTE]. ¡Que tenga un excelente día!"

═══════════════════════════════════════════
RESTRICCIONES ABSOLUTAS
═══════════════════════════════════════════
- Nunca inventes disponibilidad, precios o información que no tengas.
- Nunca confirmes un pago o cobro por teléfono.
- Nunca compartas información personal de otros clientes.
- Nunca prometas algo que no puedas garantizar.
- Si no sabes algo, di: "No cuento con esa información en este momento,
  pero puedo tomar nota para que nuestro equipo le contacte."
"""

# =======================
# FUNCIÓN PARA PROCESAR RESPUESTAS
# =======================
def procesar_formato_reserva(texto):
    """Extrae datos de reserva del formato especial"""
    if "FORMATO_RESERVA:" not in texto:
        return None
    
    try:
        # Extraer la parte del formato
        inicio = texto.find("FORMATO_RESERVA:") + len("FORMATO_RESERVA:")
        fin = texto.find("\n", inicio) if "\n" in texto[inicio:] else len(texto)
        formato = texto[inicio:fin].strip()
        
        # Parsear datos
        datos = {}
        partes = formato.split(';')
        
        for parte in partes:
            if '=' in parte:
                clave, valor = parte.split('=', 1)
                datos[clave.strip()] = valor.strip()
        
        return datos if len(datos) == 7 else None
    
    except Exception:
        return None

# =======================
# FUNCIÓN PRINCIPAL MEJORADA
# =======================
def responder(mensaje, historial, datos_reserva_parciales):
    mensaje = mensaje.strip()
    if not mensaje:
        return "Por favor, escriba su consulta.", historial, datos_reserva_parciales
    
    # Agregar mensaje del usuario al historial
    historial.append({"role": "user", "content": mensaje})
    
    # Llamada a la API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + historial[-8:],
        temperature=0.3
    )
    
    salida = response.choices[0].message.content.strip()
    
    # Verificar si la respuesta contiene datos de reserva completos
    datos_reserva = procesar_formato_reserva(salida)
    
    if datos_reserva:
        # Intentar guardar la reserva
        exito, resultado = ReservaMicroservicio.guardar_reserva(datos_reserva)
        
        if exito:
            salida += f"\n\n[✅ RESERVA CONFIRMADA - ID: {resultado}]\n"
            salida += "Sus datos han sido guardados exitosamente. "
            salida += "Recibirá un correo de confirmación pronto."
            # Reiniciar datos parciales
            datos_reserva_parciales = {}
        else:
            salida += f"\n\n[❌ ERROR EN RESERVA]\n"
            salida += "Hubo problemas con los datos proporcionados:\n"
            for error in resultado:
                salida += f"• {error}\n"
            salida += "\nPor favor, proporcione la información corregida."
    
    # Agregar respuesta al historial
    historial.append({"role": "assistant", "content": salida})
    
    return salida, historial, datos_reserva_parciales

# =======================
# SCRIPT PRINCIPAL MEJORADO
# =======================
def main():
    # INICIALIZAR VARIABLES AQUÍ - FUERA DEL LOOP
    historial = []
    datos_reserva_parciales = {}
    
    print("=" * 50)
    print("HOTEL MAR - Asistente Virtual de Reservas")
    print("=" * 50)
    print("\nPuedo ayudarte con:")
    print("• Información general del hotel")
    print("• Hacer una reserva (te guiaré paso a paso)")
    print("• Consultas sobre servicios")
    print("\nEscriba 'exit' para finalizar.\n")
    
    while True:
        try:
            mensaje = input("Cliente: ").strip()
            
            if mensaje.lower() in {"exit", "quit", "salir"}:
                print("\nBot: Gracias por su visita. Le deseamos una estancia maravillosa.")
                break
            
            respuesta, historial, datos_reserva_parciales = responder(
                mensaje, historial, datos_reserva_parciales
            )
            
            print("\nBot:", respuesta)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\nBot: Sesión interrumpida. Hasta pronto.")
            break
        except Exception as e:
            print(f"\nBot: Lo siento, ha ocurrido un error: {str(e)}")
            print("Por favor, intente nuevamente.")

# =======================
# INICIALIZACIÓN
# =======================
if __name__ == "__main__":
    # Verificar que el modelo esté disponible
    try:
        main()
    except Exception as e:
        print(f"Error al iniciar: {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Verifica tu API key de OpenAI")
        print("2. Asegúrate de que el modelo 'gpt-4o-mini' esté disponible")
        print("3. Verifica tu conexión a internet")