# 🎤 Agente Telefónico con Voz - Instrucciones

## ¿Qué se cambió?

Tu agente telefónico ahora está completamente integrado con la **API de OpenAI** para:
- **Speech-to-Text (Whisper)**: Convierte tu voz en texto con precision
- **Text-to-Speech (TTS)**: Convierte las respuestas a voz natural
- **GPT-4 Mini**: Procesa y responde tus consultas

## Cómo funciona el flujo

```
1. Haces clic en 🎤 MICRÓFONO
   ↓
2. Hablas (el bot graba tu voz)
   ↓
3. Haces clic nuevamente para detener
   ↓
4. OpenAI Whisper transcribe tu voz → texto
   ↓
5. GPT-4 Mini procesa tu mensaje y genera respuesta
   ↓
6. OpenAI TTS convierte respuesta → audio MP3
   ↓
7. Se reproduce el audio automáticamente 🔊
```

## Requisitos previos

### 1. API Key de OpenAI
Asegúrate de tener una clave API válida de OpenAI. Está configurada en `config.py`:
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")
```

**Opción 1**: Variable de entorno
```bash
export OPENAI_API_KEY="sk-proj-..."
```

**Opción 2**: Editar directamente en `config.py` (menos seguro)

### 2. Dependencias instaladas
```bash
cd /home/qurikylocket331/chatBot/tareabot
source BOT/bin/activate  # Activar el entorno virtual
pip install -r requirements.txt
```

### 3. Permisos de micrófono
- Si usas chrome/Edge: Se te pedirá permiso la primera vez
- Debes permitir acceso al micrófono en las configuraciones del navegador

## Cómo ejecutar

```bash
# Activar el entorno virtual
source BOT/bin/activate

# Ejecutar el servidor
python app.py
```

El servidor iniciará en: **http://localhost:5000**

## Nuevos Endpoints API

### POST `/transcribe`
Convierte audio a texto usando Whisper de OpenAI
```json
Request:
{
  "audio": "base64_encoded_audio_data"
}

Response:
{
  "texto": "texto transcrito",
  "success": true
}
```

### POST `/synthesize`
Convierte texto a audio MP3 usando TTS de OpenAI
```json
Request:
{
  "texto": "texto a convertir a voz"
}

Response:
{
  "audio": "base64_encoded_mp3_audio",
  "success": true
}
```

### POST `/chat`
Procesa mensaje y genera respuesta (igual que antes)
```json
Request:
{
  "mensaje": "tu mensaje aquí"
}

Response:
{
  "respuesta": "respuesta del agente",
  "reserva": null  // o datos de reserva si la hay
}
```

## Características nuevas

✅ **Micrófono mejorado**: Usa MediaRecorder en lugar de Web Speech API
✅ **Mejor precisión**: Whisper de OpenAI es más preciso que el navegador
✅ **Voz natural**: TTS de OpenAI suena más natural y profesional
✅ **Transiciones fluidas**: El audio se reproduce automáticamente
✅ **Manejo de errores**: Mensajes claros si algo falla

## Solución de problemas

### "Error: Permiso de micrófono denegado"
- Verifica que has permitido acceso al micrófono en la configuración del navegador
- En Chrome: Menú → Configuración → Privacidad → Permisos del sitio → Micrófono

### "Error de transcripción" o "Error al generar voz"
- Verifica que tu API key de OpenAI sea válida
- Verifica que tengas saldo/cuota en tu cuenta de OpenAI
- Revisa la consola del desarrollador (F12) para más detalles

### El audio no se reproduce
- Verifica que tu navegador no tenga silenciado el audio del sitio
- Intenta con otro navegador (Chrome o Edge recomendados)

### Demora en la respuesta
- La primera solicitud puede demorar un poco más
- Whisper y TTS de OpenAI toman algunos segundos

## Costos de OpenAI

Este sistema usa tres APIs de OpenAI:
- **Whisper** (speech-to-text): ~$0.02 por minuto de audio
- **GPT-4 Mini** (chat): ~$0.00015 por 1K tokens
- **TTS** (text-to-speech): ~$0.015 por 1M caracteres

Monitorea tu uso en https://platform.openai.com/account/usage

## Configuración personalizada

### Cambiar voz del bot
En `app.py`, línea ~72:
```python
voice="alloy",  # Opciones: alloy, echo, fable, onyx, shimmer, nova
```

### Cambiar modelo de chat
En `config.py`:
```python
OPENAI_MODEL = "gpt-4o-mini"  # O usa "gpt-4o", "gpt-3.5-turbo"
```

### Cambiar formato de audio
En `app.py`, línea ~72:
```python
response_format="mp3"  # O usa "opus", "aac", "flac"
```

## Recursos útiles

- [Documentación OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text)
- [Documentación OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech)
- [Documentación OpenAI Chat](https://platform.openai.com/docs/guides/chat)

---

¡Tu agente telefónico está listo para interactuar por voz! 🎉
