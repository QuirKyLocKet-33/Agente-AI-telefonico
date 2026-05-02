"""
Servicio de comunicación eficiente con OpenAI para Agente Telefónico AI (restaurante)
Integrado con RAG para evitar alucinaciones
"""
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, SYSTEM_PROMPT
from pathlib import Path
import sys

# Intentar importar RAGRetriever
try:
    sys.path.insert(0, str(Path(__file__).parent / "backend"))
    from rag_retriever import RAGRetriever
    RAG_AVAILABLE = True
except Exception as e:
    print(f"⚠️  RAG no disponible: {e}")
    RAG_AVAILABLE = False

class ChatService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.historial = []
        
        # Inicializar RAG si está disponible
        self.rag_retriever = None
        if RAG_AVAILABLE:
            try:
                from rag_retriever import VECTOR_DB_PATH, COLLECTION_NAME, MODEL_PATH
                self.rag_retriever = RAGRetriever(
                    vector_db_path=VECTOR_DB_PATH,
                    collection_name=COLLECTION_NAME,
                    model_path=MODEL_PATH
                )
                print("✅ RAG Retriever inicializado correctamente")
            except Exception as e:
                print(f"⚠️  No se pudo inicializar RAG: {e}")
                self.rag_retriever = None

    def procesar_formato_reserva(self, texto):
        """Extrae datos de reserva del formato especial para restaurante"""
        if "RESERVACION_CONFIRMADA:" not in texto:
            return None
        try:
            inicio = texto.find("RESERVACION_CONFIRMADA:") + len("RESERVACION_CONFIRMADA:")
            fin = texto.find("\n", inicio) if "\n" in texto[inicio:] else len(texto)
            formato = texto[inicio:fin].strip()
            datos = {}
            partes = formato.split(';')
            for parte in partes:
                if '=' in parte:
                    clave, valor = parte.split('=', 1)
                    datos[clave.strip()] = valor.strip()
            # Se esperan al menos los campos principales
            return datos if "nombre" in datos and "telefono" in datos and "fecha" in datos else None
        except Exception:
            return None

    def obtener_contexto_rag(self, consulta: str) -> str:
        """Obtiene contexto relevante del RAG para la consulta"""
        if not self.rag_retriever:
            return ""
        
        try:
            resultados = self.rag_retriever.retrieve(consulta, top_k=5)
            if not resultados:
                return ""
            
            contexto = "\n\n📋 INFORMACIÓN RELEVANTE DEL RESTAURANT:\n"
            for i, resultado in enumerate(resultados, 1):
                contexto += f"\n{i}. {resultado['document'][:300]}\n"
            return contexto
        except Exception as e:
            print(f"Error retrieving RAG context: {e}")
            return ""

    def enviar_mensaje(self, mensaje):
        """Envía mensaje a OpenAI y obtiene respuesta adaptada a llamada telefónica"""
        mensaje = mensaje.strip()
        if not mensaje:
            return "Por favor, indique su consulta.", None

        # Obtener contexto del RAG
        contexto_rag = self.obtener_contexto_rag(mensaje)
        
        # Añadir mensaje del usuario al historial
        self.historial.append({"role": "user", "content": mensaje})
        
        # Construir mensajes para la API
        mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Si hay contexto RAG, incluirlo como asistente
        if contexto_rag:
            mensajes.append({"role": "assistant", "content": f"Tengo esta información relevante disponible:\n{contexto_rag}"})
        
        # Añadir historial (últimos 8 mensajes)
        mensajes.extend(self.historial[-8:])
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=mensajes,
                temperature=OPENAI_TEMPERATURE
            )
            respuesta = response.choices[0].message.content.strip()
        except Exception as e:
            return f"[SISTEMA] Error de comunicación con OpenAI: {str(e)}", None

        datos_reserva = self.procesar_formato_reserva(respuesta)
        self.historial.append({"role": "assistant", "content": respuesta})
        return respuesta, datos_reserva

    def limpiar_historial(self):
        """Limpia el historial de conversación telefónica"""
        self.historial = []