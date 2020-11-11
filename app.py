import json 
from Model import *
from flask import Flask, render_template, jsonify, request
import csv
import pandas as pd 
import boto3

app = Flask(__name__)
outside_temp = []
@app.route('/getOutsideTemp', methods = ['GET', 'POST'])
def getOutsideTemp():
   if request.method == 'POST':
      app_data = request.post
      time_steps = app_data['steps']
      outside_temp = apiWeatherCall(time_steps)

   return json.dumps({"msg":"SUCCESS!!!"})

@app.route('/predict', methods = ['GET', 'POST'])
def predict():
   s3 = boto3.client('s3')
   s3.download_file('faultdetect','sensor_data.csv', 'sensor_data.csv')
   if request.method == 'POST':
      app_data = request.json
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
    