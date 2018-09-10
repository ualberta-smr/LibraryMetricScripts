#Description: 
# - Extracts the dates of the last 5 questions posted on Stack Overflow with the given tag of a library.
#Requirements: 
# - You will need to change the value of user_api_key to your Stack Exchange API token
# - You will need to install PyStackExchange.
#Input:
# File SharedFiles/librarytags.txt with the Stackoverflow tags of the libraries.
#Output:
# A pickle file called lastdiscussedSO.pkl, which will contain a dictionary where the key is a library tag, and the value of each key is
#a string containing dates in format %m/%d/%Y separated by semicolons:
#[library tag] => %m/%d/%Y;%m/%d/%Y;%m/%d/%Y;%m/%d/%Y;%m/%d/%Y
#How to run: 
# - Just run the script.

import os
import pickle

user_api_key = "your stack exchange user API key here"

import stackexchange
so = stackexchange.Site(stackexchange.StackOverflow, app_key=user_api_key, impose_throttling=True)
so.be_inclusive()

def loadLastDiscussedSOData():
  data = {}
  filename = 'lastdiscussedSO.pkl'
  if os.path.isfile(filename):
    with open(filename, 'rb') as input:
      try:
        print("Loading data")
        data = pickle.load(input)
      except EOFError:
        print("Failed to load pickle file")
        data = {}
  return data

def saveData(data):
  with open('lastdiscussedSO.pkl', 'wb') as output:
    pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def getLastDiscussedDates():
  data = loadLastDiscussedSOData()

  rel_path = "SharedFiles/librarytags.txt"
  if os.path.isdir('SharedFiles'):
    file_path = rel_path
  else:
    file_path = os.path.join(os.pardir, rel_path)
    
  with open(file_path) as f:
    tags = f.readlines()
  tags = [x.strip() for x in tags]

  for tag in tags:
    questions = so.questions(sort='creation', order='DESC', tagged=[tag,'java'])

    dates_string = ""
    for i in range(0, 10):
      if questions == None or i >= len(questions):
        break
      if i > 0:
        dates_string += ';'
      dates_string += questions[i].creation_date.strftime('%m/%d/%Y')

    if len(dates_string) == 0:
      data[tag] = None
    else:
      data[tag] = dates_string
    saveData(data)

if __name__ == "__main__":
  getLastDiscussedDates()
