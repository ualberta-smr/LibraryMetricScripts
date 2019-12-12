'''
This is a common utiities file for functions that are included in both  GitHub_Phase1.py and GitHub_Phase2.py for the popularity metric. 
'''

import time
import datetime
import json

#This is a sleep function so pause the script since GitHub does not allow frequent calls.
def go_to_sleep (msg, time_of_sleep):
  
  time_stamp = time.time()
  start_date = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')   
  error_msg = "....    " + msg + str(time_of_sleep) + " seconds, Sleeping @ " + start_date
  print (error_msg) 
  
  time.sleep(time_of_sleep)  #actual Sleep
  
  time_stamp = time.time()  
  start_date = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S') 
  error_msg = "....    " + "Waked up @ " + start_date
  print (error_msg) 

#Reads the ini file data into dict.
def read_ini_file():
    dictKeys = {}
    with open('GitHubSearch.json', 'r') as myfile:
        dictKeys = json.loads(myfile.read())
    return dictKeys 