from flask import Flask, request, render_template, redirect, url_for, flash,session
import openai
from code_main import generate_response

app = Flask(__name__)
app.secret_key ='\xb22q\xcfp\xe6W[@\xc1\xaf\xf7V\xff\xfaU'

@app.route('/', methods=['GET'])
def home():
    # Asegurar que hay una conversación en la sesión, si no, inicializarla
    if 'conversation' not in session:
        session['conversation'] = []

    # Mostrar la página con la conversación actual
    return render_template('index.html', conversation=session.get('conversation', []))


@app.route('/get-response', methods=['POST'])
def get_bot_response():
    user_input = request.form['user_input']
    bot_response = generate_response(user_input)
   
    if 'conversation' not in session:
        session['conversation'] = []

    print("Antes de agregar:", session['conversation'])   

    # Añadir la pregunta y la respuesta al historial de la conversación en la sesión
    session['conversation'].append({'role': 'user', 'content': user_input})
    session['conversation'].append({'role': 'bot', 'content': bot_response})
    
    session.modified = True
    print("Después de agregar:", session['conversation'])   

    return redirect(url_for('home'))

@app.route('/show-session')
def show_session():
    # Imprimir el contenido de la sesión en la consola del servidor
    print(session)
    # O retornar una representación del contenido de la sesión en la respuesta HTTP
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