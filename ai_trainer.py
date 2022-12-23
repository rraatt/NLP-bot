import random
import json
import pickle
import numpy as np
import stanza

from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Activation, Dropout
from tensorflow.python.keras.optimizers import gradient_descent_v2

stanza.download('uk')
nlp = stanza.Pipeline(lang='uk', processors='tokenize,mwt,pos,lemma', tokenize_no_ssplit=True)
# lemmatizer for Ukraian language

intents = json.loads(open('resources/intents.json', encoding='utf-8').read())
# loading a json file with all bot interactions

words = []
# all possible user input words
classes = []
# all classes of interaction
documents = []
# a list of tuples, containing a class and a list of possible user phrases corresponding to this phrase
ignore_letters = ['?', '!', ".", ","]
# ignored symbols

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = []
        for sent in nlp(pattern).sentences:
            for word in sent.words:
                if word.lemma not in ignore_letters:
                    word_list.append(word.lemma)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = sorted(set(words))
classes = sorted(set(classes))

pickle.dump(words, open('resources/words.pkl', 'wb'))
pickle.dump(classes, open('resources/classes.pkl', 'wb'))

training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training)

train_x = list(training[:, 0])
train_y = list(training[:, 1])

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

sgd = gradient_descent_v2.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save('resources/bot_model.h5', hist)

print('Done!')
