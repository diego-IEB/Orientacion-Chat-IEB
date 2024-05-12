from flask import Flask, request, render_template, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy.exc import OperationalError  # Importar directamente la excepción
from code_main import generate_response, check_relevance, is_question_result
import os, uuid  # Importa uuid aquí
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
import nltk
from shared import db, Conversation, update_tema_entrevista
from dotenv import load_dotenv
load_dotenv() 

nltk.download('punkt')  # Descargar los recursos necesarios
app = Flask(__name__)
app.run(host='0.0.0.0', port=8000)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversation.db'
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario_chatbot@ChatIEBPostgres:IEB_2024@ChatIEBPostgres.postgres.database.azure.com/chatbot_db?sslmode=require'


# Configuración básica de logging
logging.basicConfig(level=logging.DEBUG)
# Handler de logging para escribir a un archivo con rotación
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36))  # UUID tiene 36 caracteres
    role = db.Column(db.String(10))
    is_question = db.Column(db.Boolean, default=False)  # Nuevo campo para representar si es una pregunta
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tema_entrevista = db.Column(db.Text) 

with app.app_context():
    app.logger.info("Intentando crear tablas...")
    db.create_all()
    app.logger.info("Intento de creación de tablas finalizado.")

@app.route('/', methods=['GET'])
def home():
    session['chat_session_id'] = str(uuid.uuid4())  # Reinicia la sesión de chat
    return render_template('index.html', conversation=[])


@app.route('/get-response', methods=['POST'])
def get_bot_response():
    try:
        current_time = datetime.utcnow()
        chat_session_id = session.get('chat_session_id', str(uuid.uuid4()))
        session['chat_session_id'] = chat_session_id  # Asegurarse de que cada sesión tiene un UUID

        if 'message_count' not in session:
            session['message_count'] = 0 

        if 'start_time' not in session or 'prompt_count' not in session:
            session['start_time'] = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            session['prompt_count'] = 0

        start_time = datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M:%S.%f')
        if (current_time - start_time) > timedelta(minutes=10):
            session['start_time'] = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            session['prompt_count'] = 0
        if session['prompt_count'] >= 15:
            return "Has alcanzado el límite de preguntas permitidas por sesión."
    
        user_input = request.form['user_input']
        prompt = user_input

        print("Prompt que se enviará a OpenAI:", prompt)

        bot_response, is_question_flag, tema_conversacion = generate_response(prompt, None)
        tema_entrevista = update_tema_entrevista(bot_response)  # Asumiendo que ahora update_tema_entrevista toma directamente el texto del bot
        is_question_result_flag = is_question_result(bot_response)  # Utiliza la función is_question que implementaste
        user_message = Conversation(session_id=chat_session_id, role='user', content=user_input)
        bot_message = Conversation(session_id=chat_session_id, role='bot', content=bot_response, is_question=is_question_flag)
    
        
        db.session.add(user_message)
        db.session.add(bot_message)

        db.session.commit()  # Committing at once here

        session['message_count'] += 1
        session['prompt_count'] += 1

        response_html = f"<div class='message user'>{user_input}</div><div class='message bot'>{bot_response}</div>"
        return jsonify({'html': response_html})

    except OperationalError as e:
        app.logger.error("Database lock encountered, retrying...")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        app.logger.error(f'Error al procesar la solicitud: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/history', methods=['GET'])
def history():
    # Filtrar conversaciones por ID de sesión para enviar solo las relevantes
    chat_session_id = session.get('chat_session_id')
    conversation = Conversation.query.filter_by(session_id=chat_session_id).all()
    return render_template('history.html', conversation=conversation)