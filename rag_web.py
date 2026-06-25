# rag_web.py — RAG con interfaz web, soporte PDF y TXT
# Nombre: Carlos Emmanuel González Álvarez
# S2-D3 — RAG con LangChain + ChromaDB + Flask

import os
import sys
import uuid
import warnings
warnings.filterwarnings("ignore")

# Fix encoding para consola Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, request, jsonify, render_template, session
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import pypdf

# ─── Adaptador de embeddings (ONNX, sin PyTorch) ─────────────────────────────
class ChromaEmbeddingsAdapter(Embeddings):
    def __init__(self):
        self.ef = DefaultEmbeddingFunction()

    def _to_float(self, vec):
        """Convierte numpy array a lista de float nativo de Python."""
        return [float(x) for x in vec]

    def embed_documents(self, texts):
        return [self._to_float(v) for v in self.ef(texts)]

    def embed_query(self, text):
        return self._to_float(self.ef([text])[0])

# ─── Configuración Flask ──────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "rag_langchain_carlos_2024"

UPLOAD_FOLDER = "uploads_web"
CHROMA_FOLDER = "./chroma_web"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

embeddings = ChromaEmbeddingsAdapter()

# Almacén de sesiones: {session_id: Chroma}
sesiones = {}

# ─── Extracción de texto ──────────────────────────────────────────────────────
def extraer_texto_pdf(ruta):
    reader = pypdf.PdfReader(ruta)
    paginas = []
    for i, pagina in enumerate(reader.pages):
        texto = pagina.extract_text()
        if texto and texto.strip():
            paginas.append(Document(
                page_content=texto.strip(),
                metadata={"source": os.path.basename(ruta), "pagina": i + 1}
            ))
    return paginas

def extraer_texto_txt(ruta):
    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
        contenido = f.read()
    return [Document(
        page_content=contenido,
        metadata={"source": os.path.basename(ruta)}
    )]

# ─── Rutas Flask ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    return render_template("index.html")

@app.route("/subir", methods=["POST"])
def subir_documento():
    sid = session.get("sid", str(uuid.uuid4()))
    session["sid"] = sid

    if "archivo" not in request.files:
        return jsonify({"error": "No se recibió ningún archivo"}), 400

    archivo = request.files["archivo"]
    nombre = archivo.filename

    if not nombre:
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    extension = nombre.rsplit(".", 1)[-1].lower()
    if extension not in ["pdf", "txt"]:
        return jsonify({"error": "Solo se aceptan archivos PDF o TXT"}), 400

    ruta = os.path.join(UPLOAD_FOLDER, f"{sid}_{nombre}")
    archivo.save(ruta)

    try:
        if extension == "pdf":
            docs = extraer_texto_pdf(ruta)
        else:
            docs = extraer_texto_txt(ruta)

        if not docs:
            return jsonify({"error": "El documento está vacío o no se pudo leer"}), 400

        # Agregar a la base vectorial de la sesión
        if sid in sesiones:
            sesiones[sid].add_documents(docs)
        else:
            chroma_dir = f"{CHROMA_FOLDER}/{sid}"
            sesiones[sid] = Chroma.from_documents(
                documents=docs,
                embedding=embeddings,
                persist_directory=chroma_dir
            )

        total_paginas = len(docs)
        return jsonify({
            "ok": True,
            "nombre": nombre,
            "paginas": total_paginas,
            "tipo": extension.upper()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/preguntar", methods=["POST"])
def preguntar():
    sid = session.get("sid")
    if not sid or sid not in sesiones:
        return jsonify({"error": "No hay documentos cargados. Sube un archivo primero."}), 400

    data = request.get_json()
    pregunta = data.get("pregunta", "").strip()

    if not pregunta:
        return jsonify({"error": "La pregunta no puede estar vacía"}), 400

    try:
        resultados = sesiones[sid].similarity_search(pregunta, k=3)

        respuestas = []
        for r in resultados:
            respuestas.append({
                "fuente": r.metadata.get("source", "desconocido"),
                "pagina": r.metadata.get("pagina", None),
                "contenido": r.page_content.strip()
            })

        respuesta_principal = respuestas[0]["contenido"] if respuestas else "No encontré información relacionada."

        return jsonify({
            "ok": True,
            "pregunta": pregunta,
            "respuesta": respuesta_principal,
            "fragmentos": respuestas
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/limpiar", methods=["POST"])
def limpiar():
    sid = session.get("sid")
    if sid and sid in sesiones:
        del sesiones[sid]
    session.pop("sid", None)
    return jsonify({"ok": True})

if __name__ == "__main__":
    print()
    print("==========================================")
    print("  RAG WEB - LangChain + ChromaDB + Flask  ")
    print("  Abre en tu navegador:                   ")
    print("  http://localhost:5000                   ")
    print("==========================================")
    print()
    app.run(debug=True, port=5000)
