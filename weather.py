import json  # to work with json data
import requests  # to send requests to APIs
from math import floor
from flask import Flask, render_template, request  # flask libs

APIs = {
    'coordinates': '06885633a5bd4142814a571258329b2e',
    'data': '77832af32729e25f118fc354c25708f9'
}

wind_classification = {
    (0, 11): "Light wind",
    (12, 28): "Gentle wind",
    (29, 38): "Fresh wind",
    (39, 61): "Strong wind",
    (62, 88): "Gale",
    (89, 117): "Whole gale"
}


app = Flask(__name__)


def convert_temperature(degree):
    return str(floor(int(degree)-273.15))


def get_lat_long(address):
    location_url = f"https://api.geoapify.com/v1/geocode/search?text={address}&format=json&apiKey={APIs['coordinates']}"
    result_coordinates = requests.get(location_url)
    if result_coordinates.status_code == 200 and address != ", ":
        info_coordinates = dict(result_coordinates.json())
        return (
            info_coordinates['results'][0]['lat'],
            info_coordinates['results'][0]['lon']
        )
    else:
        return None


def wind_classifier(wind_speed):
    for interval, status in wind_classification.items():
        if interval[0] <= wind_speed < interval[1]:
            return status
    return "Hurricane"


def get_data(coordinates):
    data_list = list()
    if coordinates is not None:
        lat, lon = coordinates
        weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={APIs['data']}"
        result_data = requests.get(weather_url)
        if result_data.status_code == 200:
            info_data = result_data.json()
            for i in range(40):
                data = dict()  # create dictionary to store our data
                data['status']      = info_data['list'][i]['weather'][0]['description']
                data['temperature'] = convert_temperature(info_data['list'][i]['main']['temp'])+" C"
                data['clouds']      = str(info_data['list'][i]['clouds']['all'])+"%"
                data['wind_status'] = wind_classifier(info_data['list'][i]['wind']['speed'])
                data['time']        = info_data['list'][i]['dt_txt']
                data_list.append(data)
    else:
        data = dict()  # create dictionary to store our data
        data['status'] = ""
        data['temperature'] = ""
        data['clouds'] = ""
        data['wind_status'] = ""
        data['time'] = ""
        data_list.append(data)
    for i in range(40):
        print(json.dumps(data_list[i], indent=2))
    return data_list[0]


@app.route('/', methods=["POST", "GET"])
def function():
    if request.method == "POST":
        data_var = get_data(get_lat_long(f"{request.form['city']}, {request.form['country']}"))
        return render_template('index.html',
                               status_var     = data_var['status'],
                               temperature_var= data_var['temperature'],
                               clouds_var     = data_var['clouds'],
                               wind_var       = data_var['wind_status'],
                               time_var       = data_var['time'])
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
