#Description: 
# - Extracts the dates of the last 5 questions posted on Stack Overflow with the given tag of a library.
#Requirements: 
# - You will need to change the value of user_api_key to your Stack Exchange API token
# - You will need to install PyStackExchange.
#Input:
# File scripts/LibraryData.json which contains the Stackoverflow tags of the libraries.
#Output:
# A pickle file called lastdiscussedSO.pkl, which will contain a dictionary where the key is a library tag, and the value of each key is
#a string containing dates in format %m/%d/%Y separated by semicolons:
#[library tag] => %m/%d/%Y;%m/%d/%Y;%m/%d/%Y;%m/%d/%Y;%m/%d/%Y
#How to run: 
# - Just run the script.

import os
import pickle
import json
import stackexchange


from scripts.SharedFiles.utility_tool import read_json_file
from scripts.CommonUtilities import Common_Utilities

from librarycomparison.models import Library


def loadLastDiscussedSOData():
  data = {}
  filename = 'scripts/LastDiscussedOnStackOverflow/lastdiscussedSO.pkl'
  if os.path.isfile(filename):
    with open(filename, 'rb') as input:
      try:
        data = pickle.load(input)
      except EOFError:
        print("Failed to load pickle file")
        data = {}
  return data

def saveData(data):
  with open('scripts/LastDiscussedOnStackOverflow/lastdiscussedSO.pkl', 'wb') as output:
    pickle.dump(data, output, pickle.DEFAULT_PROTOCOL)

def getLastDiscussedDates():

  config_dict = Common_Utilities.read_config_file() # read all config data 
  user_api_key = config_dict["SO_TOKEN"]


  so = stackexchange.Site(stackexchange.StackOverflow, app_key=user_api_key, impose_throttling=True)
  so.be_inclusive()

  
  data = loadLastDiscussedSOData()

  libraries = Library.objects.all()

  for library in libraries:
    tag = library.so_tag
    if tag != "":
      questions = so.questions(sort='creation', order='DESC', tagged=[tag,'java'])

      dates_string = ""
      for i in range(0, 10):
        if questions == None or i >= len(questions):
          break
        if i > 0:
          dates_string += ';'
        dates_string += questions[i].creation_date.strftime("%m/%d/%Y, %H:%M:%S") + " UTC"

      if len(dates_string) == 0:
        data[tag] = None
      else:
        data[tag] = dates_string
      saveData(data)

if __name__ == "__main__":
  getLastDiscussedDates()
