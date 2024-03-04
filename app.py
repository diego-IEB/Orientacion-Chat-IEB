from flask import Flask, request, render_template, redirect, url_for, session
import openai
from code_main import generate_response
from config import key as openai_api_key

app = Flask(__name__)
app.secret_key = '\xb22q\xcfp\xe6W[@\xc1\xaf\xf7V\xff\xfaU'

# Configuración de la clave API de OpenAI
openai.api_key = openai_api_key

@app.route('/', methods=['GET'])
def home():
    if 'conversation' not in session:
        session['conversation'] = []
    return render_template('index.html', conversation=session.get('conversation', []))

@app.route('/get-response', methods=['POST'])
def get_bot_response():
    user_input = request.form['user_input']
    bot_response = generate_response(user_input)

    if 'conversation' not in session:
        session['conversation'] = []

    session['conversation'].append({'role': 'user', 'content': user_input})
    session['conversation'].append({'role': 'bot', 'content': bot_response})
    
    session.modified = True
    return redirect(url_for('home'))

@app.route('/show-session')
def show_session():
    print(session)
    return str(session)

if __name__ == "__main__":
    app.run(debug=False)



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