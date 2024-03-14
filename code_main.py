import openai
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import tiktoken
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

tema_entrevista = None

def indice_loader(indice):
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    global faiss_index
    faiss_index = FAISS.load_local(indice, embeddings)

indice = "index"
indice_loader(indice)

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

def generate_response(prompt, tema_entrevista):
    print("Inicio de generate_response")
    print("Prompt recibido: ", prompt)

    print("Realizando búsqueda de similitud con FAISS")
    try:
        docs = faiss_index.similarity_search(prompt, k=1)
        documento_mas_relevante = docs[0].page_content
        print("Documento más relevante: ", documento_mas_relevante)
    except Exception as e:
        print("Error durante la búsqueda de similitud con FAISS: ", e)
        return "Error al buscar documentos relevantes.", tema_entrevista

    messages = [
        {"role": "system", "content": f"Eres un asistente virtual del área de orientación profesional del IEB, únicamente dispones de la siguiente información: {documento_mas_relevante}"},
        {"role": "user", "content": prompt}
    ]

    max_response_tokens = 550
    token_limit = 4096 - num_tokens_from_messages(messages, model="gpt-3.5-turbo")

    print("Token limit: ", token_limit, ", Max response tokens: ", max_response_tokens)

    try:
        print("Enviando solicitud a OpenAI con modelo gpt-3.5-turbo")
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response = chat_completion.choices[0].message.content
        print("Respuesta recibida de OpenAI: ", response)
    except Exception as e:
        print("Error al llamar a la API de OpenAI: ", e)
        response = "Lo siento, hubo un error al generar una respuesta."

    lines = response.split("\n")
    formatted_lines = []
    is_list_ordered = False
    list_counter = 1
    for line in lines:
        line = line.strip()
        if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            if not is_list_ordered:
                formatted_lines.append("<ol>")
                is_list_ordered = True
            line = f"<li>{line.split('.', 1)[1].strip()}</li>"
            line = line.replace("<li>1", f"<li>{list_counter}")
            list_counter += 1
        else:
            if is_list_ordered:
                formatted_lines.append("</ol>")
                is_list_ordered = False
            line = f"<p>{line}</p>"
        formatted_lines.append(line)
    if is_list_ordered:
        formatted_lines.append("</ol>")

    formatted_response = "\n".join(formatted_lines)

    return formatted_response, tema_entrevista




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



#def save_conv(nombre, formato=".txt"):
   # for x in range(len(messages)):
    #    try:
      #      if messages[x]['role'] == 'system':
      #          del messages[x]
      #  except:
     #       break
    #with open(rf"conversas/{nombre}{formato}", "w", encoding='UTF-8') as file:
    #   file.write(str(messages))