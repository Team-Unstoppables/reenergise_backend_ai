import os
import numpy as np
import requests
import datetime


SR = {'white': 1, 'black': 0, 'red': 0.8, 'green': 0.6, 'blue': 0.4, 'yellow': 0.7, 'orange': 0.9, 'purple': 0.5}
epsilon = {'concrete': 0.5, 'glass': 0.9, 'aluminum': 0.8, 'wood': 0.6, 'plastic': 0.7}

def WeatherData(lat, lon):
    lat = str(lat)
    lon = str(lon)
    api_id = os.environ.get('WEATHER')
    url = "https://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&appid=" + api_id
    response = requests.get(url)
    data = response.json()
    return data['main']['temp'], data['main']['feels_like'] # feels like, room temp and other is air temp

def SolarIrradiance(lat, lon, area):
    lat = str(lat)
    lon = str(lon)
    api_id = os.environ.get('SOLAR_API')
    url = "https://developer.nrel.gov/api/solar/solar_resource/v1.json?api_key=" + api_id + "&lat=" + lat + "&lon=" + lon
    response = requests.get(url)
    data = response.json()
    # get current month from computer date
    month = datetime.datetime.now().month
    mDict = {1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun', 7: 'jul', 8: 'aug', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dec'}
    if data['outputs']['avg_dni'] != 'no data': 
        return data['outputs']['avg_dni']['annual'] * area, data['outputs']['avg_dni']['monthly'][mDict[month]] * area
    
    else:
        return 4.05 * area, 6.53 * area
    
def RoofTemperature(SR, I, T_air, h_conv):
    T_surf = ((1-SR) *I + h_conv*T_air )/h_conv
    T_surf = T_surf - 273.15
    return T_surf

def RoomTemperature(T_surf, T_room_ideal):
    c_air = 1005
    c_concrete = 880
    factor = c_concrete/c_air
    T_room = (T_room_ideal + factor *(T_surf+273.15)) / (1+factor)
    return T_room - 273.15

def ac_energy(T_room, T_ac, area):
    c_air = 1005
    density_air = 1.2
    mass = density_air * area * 3 # 3m room height
    T_room = T_room + 273.15
    T_ac = float(T_ac) + 273.15
    energy = mass * (T_room - T_ac) * 0.001
    #energy = 0.00094781712 * energy
    return energy

AC_Cooling_Chart = {'split': {'model': {'1': '984', '1.5': '1490', '2': '1732'}}
                    , 'window': {'model': {'1': '1250', '2': '1745'}}} # all values in Watts/hr = Joules/sec


def main(lat, lon, area, ac_temp, cost, ac_type='split', model='1.5'):
    # get weather data
    T_air, T_room_ideal = WeatherData(lat, lon)
    # get solar irradiance
    I, I_month = SolarIrradiance(lat, lon, area)
    # get roof temperature for white roof and black roof
    T_surf_white = RoofTemperature(SR['white'], I, T_air, 10)
    T_surf_black = RoofTemperature(SR['black'], I, T_air, 10)
    # get room temperature for white roof and black roof
    T_room_white = RoomTemperature(T_surf_white, T_room_ideal)
    T_room_black = RoomTemperature(T_surf_black, T_room_ideal)

    # get energy consumption for white roof and black roof
    energy_white = ac_energy(T_room_white, ac_temp, area)
    energy_black = ac_energy(T_room_black, ac_temp, area)
    # convert to units
    print(ac_type, model)
    energy_white = energy_white / (float(AC_Cooling_Chart[ac_type]['model'][model]) / 1000)
    energy_black = energy_black / (float(AC_Cooling_Chart[ac_type]['model'][model]) / 1000)

    cost_white = energy_white * cost
    cost_black = energy_black * cost
    # get savings
    savings = energy_black- energy_white
    savings = savings * (float(AC_Cooling_Chart[ac_type]['model'][model]) / 1000)
    savings = savings * cost

    saving_dict = {'Cost Saving': savings, 'cost_white': cost_white, 'cost_black': cost_black, 'energy_white': energy_white, 'energy_black': energy_black, 'T_surf_white': T_surf_white, 'T_surf_black': T_surf_black, 'T_room_white': T_room_white, 'T_room_black': T_room_black}
    return saving_dict

    
    




if __name__ == "__main__":
    lat = -37.7749
    lon = 122.4194
    area = 100
    ac_temp = 5
    ac_type = 'split'
    model = '1.5'
    cost = 0.15
    print(main(lat, lon, area, ac_temp, cost, ac_type, model))
