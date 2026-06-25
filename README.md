# S2-D3 — RAG básico con LangChain

## Descripción

Este proyecto implementa una práctica básica de RAG usando Python, LangChain y ChromaDB.

El programa carga un documento de texto, lo divide en fragmentos, crea embeddings, guarda la información en una base vectorial y permite hacer preguntas desde la consola.

## Flujo del proyecto

```
Documento → Chunks → Embeddings → ChromaDB → Pregunta del usuario → Búsqueda semántica → Respuesta basada en el documento
```

## Estructura del proyecto

```
S2-D3_RAG_LangChain_Carlos_Gonzalez
│
├── documentos/
│   └── manual_empresa.txt    ← Documento de prueba
│
├── chroma_langchain/         ← Base vectorial (se crea automáticamente)
│
├── rag_basico.py             ← Código principal del RAG
│
└── README.md                 ← Este archivo
```

## Tecnologías utilizadas

- Python
- LangChain
- ChromaDB
- HuggingFace Embeddings
- Sentence Transformers

## Partes del RAG implementadas

| Parte del RAG         | En el código                         |
|-----------------------|--------------------------------------|
| Cargar documento      | `TextLoader`                         |
| Dividir en chunks     | `RecursiveCharacterTextSplitter`     |
| Crear embeddings      | `HuggingFaceEmbeddings`              |
| Guardar en vector DB  | `Chroma`                             |
| Preguntar             | `input()`                            |
| Recuperar información | `similarity_search()`                |
| Responder con contexto| Imprime fragmento más relevante      |

## Cómo ejecutar

1. Instalar dependencias:

```bash
python -m pip install langchain langchain-community langchain-text-splitters langchain-chroma chromadb sentence-transformers langchain-huggingface
```

2. Ejecutar el programa:

```bash
python rag_basico.py
```

3. Escribir una pregunta en consola.

**Ejemplo:**

```
¿Cómo recupero mi contraseña?
```

## Resultado esperado

El sistema debe recuperar el fragmento del documento más relacionado con la pregunta del usuario.

**Preguntas de prueba:**
- ¿Cómo recupero mi contraseña?
- ¿Quién me ayuda con una cotización?
- ¿Qué hace Recursos Humanos?

---

**Nombre:** Carlos Emmanuel González Álvarez  
**Actividad:** S2-D3 — RAG completo: implementación con LangChain
