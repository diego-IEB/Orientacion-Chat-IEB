#import config
import openai
import os
import io
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv
 
load_dotenv()

# Configuración de la clave API de OpenAI
#openai.api_key = config.key
openai.api_key = os.getenv('OPENAI_API_KEY')

def document_indexing(documento, indice):
    try:
        print(f"Intentando cargar el documento: {documento}.txt")
        with io.open(f"{documento}.txt", 'r', encoding='utf-8') as file:
            text = file.read()
        print("Documento cargado. Procesando páginas...")

        pages = text.split('\n\n')
        documents = [Document(page_content=page) for page in pages]

        embeddings = OpenAIEmbeddings()
        faiss_index = FAISS.from_documents(documents, embeddings)
        faiss_index.save_local(indice)
        print("Indexación completada correctamente.")
    except Exception as e:
        print(f"Error durante la indexación: {e}")

if __name__ == "__main__":
    documento = "info"
    indice = "index"
    document_indexing(documento, indice)
