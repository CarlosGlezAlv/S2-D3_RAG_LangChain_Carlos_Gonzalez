import os
import warnings
warnings.filterwarnings("ignore")

from langchain_classic.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

class ChromaEmbeddingsAdapter(Embeddings):
    def __init__(self):
        self.ef = DefaultEmbeddingFunction()

    def _to_float(self, vec):
        return [float(x) for x in vec]

    def embed_documents(self, texts):
        return [self._to_float(v) for v in self.ef(texts)]

    def embed_query(self, text):
        return self._to_float(self.ef([text])[0])

carpeta_documentos = "documentos"
archivos = [
    "horarios_empresa.txt",
    "contrasenas_acceso.txt",
    "ventas_facturacion.txt",
    "recursos_humanos.txt"
]

todos_los_documentos = []
for archivo in archivos:
    ruta = os.path.join(carpeta_documentos, archivo)
    loader = TextLoader(ruta, encoding="utf-8")
    todos_los_documentos.extend(loader.load())

embeddings = ChromaEmbeddingsAdapter()
base_vectorial = Chroma.from_documents(
    documents=todos_los_documentos,
    embedding=embeddings, persist_directory="./chroma_langchain"
)

while True:
    pregunta = input("Pregunta: ")

    if pregunta.strip().lower() == "salir":
        break

    if pregunta.strip() == "":
        continue

    resultados = base_vectorial.similarity_search(pregunta, k=1)

    if resultados:
        print()
        print("Respuesta:", resultados[0].page_content.strip())
        print()
    else:
        print()
        print("No encontre informacion relacionada.")
        print()
