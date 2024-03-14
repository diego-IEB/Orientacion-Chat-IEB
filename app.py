from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from code_main import generate_response
import os
import openai

load_dotenv() 

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

openai.api_key = os.getenv('OPENAI_API_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversation.db'
db = SQLAlchemy(app)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(10))
    content = db.Column(db.Text)

try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print("Error durante la inicialización de la base de datos:", e)

tema_conversacion = None

@app.route('/', methods=['GET'])
def home():
    conversation = Conversation.query.all()
    return render_template('index.html', conversation=conversation)

@app.route('/get-response', methods=['POST'])
def get_bot_response():
    try:
        global tema_conversacion
        user_input = request.form['user_input']
        bot_response, tema_conversacion = generate_response(user_input, tema_conversacion)

        user_message = Conversation(role='user', content=user_input)
        bot_message = Conversation(role='bot', content=bot_response)

        db.session.add(user_message)
        db.session.add(bot_message)
        db.session.commit()

        response_html = f"""
            <div class='message user'>{user_input}</div>
            <div class='message bot'>{bot_response}</div>
        """
        return response_html
    except Exception as e:
        print("Error al obtener respuesta del bot:", e)
        return "Error al obtener respuesta del bot."

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)








#@app.route('/', methods=['GET', 'POST'])
#def home():
 #   if 'conversation' not in session:
  #      session['conversation'] = []
    
 #   if request.method == 'POST':
  #      user_input = request.form['user_input']
   #     bot_response = generate_response(user_input)
#
 #       # Añadir la pregunta y la respuesta al historial de la conversación en la sesión
  #      session['conversation'].append({'role': 'user', 'content': user_input})
   #     session['conversation'].append({'role': 'bot', 'content': bot_response})
    #    session.modified = True
   # print(session['conversation'])
   # return render_template('index.html', conversation=session.get('conversation', []))