from config import * # impprtamos el token
import telebot # api de telegram
import nltk
import os
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import string # to process standard python strings


import nltk
from nltk.stem import WordNetLemmatizer
nltk.download('popular', quiet=True) # for downloading packages

#Leer el trxto d ela base de datos y hacer tokens
baseDeDatos=open('chatbot.txt','r',errors = 'ignore')

raw=baseDeDatos.read()
raw=raw.lower()# converts to lowercasel
nltk.download('punkt') # first-time use only
nltk.download('wordnet') # first-time use only
oraciones_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
palabras_tokens = nltk.word_tokenize(raw)# converts to list of words
frase_no_contemplada= "" #Para guardar en el txt

#Limpiar palabras
#
# from nltk.corpus import stopwords
##from tqdm import tqdm
#def normalize(s):
 ## replacements={
  #  ("á","a"),
  #  ("é","e"),
  #  ("í", "i"),
   # ("ó","o"),
 #    ("ú","u"), }   
  #for a, b in replacements:
    #    s=s.replace(a,b).replace(a.upper(),b.upper())
 # return s  
#token_limpio=[]  
#guardar=True    
#for i in  tqdm(palabras_tokens)	:
   # for word in stopwords.words('spanish'):
   #   if(word.lower() == i.lower()):
   #       guardar=False
   # if (guardar):
    #   if (len(i)>2):
   #      token_limpio.append(normalize(i))
   # guardar=True
        

lemmer = nltk.stem.WordNetLemmatizer()
#WordNet is a semantically-oriented dictionary of English included in NLTK.
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))



#Leer los patrones del texto ingressdo y buscar ua respesta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#pip install googletrans
from googletrans import Translator
def traducir(user_response, src_lang, dest_lang):
    translator=Translator(service_urls=['translate.google.com'])
    user_response=translator.translate(user_response, src=src_lang, dest=dest_lang).text
    return user_response


def response(user_response):
    #Devuelve la confirmacion de que se guardo la respuesta no satisfactoria
    if(user_response.text == "No"):
            return "Pregunta guardada"
    else:
        user_response = user_response.text
        #Evita la palabra No para cuando se usen los controles
        respuestaChatbot=''
        #Traducir de español a ingles
        user_response = traducir(user_response, 'auto', 'en')
        oraciones_tokens.append(user_response)
        TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
        tfidf = TfidfVec.fit_transform(oraciones_tokens)
        vals = cosine_similarity(tfidf[-1], tfidf)
        idx=vals.argsort()[0][-2]
        flat = vals.flatten()
        flat.sort()
        req_tfidf = flat[-2]
        if(req_tfidf==0):
            respuestaChatbot=respuestaChatbot+"Disculpe no encuentro la informacion"
            return respuestaChatbot
        else:
            respuestaChatbot = respuestaChatbot+oraciones_tokens[idx]
            #traducir de ingles a español
            return traducir(respuestaChatbot, 'en', 'es')
    
    
from telebot.types import ForceReply
from telebot.types import ReplyKeyboardRemove 
from telebot.types import ReplyKeyboardMarkup 
#frfrom telebot.types importom telebot.types import ForceReply
# intsncias del bot
token = os.environ['TOKEN']
bot = telebot.TeleBot(token)
#responde al start
@bot.message_handler(commands=["start"])
#Funcion
def cmd_start(message):
    #da la bienvenida
    botones= ReplyKeyboardRemove()
    bot.reply_to(message,"Bienvendido al bot soporte de la Agencia de viajes, haga sus preguntas")

@bot.message_handler(content_types=["text"])
def bot_mensajes_texto(message):
    botones= ReplyKeyboardRemove()
    botones=ReplyKeyboardMarkup(one_time_keyboard=True
                                 ,input_field_placeholder= "Pulse su respuesta"
                                 ,resize_keyboard=True)
    #gestiona los mensajes de texto recibido
    botones.add("No")
    #valoracion= ForceReply()
    respuesta1=bot.send_message(message.chat.id, response(message))
    #Evita decir 2 veces que aprete el boton
    if respuesta1.text == "Disculpe no encuentro la informacion":
       global frase_no_contemplada
       bot.send_message(message.chat.id, "Seleccione el boton 'No' si no estuvo conforme con la respuesta")
    if(message.text == "No"):
           guardarPregunta(frase_no_contemplada)
    else:
        frase_no_contemplada = message.text
    print(frase_no_contemplada)

def guardarPregunta(message):
    print("Funciona hay q guardar la pregunta no contestada")
    preguntas=open('preguntasSinResolver.txt','a',errors = 'ignore')
    preguntas.write(message+"\n")
        
        
          
def verificarRespuesta(message):
     if message.text!="No" and message.text!="Si":
        msg=bot.send_message(message.chat.id, "Por favor pulse un boton")
        bot.register_next_step_handler(msg,verificarRespuesta)

     else:
         return True

         
#MAIN
if __name__=='__main__':
    print('Iniciando el bot')
    bot.infinity_polling()