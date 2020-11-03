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

def preprocess_sensor_data(data,area):
    processed = []
    for i in range(0, len(data)):
        processed.append(float(area)*data['Speed'][i])
    data['air_flow'] = processed
    return data

def model(data, start_time_train, stop_time_train, start_time_test, stop_time_test):
    
    #data = pd.read_csv('result.csv', parse_dates=['time'], index_col=['time'])
    #data = pd.read_csv(file_name, parse_dates=['time'], index_col=['time'])
    
    train_data = data.loc[start_time_train : stop_time_train]

    test_data = data.loc[start_time_test : stop_time_test]

    x = data[['supply_temp', 'air_flow','outdoor_temp','occupancy']]
    y = data[['zone_temp']]

    x_test = train_data[['supply_temp', 'air_flow','outdoor_temp', 'occupancy']]
    y_test = test_data[['zone_temp']]

    regressor = SVR()
    model = regressor.fit(x, y)
    y_pred = model.predict(x_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    print(rmse)
    print('y_test: ',y_test.zone_temp.values)
    print('y_pred: ',y_pred)
    return y_pred


