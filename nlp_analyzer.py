import os
import random
import pickle
import numpy as np
import stanza
from tensorflow.python.keras.models import load_model
from autocorrect import Speller
import logging


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
logging.getLogger("stanza").setLevel(logging.WARNING)

stanza.download('uk')
nlp = stanza.Pipeline(lang='uk', processors='tokenize,mwt,pos,lemma', tokenize_no_ssplit=True)
spell = Speller('uk')

model = load_model('resources/bot_model.h5')
words = pickle.load(open('resources/words.pkl', 'rb'))
classes = pickle.load(open('resources/classes.pkl', 'rb'))


def format_command(command):
    ignore_letters = ['?', '!', ".", ","]
    sentence_words = []
    command = spell(command)
    for sent in nlp(command).sentences:
        for word in sent.words:
            if word.lemma not in ignore_letters:
                sentence_words.append(word.lemma)
    return sentence_words


def get_bag_of_words(command):
    sentence_words = format_command(command)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_tag(command):
    bow = get_bag_of_words(command)
    result = model.predict(np.array([bow]))[0]
    results = [[i, r] for i, r in enumerate(result) if r > 0.25]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(command, intents_json):
    intents_list = predict_tag(command)
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    fitting_response = ''
    for i in list_of_intents:
        if i['tag'] == tag:
            fitting_response = {'response': random.choice(i['responses']), 'tag': i['tag']}
            break
    return fitting_response


