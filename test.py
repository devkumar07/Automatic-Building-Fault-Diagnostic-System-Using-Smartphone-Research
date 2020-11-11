import requests, json
import time

starttime = time.time()
api_key = "ae13574a1f19a995ed53b8d8dd950cf3"
  
# base_url variable to store url 
base_url = "http://api.openweathermap.org/data/2.5/weather?"
  
# Give city name 
city_name = 'San Jose'
  
# complete_url variable to store 
# complete url address 
complete_url = base_url + "appid=" + api_key + "&q=" + city_name +"&units=metric" 
i = 0
while True and i < 5:
    # get method of requests module 
    # return response object 
    i = i + 1
    response = requests.get(complete_url) 
    
    # json method of response object  
    # convert json format data into 
    # python format data 
    x = response.json() 
    
    # Now x contains list of nested dictionaries 
    # Check the value of "cod" key is equal to 
    # "404", means city is found otherwise, 
    # city is not found 
    if x["cod"] != "404": 
    
        # store the value of "main" 
        # key in variable y 
        y = x["main"] 
    
        # store the value corresponding 
        # to the "temp" key of y 
        current_temperature = y["temp"] 

        print('temp:',str(current_temperature))
    
    else: 
        print(" City Not Found ") 
    time.sleep(10.0 - ((time.time() - starttime) % 10.0))