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
      outside_temp = apiWeatherCall(time_steps)
      print(outside_temp)
   return json.dumps({"error":200, "msg":"Outside tempreature recorded!"})

@app.route('/predict', methods = ['GET', 'POST'])
def predict():
   s3 = boto3.client('s3')
   if request.method == 'POST':
      app_data = request.json
      s3.download_file('faultdetect',app_data['file_name']+'.csv', 'sensor_data.csv')
      data = pd.read_csv('sensor_data.csv', parse_dates=['time'], index_col=['time'])
      data = preprocess_sensor_data(data, app_data['area'])
      error_rate = model(data)
      print(error_rate)
      if error_rate > 2.0:
         return json.dumps({"error":error_rate, "msg":"Insufficient data"})
      else:
         return json.dumps({"error":error_rate, "msg":"Sufficient data"})
   return json.dumps({"REQUEST ERROR":"COULD NOT RECIEVE POST REQUEST"})
if __name__ == '__main__':
    app.run()
    