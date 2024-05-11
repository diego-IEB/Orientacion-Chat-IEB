import openai
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import re
from nltk.tokenize import word_tokenize
from shared import db, update_tema_entrevista, Conversation


load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
client = openai.Client(api_key=openai_api_key)


def indice_loader(indice):
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    global faiss_index
    faiss_index = FAISS.load_local(indice, embeddings)

indice = "index"
indice_loader(indice)

def aplicar_formato(response):
    formatted_lines = []
    lines = response.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            # Comprobamos si la línea es un ítem de lista
            match = re.match(r'^(\d+\.)\s*(.*?:)', line)
            if match:
                # Aplicamos negrita hasta los dos puntos
                numbered_part, bold_part = match.groups()
                formatted_line = f"<div class='list-item'><strong>{numbered_part} {bold_part}</strong>{line[len(match.group(0)):]}</div>"
            else:
                formatted_line = f"<p>{line}</p>"
            formatted_lines.append(formatted_line)
    return ''.join(formatted_lines)

def generate_response(prompt, tema_entrevista):
    try:
        docs = faiss_index.similarity_search(prompt, k=1)
        documento_mas_relevante = docs[0].page_content
        messages = [{"role": "system", "content": f"Eres un asistente virtual del área de orientación profesional del IEB, únicamente dispones de la siguiente información: {documento_mas_relevante}"}, {"role": "user", "content": prompt}]
        chat_completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages, temperature=0.7)
        response = chat_completion.choices[0].message.content
        formatted_response = aplicar_formato(response)
        is_question_flag = is_question_result(response)  # Evalúa aquí si es pregunta
        return formatted_response, is_question_flag, tema_entrevista
    except Exception as e:
        return "Lo siento, hubo un error al generar una respuesta.", tema_entrevista

def check_relevance(new_input, last_content):
    # Placeholder para función de similitud
    # Deberás implementar un método para evaluar la similitud real aquí.
    return new_input.lower() in last_content.lower()


def is_question_result(text):
    # Utiliza una expresión regular para buscar un signo de interrogación en cualquier parte del texto
    return bool(re.search(r'\?', text))


#2.0 aqui empiezo el desarrollo de la parte de tema_entrevista



