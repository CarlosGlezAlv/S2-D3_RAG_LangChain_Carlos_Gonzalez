
import os
from langchain_classic.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

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
    doc = loader.load()
    todos_los_documentos.extend(doc)
    print(f"{archivo}")

print()
print(f"  Total de documentos cargados: {len(todos_los_documentos)}")
print()


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

base_vectorial = Chroma.from_documents(
    documents=todos_los_documentos,
    embedding=embeddings,
    persist_directory="./chroma_langchain"
)

while True:
    pregunta = input("¿Qué deseas preguntar?: ")
    if pregunta.strip().lower() == "salir":
        break

    if pregunta.strip() == "":
        print("Por favor escribe una pregunta válida.\n")
        continue
    resultados = base_vectorial.similarity_search(pregunta, k=2)


    print()
    print(f"Pregunta: {pregunta}")
    print()

    for i, resultado in enumerate(resultados):
        nombre_doc = os.path.basename(resultado.metadata.get("source", "desconocido"))
        print(f"  ┌── Fragmento {i + 1} — Fuente: {nombre_doc}")
        print(f"  │")
        for linea in resultado.page_content.strip().split("\n"):
            print(f"  │  {linea}")
        print(f"  └{'─' * 45}")
        print()

    if resultados:
        nombre_fuente = os.path.basename(resultados[0].metadata.get("source", ""))
        print(f"Fuente principal: {nombre_fuente}")
        print()
        for linea in resultados[0].page_content.strip().split("\n"):
            print(f"  {linea}")
    else:
        print("No encontré información relacionada con tu pregunta.")


