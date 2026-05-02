# 🚀 Configuración RAG para Agente Telefónico

## Resumen de Cambios

Tu sistema ahora tiene integración completa de RAG (Retrieval-Augmented Generation) para que el agente telefónico no alucine y responda basado en información real.

## ✅ Cambios Realizados

### 1. **Corrección de Rutas**
- `backend/ingest_rag.py`: Rutas corregidas para apuntar correctamente
- `backend/rag_retriever.py`: Sincronizado con versión v1 de vector_db
- `MODEL_PATH`: Ahora descarga automáticamente de HuggingFace

### 2. **requirements.txt Actualizado**
Se agregaron:
```
sentence-transformers==3.0.0
chromadb==0.4.24
```

### 3. **chat_service.py Integrado con RAG**
El servicio de chat ahora:
- Inicializa RAGRetriever automáticamente
- Busca información relevante antes de responder
- Inyecta contexto en los mensajes a OpenAI
- Fallback seguro si RAG no está disponible

## 📝 Pasos para Ejecutar

### Paso 1: Instalar dependencias
```bash
cd /home/qurikylocket331/chatBot/tareabot
conda activate BOT
pip install -r requirements.txt
```

### Paso 2: Procesar datos con ingestión RAG
```bash
python backend/ingest_rag.py
```
Esto:
- Leerá todos los JSON de información (menús, FAQs, contacto, etc.)
- Generará embeddings de esos datos
- Los almacenará en ChromaDB (en `data/embeddings/vector_db/v1/`)

**Deberías ver output como:**
```
🔹 Cargando modelo de embeddings...
🔹 Cargando JSONs...
   → contact.json: 4 chunks
   → faqs.json: X chunks
   → menu.json: X chunks
   ...
✅ Ingestión completada correctamente.
```

### Paso 3: Ejecutar el agente
```bash
python app.py
```
Abre en navegador: **http://localhost:5000**

## 🔍 Cómo Funciona Ahora

```
Usuario: "¿Qué platillos tienen?"
    ↓
ChatService.enviar_mensaje()
    ↓
RAGRetriever busca en la BD vectorial
    ↓
Encuentra: [menú_tostadas, tacos_varieties, ...]
    ↓
Inyecta contexto en el prompt a OpenAI:
   "Aquí tienes información del restaurante:
    1. Tipos de tostadas Casa Laguna...
    2. Tipos de tacos...
    Pregunta del cliente: ¿Qué platillos tienen?"
    ↓
OpenAI responde basándose SOLO en esa información
    ↓
Respuesta natural al usuario (sin alucinaciones)
```

## 📂 Estructura de Archivos

```
tareabot/
├── backend/
│   ├── ingest_rag.py          # Procesa JSONs → Embeddings
│   └── rag_retriever.py        # Busca información relevante
├── data/
│   ├── docs/casalaguna_tampico/  # Tu información
│   │   ├── contact/contact.json
│   │   ├── frequent_requests/faqs.json
│   │   ├── locations/location.json
│   │   ├── menu/menu.json
│   │   └── politics/politics.json
│   └── embeddings/
│       └── vector_db/v1/       # Base de datos vectorial (se crea al ingestar)
├── chat_service.py             # Integrado con RAG ✅
├── app.py                      # Servidor Flask
└── requirements.txt            # Actualizado con nuevas librerías
```

## 🧪 Verificación

### 1. Verificar que ChromaDB se create correctamente
Después de ejecutar `backend/ingest_rag.py`, verifica que exista:
```bash
ls -la data/embeddings/vector_db/v1/
```

Deberías ver archivos `.db` y directorios.

### 2. Probar RAG directamente
```bash
python -c "
from backend.rag_retriever import RAGRetriever, VECTOR_DB_PATH, COLLECTION_NAME, MODEL_PATH
retriever = RAGRetriever(VECTOR_DB_PATH, COLLECTION_NAME, MODEL_PATH)
results = retriever.retrieve('¿Qué tacos hay?', top_k=3)
for r in results:
    print(f'ID: {r[\"id\"]}')
    print(f'Doc: {r[\"document\"][:200]}')
    print('---')
"
```

### 3. Ver logs de inicialización
Cuando ejecutes `python app.py`, deberías ver:
```
✅ RAG Retriever inicializado correctamente
```

## ⚠️ Posibles Problemas

### Error: "La colección no existe"
**Causa**: No has ejecutado `backend/ingest_rag.py` todavía
**Solución**: Ejecuta `python backend/ingest_rag.py`

### Error: "Modelo no encontrado"
**Causa**: Primera vez descargando el modelo de HuggingFace
**Solución**: Es normal, toma 1-2 minutos en primera ejecución

### No se muestra contexto RAG
**Causa**: RAGRetriever no inicializó correctamente
**Solución**: Revisa los logs de `python app.py` para errores

## 🎯 Pruebas Recomendadas

Haz estas preguntas al agente para verificar que RAG funciona:

1. **Información de menú**
   "¿Qué tipo de tostadas tienen?"
   → Debería listar tostadas reales del menú

2. **Información de contacto**
   "¿Cuál es el teléfono?"
   → Debería dar el teléfono real

3. **Información de horarios**
   "¿A qué hora cierran?"
   → Debería dar horarios reales

4. **Preguntas frecuentes**
   "¿Puedo cancelar mi reservación?"
   → Debería responder basándose en políticas reales

Si **todas** las respuestas usan información de tus JSONs (no inventada), RAG está funcionando correctamente ✅

## 📊 Monitoreo

Para ver qué información está usando el RAG:
1. Abre DevTools (F12) en el navegador
2. Ve a la pestaña **Console** o **Network**
3. Busca los logs de inicialización

## 🚀 Próximos Pasos (Opcional)

- Añadir más documentos a `data/docs/casalaguna_tampico/`
- Ejecutar nuevamente `backend/ingest_rag.py` para reindexar
- Hacer re-ingestión cada vez que actualices información

---

¿Necesitas ayuda ejecutando alguno de estos pasos?
