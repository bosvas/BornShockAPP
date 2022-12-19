import requests
import datetime


def get_latitude_longitude_by_city(adress):
    url = f'http://api.positionstack.com/v1/forward?access_key=472cada58ab5cad9347598e392bfd085&query={adress}'
    response = requests.get(url, headers={'Accept': 'application/json'})
    json_test = response.json()
    latitude = json_test['data'][0]['latitude']
    longitude = json_test['data'][0]['longitude']
    return latitude, longitude


def get_quakes(start_time, address):
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query?'

    format = '%Y-%m-%d'
    start_in_date_format = datetime.datetime.strptime(start_time, format)
    end_time_in_data_format = start_in_date_format + datetime.timedelta(days=7)
    end_time = end_time_in_data_format.strftime(format)
    coordinates = get_latitude_longitude_by_city(address)
    latitude = coordinates[0]
    longitude = coordinates[1]

    response = requests.get(url, headers={'Accept': 'application/json'}, params={
        'format': 'geojson',
        'starttime': start_time,
        'endtime': end_time,
        'latitude': latitude,
        'longitude': longitude,
        'maxradiuskm': 2000,
        'minmagnitude': 1
    })
    # print(response.text)
    json_test = response.json()
    database = json_test['features']
    quake_list = []
    for quake in database:
        place = quake['properties']['place']
        mag = quake['properties']['mag']
        time = quake['properties']['time']
        date = datetime.datetime.fromtimestamp(int(time)/1000).strftime('%Y-%m-%d %H:%M')
        quake_list.append((place, mag, date))
        # print(f'Place: {place}. Magnitude: {mag}, date : {date}')

    return sorted(quake_list, key=lambda t: t[2])


