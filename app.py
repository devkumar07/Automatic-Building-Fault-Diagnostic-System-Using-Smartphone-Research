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
      print(time_steps)
      global outside_temp
      outside_temp = apiWeatherCall(time_steps)
   return json.dumps({"error":200, "msg":"Outside tempreature recorded!"})

@app.route('/predict', methods = ['GET', 'POST'])
def predict():
   s3 = boto3.client('s3')
   if request.method == 'POST':
      app_data = request.json
      #Download file from AWS S3
      s3.download_file('faultdetect','test_data.csv', 'sensor_data.csv')
      s3.download_file('faultdetect','zone_temp.csv', 'zone_temp.csv')

      #Loading data from Testo sensor and Goove sensor
      data = pd.read_csv('sensor_data.csv', parse_dates=['time'], index_col=['time'])
      data1 = pd.read_csv('data/result.csv', parse_dates=['time'], index_col=['time'])
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

      print(start_time)
      print('-----------')
      print(outside_temp)
      #Filtering data and converting it into 1 min interval
      data = data.loc[str(start_time):str(end_time)]
      data1 = data1.loc['2017-11-14 15:20:00':'2017-11-14 16:20:00']
      data = data.asfreq(freq='300S')
      zone_data.set_index('time', inplace=True)
      zone_data = zone_data.asfreq(freq='300S')
      filtered_outside_temp = outside_temp.loc[str(start_time):str(end_time)]
      filtered_outside_temp = filtered_outside_temp.asfreq(freq='300S')


      #Loading zone temperature and outdoor temperature to main dataframe
      data['zone_temp'] = zone_data.loc[str(start_time):str(end_time)]['temp']
      data['outdoor_temp'] = outside_temp.loc[str(start_time):str(end_time)]['temp']

      #Preprocessing data to get air_flow
      data = preprocess_sensor_data(data, app_data['area'], outside_temp,start_time,end_time)
      print(data)
      print(data1)
      
      #Calling ML model
      error_rate, vec1 = model(data)
      error_rate1, vec2 = model(data1)
      score = compute_jensen_shannon_divergence(vec1, vec2)
      if error_rate > 2.0 or error_rate1 > 2.0:
         return json.dumps({"error": 200, "msg":"Insufficient data"})
      else:
         return json.dumps({"error": 200, "msg": 'Divergence: '+str(score)})
   return json.dumps({"error":"COULD NOT RECIEVE POST REQUEST"})
if __name__ == '__main__':
    app.run()
    