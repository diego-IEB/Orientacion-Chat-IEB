import nltk
from flask_sqlalchemy import SQLAlchemy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import logging

nltk.download('punkt')
nltk.download('stopwords')

db = SQLAlchemy()

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Puedes ajustar el nivel según necesites
handler = logging.StreamHandler()  # O cualquier otro handler que prefieras
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36))
    role = db.Column(db.String(10))
    is_question = db.Column(db.Boolean, default=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    tema_entrevista = db.Column(db.Text)

def update_tema_entrevista(content):
    try:
        tema_entrevista = extract_keywords(content)
        return tema_entrevista
    except Exception as e:
        logger.error(f"Error al calcular tema de entrevista: {str(e)}")
        return None
    

def extract_keywords(text):
    # Puedes ajustar el método de extracción de palabras clave según necesites
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words if word.isalpha() and word not in stopwords.words('spanish')]
    word_freq = Counter(words)
    common_words = word_freq.most_common(4)  # Ajusta el número según tu preferencia
    return " ".join([word for word, freq in common_words])



# En tu endpoint o función donde manejas la conversación
#def some_function_handling_conversation():
    # Lógica para manejar la conversación
    #response, is_question_flag, tema_entrevista = generate_response(prompt, tema_entrevista)
    
    # Supongamos que decides actualizar el tema después de generar la respuesta
   # updated_tema = update_tema_entrevista(session_id, commit=False)
    #if updated_tema:
    #    try:
     #       db.session.commit()
      #  except Exception as e:
       #     db.session.rollback()
        #    app.logger.error(f"Error committing changes: {str(e)}")