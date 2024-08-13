from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    redirect,
    url_for
)
import os
import requests
from dotenv import load_dotenv
from dadata import Dadata
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
token = os.getenv('TOKEN')
secret = os.getenv('SECRET')
dadata = Dadata(token, secret)
access_key = os.getenv('ACCESS_KEY')


@app.route('/')
def index_page():
    return render_template('index.html')

@app.post('/')
def add_city():
    location = request.form.to_dict().get('location', '')
    if location == '':
        return render_template('404.html')
    return redirect(url_for('render_forecasts', location=location))

@app.route('/<string:location>')
def render_forecasts(location):
    result = dadata.clean("address", location)
    lat = result['geo_lat']
    lon = result['geo_lon']
    headers = {
        'X-Yandex-Weather-Key': access_key
    }
    response = requests.get(f"https://api.weather.yandex.ru/v2/forecast?lat={lat}&lon={lon}", headers=headers)
    data = response.json()
    temperature = data.get('fact').get('temp')
    icon = data.get('fact').get('icon')
    condition = data.get('fact').get('condition')
    feels_like = data.get('fact').get('feels_like')
    wind_speed = data.get('fact').get('wind_speed')
    conditionDictionary = {
        "clear" : "ясно",
        "partly-cloudy" : "малооблачно",
        "cloudy": "облачно с прояснениями",
        "overcast" : "пасмурно",
        "light-rain" : "небольшой дождь",
        "rain" : "дождь",
        "heavy-rain" : "сильный дождь",
        "showers" : "ливень",
        "wet-snow" : "дождь со снегом",
        "light-snow" : "небольшой снег",
        "snow" : "снег",
        "snow-showers" : "снегопад",
        "hail" : "град",
        "thunderstorm" : "гроза",
        "thunderstorm-with-rain" : "дождь с грозой",
        "thunderstorm-with-hail" : "гроза с градом"
    }
    forecasts = data.get('forecasts')
    conditionRu = conditionDictionary.get(condition)
    return render_template('forecasts.html', location=location, temperature=temperature, 
                            condition=conditionRu, forecasts=forecasts, conditionDictionary=conditionDictionary,
                            feels_like=feels_like, wind_speed=wind_speed, icon=icon)