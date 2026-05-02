# 🎤 Agente Telefónico AI con RAG

Agente telefónico inteligente para restaurante Casa Laguna con integración de RAG (Retrieval-Augmented Generation) para respuestas basadas en información real sin alucinaciones.

## 🚀 Características

- ✅ Agente telefónico con voz usando OpenAI Whisper, GPT-4o-mini y TTS
- ✅ Sistema RAG integrado para evitar alucinaciones
- ✅ Gestión de reservaciones automática
- ✅ Persistencia de datos en JSON
- ✅ Interface web interactiva
- ✅ Información segura de API Key

## 📋 Requisitos Previos

- Python 3.8+
- Conda (o virtualenv)
- Cuenta de OpenAI con API Key
- Git

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/QuirKyLocKet-33/Agente-AI-telefonico.git
cd Agente-AI-telefonico
```

### 2. Crear entorno virtual
```bash
conda create -n bot python=3.12
conda activate bot
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copia el archivo `.env.example` a `.env` y completa con tu información:

```bash
cp .env.example .env
```

Edita `.env` y añade tu OpenAI API Key:
```
OPENAI_API_KEY=sk-proj-tu-clave-aqui
```

**⚠️ IMPORTANTE**: Nunca subas el archivo `.env` a GitHub. Está excluido en `.gitignore`.

### 5. Procesar datos RAG (Primera vez)
```bash
python backend/ingest_rag.py
```

Este comando:
- Lee los archivos JSON con información del restaurante
- Genera embeddings de los datos
- Crea la base de datos vectorial en `data/embeddings/vector_db/v1/`

### 6. Ejecutar el agente
```bash
python app.py
```

Abre en tu navegador: **http://localhost:5000**

## 📁 Estructura del Proyecto

```
tareabot/
├── backend/
│   ├── ingest_rag.py          # Procesa JSONs → Embeddings
│   └── rag_retriever.py        # Busca información relevante
├── data/
│   ├── docs/
│   │   └── casalaguna_tampico/
│   │       ├── contact/contact.json
│   │       ├── frequent_requests/faqs.json
│   │       ├── locations/location.json
│   │       ├── menu/menu.json
│   │       └── politics/politics.json
│   └── embeddings/vector_db/   # BD vectorial (se crea automáticamente)
├── templates/
│   └── index.html              # Interface web
├── app.py                      # Servidor Flask
├── chat_service.py             # Servicio de chat + RAG
├── config.py                   # Configuración
├── requirements.txt            # Dependencias
├── .env.example               # Plantilla de variables
├── .gitignore                 # Archivos a ignorar en git
└── README.md                  # Este archivo
```

## 🔐 Seguridad

- Las claves API se cargan desde variables de entorno (`.env`)
- Nunca se comitean secretos en GitHub
- `.gitignore` excluye archivos sensibles automáticamente

## 📚 Documentación Adicional

- [RAG_SETUP.md](RAG_SETUP.md) - Guía detallada del sistema RAG
- [INSTRUCCIONES_VOZ.md](INSTRUCCIONES_VOZ.md) - Instrucciones del agente telefónico

## 🧪 Pruebas Recomendadas

Haz estas preguntas para verificar que todo funciona:

1. "¿Qué tipo de tostadas tienen?"
2. "¿Cuál es el teléfono del restaurante?"
3. "¿A qué hora cierran?"
4. "¿Puedo cancelar mi reservación?"

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes, abre un issue primero para discutir los cambios propuestos.

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.


## 👨‍💼 Autor

- QuirKyLocKet-33

---

**¿Dudas o problemas?** Abre un issue en GitHub.
