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
import cairosvg

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

#returns png binary representation of a pygal chart
def chart_to_blob(pygal_chart):
    return cairosvg.svg2png(bytestring=pygal_chart.render(), dpi=300)

