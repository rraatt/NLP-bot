import pyttsx3
import speech_recognition as sr


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 0.7
        audio = r.listen(source)
        try:
            return r.recognize_google(audio, language="uk-UA", show_all=True)['alternative'][0]['transcript']
        except TypeError as e:
            return "None"


def read(text):
    eng = pyttsx3.init()
    voices = eng.getProperty('voices')
    voice = voices[3]
    eng.setProperty('voice', voice.id)
    eng.say(text)
    eng.runAndWait()





