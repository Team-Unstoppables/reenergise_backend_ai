import os
import numpy as np
import requests
import datetime

SR = {'white': 0.71, 'black': 0.05, 'red': 0.40, 'grey': 0.38, 'green': 0.17, 'brown': 0.11}
epsilon = {'concrete': 0.5, 'glass': 0.9, 'aluminum': 0.8, 'wood': 0.6, 'plastic': 0.7}

def WeatherDailyData(lat, lon):
    lat = str(lat)
    lon = str(lon)
    api_id = os.environ.get('WEATHER')
    url = "https://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&appid=" + api_id
    response = requests.get(url)
    data = response.json()
    #print(data['main']['temp'] - 273.15, data['main']['feels_like'] - 273.15)
    return data['main']['temp'], data['main']['feels_like'] # feels like, room temp and other is air temp

def MonthlyWeather(lat, lon, mon):
    lat = str(lat)
    lon = str(lon)
    place = requests.get("https://api.opencagedata.com/geocode/v1/json?q=" + lat + "+" + lon + "&key=1cdb447dbbe543baa73a53e40e6e26d0")
    place = place.json()
    print(place)
    place = place['results'][0]['components']['state']
    # https://api.worldweatheronline.com/premium/v1/weather.ashx?key=c3debe0db4e84063adf184530222311&q=London&fx=no&cc=no&mca=yes&format=json
    api_id = "c3debe0db4e84063adf184530222311"
    url = "https://api.worldweatheronline.com/premium/v1/weather.ashx?key=c3debe0db4e84063adf184530222311&q="+place+"&fx=no&cc=no&mca=yes&format=json"
    #print(url)
    response = requests.get(url)
    data = response.json()
    # get average temperature for the specified month
    temp = data["data"]["ClimateAverages"][0]['month'][mon-1]['absMaxTemp']
    return temp

def AnnualData(lat, lon):
    temp_list = []
    for i in range(1, 13):
        temp = MonthlyWeather(lat, lon, i)
        temp_list.append(temp)
    sumVar = 0
    for i in temp_list:
        sumVar = sumVar + float(i)
    return sumVar/12
    
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
    T_air, T_room_ideal = WeatherDailyData(lat, lon)
    # get solar irradiance
    I, I_month = SolarIrradiance(lat, lon, area)
    # get for all colors in SR
    T_surf = {}
    for color in SR:
        T_surf[color] = RoofTemperature(SR[color], I, T_air, 5)
    # get for all materials in epsilon  for all T_surf
    T_room = {}
    for color in T_surf:
        T_room[color] = RoomTemperature(T_surf[color], T_room_ideal)
    
    # energy consumption for all colors
    energy = {}
    for color in T_room:
        energy[color] = ac_energy(T_room[color], ac_temp, area)
    
    energy_color = {}
    for color in energy:
        energy_color[color] = energy[color] / (float(AC_Cooling_Chart[ac_type]['model'][model]) / 1000)

    # cost for each color
    cost_color = {}
    for color in energy_color:
        cost_color[color] = energy_color[color] * cost
    
    # savings corresponding to all colors mapping cost based on each color to one another
    savings = {}
    for color in cost_color:
        savings[color] = {}
        for color2 in cost_color:
            savings[color][color2] = cost_color[color] - cost_color[color2]
            savings[color][color2] = savings[color][color2] * (float(AC_Cooling_Chart[ac_type]['model'][model]) / 1000)
            # multiply with cost
            savings[color][color2] = savings[color][color2] * cost
    # get current month number
    month = datetime.datetime.now().month
    T_air_month = float(MonthlyWeather(lat, lon, month))
    T_room_ideal_month = T_air_month - 5   
    I_month, I_month_month = SolarIrradiance(lat, lon, area)
    T_surf_month = {}
    for color in SR:
        T_surf_month[color] = RoofTemperature(SR[color], I_month, T_air_month, 5)
    T_room_month = {}
    for color in T_surf_month:
        T_room_month[color] = RoomTemperature(T_surf_month[color], T_room_ideal_month)
    energy_month = {}
    for color in T_room_month:
        energy_month[color] = ac_energy(T_room_month[color], ac_temp, area)
    energy_color_month = {}
    for color in energy_month:
        energy_color_month[color] = energy_month[color] / (float(AC_Cooling_Chart[ac_type]['model'][model]) / 1000)
    cost_color_month = {}
    for color in energy_color_month:
        cost_color_month[color] = energy_color_month[color] * cost
    savings_month = {}
    for color in cost_color_month:
        savings_month[color] = {}
        for color2 in cost_color_month:
            savings_month[color][color2] = cost_color_month[color] - cost_color_month[color2]
            savings_month[color][color2] = savings_month[color][color2] * (float(AC_Cooling_Chart[ac_type]['model'][model]) / 1000)
            # multiply with cost
            savings_month[color][color2] = savings_month[color][color2] * cost * 10 * 30
    
    T_air_year = float(AnnualData(lat, lon))
    T_room_ideal_year = T_air_year - 5
    I_year, I_month_year = SolarIrradiance(lat, lon, area)
    T_surf_year = {}
    for color in SR:
        T_surf_year[color] = RoofTemperature(SR[color], I_year, T_air_year, 5)
    T_room_year = {}
    for color in T_surf_year:
        T_room_year[color] = RoomTemperature(T_surf_year[color], T_room_ideal_year)
    energy_year = {}
    for color in T_room_year:
        energy_year[color] = ac_energy(T_room_year[color], ac_temp, area)
    energy_color_year = {}
    for color in energy_year:
        energy_color_year[color] = energy_year[color] / (float(AC_Cooling_Chart[ac_type]['model'][model]) / 1000)
    cost_color_year = {}
    for color in energy_color_year:
        cost_color_year[color] = energy_color_year[color] * cost
    savings_year = {}
    for color in cost_color_year:
        savings_year[color] = {}
        for color2 in cost_color_year:
            savings_year[color][color2] = cost_color_year[color] - cost_color_year[color2]
            savings_year[color][color2] = savings_year[color][color2] * (float(AC_Cooling_Chart[ac_type]['model'][model]) / 1000)
            # multiply with cost
            savings_year[color][color2] = savings_year[color][color2] * cost * 10 * 30 * 12
    
     # save savings, room temp, roof temp, energy consumption, cost for each color in a dictionary
    data = {}
    data['savings'] = savings
    data['room_temp'] = T_room
    data['roof_temp'] = T_surf
    data['energy'] = energy #kwh
    data['cost'] = cost_color #currency
    data['savings_month'] = savings_month
    data['saving_year'] = savings_year
    return data


    
if __name__ == "__main__":
    lat = -27.42
    lon = 153.05381
    area = 100
    ac_temp = 5
    ac_type = 'split'
    model = '1.5'
    cost = 0.15
    data = main(lat, lon, area, ac_temp, cost, ac_type, model)