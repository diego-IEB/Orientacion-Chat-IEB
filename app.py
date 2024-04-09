from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from code_main import generate_response
import os
import openai

load_dotenv() 

app = Flask(__name__) #Se crea una instancia de Flask para la aplicación web.
app.secret_key = os.getenv('FLASK_SECRET_KEY') #Se establece una clave secreta para la aplicación Flask, utilizada para mantener sesiones seguras.

openai.api_key = os.getenv('OPENAI_API_KEY') #Se configura la clave API de OpenAI.

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversation.db' #Se configura la URI de la base de datos para SQLAlchemy, especificando que se usará SQLite y el nombre del archivo de la base de datos.
db = SQLAlchemy(app)

class Conversation(db.Model): #Se define el Modelo "Conversation" para almacenar los mensajes de la conversación en la bbdd
    id = db.Column(db.Integer, primary_key=True) #Campo de la bbdd: Id del mensaje
    role = db.Column(db.String(10)) #Campo de la bbdd: rol del mensaje como bot o usuario
    content = db.Column(db.Text) #Campo de la bbdd: contenido del mensaje

try:
    with app.app_context():
        db.create_all() #Creación de las tablas de la bbdd.
except Exception as e:
    print("Error durante la inicialización de la base de datos:", e)

tema_conversacion = None

@app.route('/', methods=['GET'])
def home(): #función home que se muestra cada vez que el usuario haga una  pregunta o solicitud a la ruta raiz "/".
    conversation = Conversation.query.all() #consulta a la tabla Conversation de SQLAlchemy y alamcenamiento de todas las entradas
    return render_template('index.html', conversation=conversation) #se pide a la app de Flask que renderice la plantilla html: index.html, pasando y mostrando dinámicamente el contenido de la variable conversación. 

@app.route('/get-response', methods=['POST'])
def get_bot_response(): #función get_bot_response procesa las solicitudes POST recibidas en /get-response. Toma el input del usuario, genera una respuesta y devuelve la respuesta en formato html.
    try:
        global tema_conversacion #para mantener un contexto en la conversación, la variable tema_conversacion va variando según los inputs recibidos.
        user_input = request.form['user_input'] #extrae el mensaje introducido por el usuario
        bot_response, tema_conversacion = generate_response(user_input, tema_conversacion) #pasamos el mensaje del usuario y el mensaje del usuario a la funcion generate_response y ésta retorna una respuesta.

        user_message = Conversation(role='user', content=user_input) #instancia del modelo Conversation para el mensaje del usuario
        bot_message = Conversation(role='bot', content=bot_response) #instancia del modelo conversatio para el mensaje del bot.

        db.session.add(user_message)
        db.session.add(bot_message)
        db.session.commit() #Se guardan ambas instancias en la bbdd.

        response_html = f"""
            <div class='message user'>{user_input}</div>
            <div class='message bot'>{bot_response}</div>
        """
        return response_html #devuelve los string de html tanto del usuario como del bot, formateados para la visualización.
    except Exception as e: #manejo de errores
        print("Error al obtener respuesta del bot:", e)
        return "Error al obtener respuesta del bot."

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

