import json 
from Model import *
from flask import Flask, render_template, jsonify, request
import csv
import pandas as pd 
import boto3

app = Flask(__name__)
outside_temp = pd.DataFrame()
@app.route('/getOutsideTemp', methods = ['GET', 'POST'])
def getOutsideTemp():
   if request.method == 'POST':
      app_data = request.json
      time_steps = app_data['steps']
      global outside_temp
      outside_temp = apiWeatherCall(time_steps)
   return json.dumps({"error":200, "msg":"Outside tempreature recorded!"})

@app.route('/predict', methods = ['GET', 'POST'])
def predict():
   s3 = boto3.client('s3')
   if request.method == 'POST':
      app_data = request.json
      #Download file from AWS S3
      s3.download_file('faultdetect',app_data['file_name']+'.csv', 'sensor_data.csv')

      #Loading data fro Testo sensor and Goove sensor
      data = pd.read_csv('sensor_data.csv', parse_dates=['time'], index_col=['time'])
      zone_data = pd.read_csv('zone_temp.csv')

      #Fetching start and stop times
      zone_data['time'] = pd.to_datetime(zone_data['time'])
      start_time = zone_data['time'][0]
      end_time = zone_data['time'][len(zone_data['time'])-1]

      """
      print(data)
      print(zone_data)
      print(outside_temp)
      print(start_time)
      """
      #Filtering data and converting it into 1 min interval
      data = data.loc[str(start_time):str(end_time)]
      data = data.asfreq(freq='60S')
      zone_data.set_index('time', inplace=True)

      #Loading zonet temperature and outdoor temperature to main dataframe
      data['zone_temp'] = zone_data.loc[str(start_time):str(end_time)]['temp']
      data['outdoor_temp'] = outside_temp.loc[str(start_time):str(end_time)]['temp']

      #Preprocessing data to get air_flow
      data = preprocess_sensor_data(data, app_data['area'], outside_temp,start_time,end_time)
      print(data)
      
      #Calling ML model
      error_rate = model(data)
      print(error_rate)
      if error_rate > 2.0:
         return json.dumps({"error": 200, "msg":"Insufficient data"})
      else:
         return json.dumps({"error": 200, "msg":"Sufficient data"})
   return json.dumps({"REQUEST ERROR":"COULD NOT RECIEVE POST REQUEST"})
if __name__ == '__main__':
    app.run()
    