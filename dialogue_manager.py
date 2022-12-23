import time

from environs import Env
import speach_controller as sc
from nlp_analyzer import get_response
import json
import requests
from datetime import datetime, timedelta, date

env = Env()
env.read_env('.env')


def start_bot():
    voice_mode = True
    listen_mode = True
    intents = load_intents()
    give_response('\n\nПривіт, я голосивий помічник Погода бот,\n'
                  ' я існую щоб допомогти вам бути вкурсі актуальної погоди.\n'
                  'Будь-ласка, скажи мені, якщо ти хочеш, щоб я перестав говорити вголос\n '
                  'aбо\і слухати тебе через мікрофон', voice_mode)

    while True:

        command = get_reply(listen_mode)
        result = get_response(command, intents)
        give_response(result['response'], voice_mode)

        match result['tag']:
            case 'voice-on':
                voice_mode = True
            case 'voice-off':
                voice_mode = False
            case 'listen-on':
                listen_mode = True
            case 'listen-off':
                listen_mode = False
            case 'get-weather-today':
                get_forecast_for_day(voice_mode, 1)
            case 'get-weather-tomorrow':
                get_forecast_for_day(voice_mode, 2)
            case 'get-weather-aftertomorrow':
                get_forecast_for_day(voice_mode, 3)
            case 'get-forecast-today':
                get_weather_for_day(voice_mode)
            case 'get-fallout-today':
                will_snow_rain(voice_mode, 1)
            case 'get-fallout-tomorrow':
                will_snow_rain(voice_mode, 2)
            case 'get-fallout-aftertomorrow':
                will_snow_rain(voice_mode, 3)
            case 'farewell':
                break
            case _:
                pass

def load_intents():
    return json.loads(open('resources/intents.json', encoding='utf-8').read())


def give_response(response, voice_mode):
    if voice_mode:
        sc.read(response)
    print(response)


def get_reply(listen_mode):
    if listen_mode:
        reply = sc.listen()
    else:
        reply = input("")
    return reply

def get_weather_for_day(voice_mode):
    weather = requests.get('http://api.weatherapi.com/v1/forecast.json',
                           params={'key': env.str('API-KEY'), 'q': 'auto:ip', 'lang': 'uk',
                                   'days': 1}).json()
    forecast = weather['forecast']['forecastday'][0]['hour']
    needed = [hour for hour in forecast if hour['time_epoch'] > time.time()]
    if not needed:
        needed = forecast[-1]
    step = 1
    if len(needed)>=5:
        step = 2
    if len(needed)>=8:
        step = 3
    if len(needed)>=12:
        step = 4
    for hour in needed[::step]:
        print("О " + datetime.strptime(hour['time'], '%Y-%m-%d %H:%M').strftime('%H:%M') + " буде " + hour['condition'][
            'text'].lower() + " температура: " + str(int(hour['temp_c'])) + " по цельсію")


def get_forecast_for_day(voice_mode, day):
    forecast = get_forecast(day)
    give_response(" від " + str(int(forecast['day']['mintemp_c'])) + " по цельсію до " + str(int(forecast['day']['maxtemp_c']))+
                   "по цельсію буде " + forecast['day']['condition']['text'].lower(), voice_mode)

def will_snow_rain(voice_mode, day):
    forecast = get_forecast(day)
    if forecast['day']["daily_will_it_rain"]:
        give_response("буде дощ, візьми парасольку!", voice_mode)
    elif forecast['day']["daily_will_it_snow"]:
        give_response("буде сніг, приготуйся!", voice_mode)
    else:
        give_response("усе буде добре, не хвилюйся!", voice_mode)


def get_forecast(day_req):
    weather = requests.get('http://api.weatherapi.com/v1/forecast.json',
                           params={'key': env.str('API-KEY'), 'q': 'auto:ip', 'lang': 'uk',
                                   'days': day_req}).json()

    return [day for day in weather['forecast']['forecastday'] if
                datetime.strptime(day['date'], '%Y-%m-%d').date() == date.today() + timedelta(
                    days=day_req-1)][0]