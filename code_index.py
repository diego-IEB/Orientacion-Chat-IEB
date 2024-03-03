import config
import openai
import os
import io
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document 

openai.api_key = config.key
os.environ["OPENAI_API_KEY"] = config.key

def document_indexing(documento, indice):
    try:
        print(f"Intentando cargar el documento: {documento}.txt")
        with io.open(f"{documento}.txt", 'r', encoding='utf-8') as file:
            text = file.read()
        print("Documento cargado. Procesando páginas...")

        # Suponiendo que cada "página" de tu documento está separada por dos saltos de línea
        pages = text.split('\n\n')

        # Convertimos cada página en un objeto Document
        documents = [Document(page_content=page) for page in pages]

        embeddings = OpenAIEmbeddings()
        faiss_index = FAISS.from_documents(documents, embeddings)
        faiss_index.save_local(indice)
        print("Indexación completada correctamente.")
    except Exception as e:
        print(f"Error durante la indexación: {e}")

if __name__ == "__main__":
    documento = "info"  # Nombre del archivo sin la extensión .txt
    indice = "index"  # Nombre del índice para guardar
    document_indexing(documento, indice)
