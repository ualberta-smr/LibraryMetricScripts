'''
This is a common utiities file for functions that are included in both  GitHub_Phase1.py and GitHub_Phase2.py for the popularity metric. 
'''

import time
import datetime
import json
import pickle
import base64
import sys
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

#This is a sleep function so pause the script since GitHub does not allow frequent calls.
def go_to_sleep (msg, time_of_sleep):
  
  time_stamp = time.time()
  start_date = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')   
  error_msg = "....    " + msg + str(time_of_sleep) + " seconds, Sleeping @ " + start_date
  print (error_msg) 
  
  time.sleep(time_of_sleep)  #actual Sleep
  
  time_stamp = time.time()  
  start_date = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S') 
  error_msg = "....    " + "Woke up @ " + start_date
  print (error_msg) 

#Reads the config file data into dict.
def read_config_file():
    dictKeys = {}
    with open('scripts/Config.json', 'r') as myfile:
        dictKeys = json.loads(myfile.read(),strict=False)
    return dictKeys 

#returns binary representation of a pkl image
def pkl_to_blob(file_name):

    pkl_file = open("scripts/" + file_name + ".pkl", "rb")

    img_data = pickle.load(pkl_file)

    img_data = img_data.split(",")

    value = base64.b64decode(img_data[1])

    pkl_file.close()

    #return value
    pkl_file.close()

    with open(file_name + ".svg", "wb") as file:
         file.write(value)

    drawing = svg2rlg(file_name + ".svg")    

    renderPM.drawToFile(drawing, file_name + ".png", fmt="PNG")

    with open(file_name + ".png", "rb") as image:
      content = image.read()

    return bytearray(content)


