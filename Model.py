import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from sklearn import linear_model
import statsmodels.api as sm
from sklearn.metrics import r2_score
from sklearn.svm import SVR
from statsmodels.tools.eval_measures import rmse
from sklearn.metrics import r2_score, mean_squared_error
import boto3
from sklearn.model_selection import train_test_split
import time
import requests, json
from sklearn import preprocessing
from scipy.spatial import distance

def apiWeatherCall(time_steps):
    i = 0
    starttime = time.time()
    api_key = "ae13574a1f19a995ed53b8d8dd950cf3"
    
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    city_name = 'San Jose'

    temp = []
    time_vec = []

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name +"&units=metric" 
    i = 0
    while True and i < int(time_steps):
        i = i + 1
        response = requests.get(complete_url) 
        
        x = response.json() 

        if x["cod"] != "404": 

            y = x["main"] 

            current_temperature = y["temp"] 
            now = datetime.now()
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            time_vec.append(dt_string)
            temp.append(str(current_temperature))
            print('time:',str(dt_string))
            print('temp:',str(current_temperature))
        
        else: 
            print(" City Not Found ") 
        time.sleep(1.0 - ((time.time() - starttime) % 1.0))
    d = {"time":time_vec,'temp':temp}
    df = pd.DataFrame(d)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df.to_csv ('export_temp.csv', index = True, header=True) 
    return pd.read_csv('export_temp_final.csv', parse_dates=['time'], index_col=['time'])

def preprocess_sensor_data(data,area,outside_temp, start_time, stop_time):
    processed = []
    for i in range(0, len(data)):
        processed.append(float(area)*data['Speed'][i])
    filtered_data = outside_temp.loc[str(start_time):str(stop_time)]
    filtered_outside_temp = filtered_data['temp']
    data['air_flow'] = processed
    data['outdoor_temp'] = filtered_outside_temp
    return data

def model(data):
    
    #data = pd.read_csv('result.csv', parse_dates=['time'], index_col=['time'])
    #data = pd.read_csv(file_name, parse_dates=['time'], index_col=['time'])
    
    #train_data = data.loc[start_time_train : stop_time_train]

    #test_data = data.loc[start_time_test : stop_time_test]

    x = data[['supply_temp', 'air_flow','outdoor_temp','occupancy']]
    y = data[['zone_temp']]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, shuffle = False)
    #x_test = train_data[['supply_temp', 'air_flow','outdoor_temp', 'occupancy']]
    #y_test = test_data[['zone_temp']]

    regressor = SVR()
    model = regressor.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    print(rmse)
    print('y_test: ',y_test.zone_temp.values)
    print('y_pred: ',y_pred)
    return rmse, y_pred

def compute_jensen_shannon_divergence(vec1, vec2):

    p = np.histogram(vec1)[0] / len(vec1)    
    q = np.histogram(vec2)[0] / len(vec2)
    print(p)
    print(q)
    score = distance.jensenshannon(p, q) ** 2
    return score





