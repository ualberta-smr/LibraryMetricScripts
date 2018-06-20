import os
import pickle

user_api_key = "kIqL02JIr5xqq99D*ckRiA(("

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
  #print(data)

  with open("librarytags.txt") as f:
    tags = f.readlines()
  tags = [x.strip() for x in tags]

  for tag in tags:
    if tag in data:
      continue
    questions = so.questions(sort='creation', order='DESC', tagged=[tag,'java'])

    if len(questions) > 0:
        q = questions[0]
        data[tag] = q.creation_date
        saveData(data)
    else:
        data[tag] = None
        saveData(data)

if __name__ == "__main__":
  getLastDiscussedDates()