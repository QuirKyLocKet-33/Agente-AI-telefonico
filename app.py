"""
Servidor web para el Agente Telefónico AI de CASA LAGUNA
"""
from flask import Flask, render_template, request, jsonify
from chat_service import ChatService
from persistence_service import PersistenceService
from config import RESERVAS_JSON_FILE, OPENAI_API_KEY
from openai import OpenAI
import io
import base64
import concurrent.futures

app = Flask(__name__)
chat_service = ChatService()
persistence_service = PersistenceService(RESERVAS_JSON_FILE)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def index():
    """Página principal del agente telefónico web"""
    return render_template('index.html')

@app.route('/greeting', methods=['GET'])
def greeting():
    """Devuelve el saludo inicial de Sofía al contestar la llamada"""
    try:
        texto = "Gracias por llamar a CASA LAGUNA, le habla Sofía. ¿En qué le puedo ayudar el día de hoy?"
        tts = openai_client.audio.speech.create(
            model='tts-1', voice='alloy', input=texto, response_format='opus'
        )
        audio_base64 = base64.b64encode(tts.content).decode('utf-8')
        return jsonify({'audio': audio_base64, 'texto': texto, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/voice', methods=['POST'])
def voice():
    """
    Endpoint unificado: recibe audio, transcribe + chat + TTS en paralelo.
    Reduce 3 round trips a 1, usando webm y opus para menor tamaño.
    """
    try:
        data = request.get_json()
        audio_base64 = data.get('audio', '')
        mime_type = data.get('mime', 'audio/webm')  # webm por defecto

        if not audio_base64:
            return jsonify({'error': 'No se proporcionó audio'}), 400

        audio_data = base64.b64decode(audio_base64)

        # Determinar extensión según mime type
        ext_map = {
            'audio/webm': 'webm',
            'audio/ogg': 'ogg',
            'audio/wav': 'wav',
            'audio/mp4': 'mp4',
        }
        ext = ext_map.get(mime_type.split(';')[0].strip(), 'webm')

        audio_file = io.BytesIO(audio_data)
        audio_file.name = f'audio.{ext}'

        # 1. Transcribir con Whisper
        transcript = openai_client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            language='es'
        )
        texto_usuario = transcript.text.strip()
        if not texto_usuario:
            return jsonify({'error': 'No se detectó voz clara'}), 400

        # 2. Obtener respuesta del agente
        respuesta, datos_reserva = chat_service.enviar_mensaje(texto_usuario)

        # 3. Procesar reserva si aplica
        if datos_reserva:
            exito, mensaje_reserva = persistence_service.guardar_reserva(datos_reserva)
            if exito:
                respuesta += f"\n\n[✅ RESERVACIÓN CONFIRMADA - ID: {mensaje_reserva}]\n"
                respuesta += "Sus datos han sido guardados exitosamente.\n"
                respuesta += "Recibirá un correo de confirmación pronto."
                chat_service.limpiar_historial()
            else:
                respuesta += f"\n\n[❌ ERROR EN RESERVACIÓN]\n"
                for error in mensaje_reserva:
                    respuesta += f"• {error}\n"
                respuesta += "\nPor favor, proporcione la información corregida."

        # 4. Generar TTS con opus (más rápido y compacto que mp3)
        tts_response = openai_client.audio.speech.create(
            model='tts-1',
            voice='alloy',
            input=respuesta,
            response_format='opus'
        )
        audio_respuesta = base64.b64encode(tts_response.content).decode('utf-8')

        return jsonify({
            'transcripcion': texto_usuario,
            'respuesta': respuesta,
            'audio': audio_respuesta,
            'reserva': datos_reserva,
            'success': True
        })

    except Exception as e:
        print(f'Error en /voice: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Endpoint legado de transcripción (mantener compatibilidad)"""
    try:
        data = request.get_json()
        audio_base64 = data.get('audio', '')
        if not audio_base64:
            return jsonify({'error': 'No se proporcionó audio'}), 400
        audio_data = base64.b64decode(audio_base64)
        audio_file = io.BytesIO(audio_data)
        audio_file.name = 'audio.webm'
        transcript = openai_client.audio.transcriptions.create(
            model='whisper-1', file=audio_file, language='es'
        )
        return jsonify({'texto': transcript.text, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/synthesize', methods=['POST'])
def synthesize():
    """Endpoint legado de síntesis (mantener compatibilidad)"""
    try:
        data = request.get_json()
        texto = data.get('texto', '').strip()
        if not texto:
            return jsonify({'error': 'No se proporcionó texto'}), 400
        response = openai_client.audio.speech.create(
            model='tts-1', voice='alloy', input=texto, response_format='opus'
        )
        audio_base64 = base64.b64encode(response.content).decode('utf-8')
        return jsonify({'audio': audio_base64, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint para procesar mensajes del chat"""
    data = request.get_json()
    mensaje = data.get('mensaje', '').strip()

    if not mensaje:
        return jsonify({'respuesta': 'Por favor, indique su consulta.', 'reserva': None})

    # Procesar mensaje con el servicio de chat
    respuesta, datos_reserva = chat_service.enviar_mensaje(mensaje)

    # Si hay datos de reserva, procesarlos
    if datos_reserva:
        exito, mensaje_reserva = persistence_service.guardar_reserva(datos_reserva)
        if exito:
            respuesta += f"\n\n[✅ RESERVACIÓN CONFIRMADA - ID: {mensaje_reserva}]\n"
            respuesta += "Sus datos han sido guardados exitosamente.\n"
            respuesta += "Recibirá un correo de confirmación pronto."
            chat_service.limpiar_historial()  # Reiniciar conversación
        else:
            respuesta += f"\n\n[❌ ERROR EN RESERVACIÓN]\n"
            respuesta += "Hubo problemas con los datos proporcionados:\n"
            for error in mensaje_reserva:
                respuesta += f"• {error}\n"
            respuesta += "\nPor favor, proporcione la información corregida."

    return jsonify({'respuesta': respuesta, 'reserva': datos_reserva})

@app.route('/reservas', methods=['GET'])
def obtener_reservas():
    """Endpoint para obtener todas las reservas (para administración)"""
    reservas = persistence_service.obtener_reservas()
    return jsonify(reservas)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)