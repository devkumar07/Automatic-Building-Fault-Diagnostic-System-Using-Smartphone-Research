import json 
from Model import *
from flask import Flask, render_template, jsonify, request
import csv
import pandas as pd 
import boto3

app = Flask(__name__)

@app.route('/predict', methods = ['GET', 'POST'])
def predict():
   s3 = boto3.client('s3')
   s3.download_file('faultdetect','actual_result.csv', 'sensor_data.csv')
   if request.method == 'POST':
      app_data = request.json
      data = pd.read_csv('sensor_data.csv', parse_dates=['time'], index_col=['time'])
      data = preprocess_sensor_data(data, app_data['area'])
      print(data.head())
   #result = model('client_actual_result.csv')
   return json.dumps({"result":"Success!!!!!"})
if __name__ == '__main__':
    app.run()
    