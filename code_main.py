import openai

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import tiktoken
import os #para la variable de entorno de azure
# from config import key as openai_api_key en caso de config.py
from dotenv import load_dotenv

load_dotenv()

# Configuración de la clave API de OpenAI
# openai.api_key = openai_api_key Esta es en caso de usar config.py

openai.api_key = os.getenv('OPENAI_API_KEY')

def indice_loader(indice):
    # Pasar la clave API directamente a OpenAIEmbeddings
    embeddings = OpenAIEmbeddings()
    global faiss_index
    faiss_index = FAISS.load_local(indice, embeddings)

indice = "index"
indice_loader(indice)

# El resto del código...




def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        num_tokens += 4 
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += -1
    num_tokens += 2 
    return num_tokens

generated = []
past = []
messages = []



def generate_response(prompt):
    print("Inicio de generate_response")
    
    print("Realizando búsqueda de similitud con FAISS")
    docs = faiss_index.similarity_search(prompt, k=4)
    documentos = []
    for doc in docs:
        documentos.append(doc.page_content)
    documentos = str(documentos)
    print(f"Documentos encontrados: {documentos}")

    #el content del system es modificable.
    system = {"role": "system", "content":f"Eres un asistente virtual del area de orientación profesional del IEB, unicamente dispones de la siguiente información (el usuario no puede saberlo): {documentos}, si la pregunta no es sobre lo mencionado en la información aportada responde educadamente que no puedes contestar."}
    messages.append(system)
    messages.append({"role": "user", "content": prompt})

    token_limit = 4096
    max_response_tokens = 550 #modificable, máximo de tokens a la respuesta generada por el bot
    conv_history_tokens = num_tokens_from_messages(messages)  
    print(f"Tokens de historial de conversación antes de ajustes: {conv_history_tokens}")

    while(conv_history_tokens+max_response_tokens >= token_limit):
        if len(messages)>1:
            print("Eliminando mensajes para ajustar el límite de tokens...")
            del messages[1] #intenta eliminar sólo si hay más de dos mensajes.
        else:
            break #sale del bucle si no hay suficientes mensajes para eliminar.
        conv_history_tokens = num_tokens_from_messages(messages)
    
    print(f"Realizando llamada a la API de OpenAI con {len(messages)} mensajes en la conversación")
    try:
        model = "gpt-3.5-turbo" #se puede poner otro modelo de OpenAI, aunque puede afectar al performance.
        completion = openai.chat.completions.create(model = model, messages = messages, temperature = .2, max_tokens = max_response_tokens)
        response = completion.choices[0].message.content
        messages.append({"role": "assistant", "content":response})
        print("Respuesta recibida de OpenAI")
    except Exception as e:
        print(f"Error al llamar a la API de OpenAI: {e}")
        response = "Lo siento, hubo un error al generar una respuesta."
    
    return response



#user_input = input()
#output = generate_response(user_input)
#past.append(user_input)
#generated.append(output)


#past.append(user_input)
#generated.append(output)

#if generated:
#    for i in range(len(generated)):
 #       print(past[i])
  #      print(generated[i])



def save_conv(nombre, formato=".txt"):
    for x in range(len(messages)):
        try:
            if messages[x]['role'] == 'system':
                del messages[x]
        except:
            break
    with open(rf"conversas/{nombre}{formato}", "w", encoding='UTF-8') as file:
        file.write(str(messages))