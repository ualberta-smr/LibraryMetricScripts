#This script will extract the Performance metrics 
#Requirements: Need the list of performance keywords (performancewords.txt) and performance dataset (performancedataset.xlsx)
#              Needs the list of repositories (repositories.txt)
#              You will need to install Pygithub, and some other libraries (nltk, etc).
#HOW TO USE: Just run the script.

import re
import nltk
import sys
import getpass

from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from github import Github, Repository
import string

list_descriptions = []
list_labels = []

stemmer = PorterStemmer()

def stem_words(tokens):
  stemmed = []
  for item in tokens:
    stemmed.append(stemmer.stem(item))
  return stemmed

def tokenize(text):
  lowers = text.lower()
  no_punctuation = lowers.translate(str.maketrans('','',string.punctuation))
  text = no_punctuation
  tokens = nltk.word_tokenize(text)
  stems = stem_words(tokens)
  return stems

def read_dataset():
  from openpyxl import load_workbook
  wb = load_workbook('performancedataset.xlsx')

  for sheet in wb:
    for i in range(1, len(sheet['B'])):
      #Get the value from the classification column
      classification = sheet[('B' + str(i))].value
      #Get the value from the summary column
      summary = sheet[('A'+str(i))].value.encode('utf-8').decode('utf-8')
      lowers = summary.lower()
      no_punctuation = lowers.translate(str.maketrans('','',string.punctuation))
      list_descriptions.append(no_punctuation)
      if classification == 1: #1 stands for Performance issue
        list_labels.append(1)
      else:
        list_labels.append(0)

def useTFIDF():
  tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english', min_df=.01)
  return tfidf

def useCounts():
  cv = CountVectorizer(tokenizer=tokenize, stop_words='english', min_df=100)
  return cv

def crossValidate(classifier, counts, list_labels):
  from sklearn.model_selection import StratifiedKFold, cross_val_score

  print("Performing cross validation...")
  k_fold = StratifiedKFold(n_splits=10, shuffle=True, random_state=1)
  scores_precision = cross_val_score(classifier, counts, list_labels, cv=k_fold, scoring='precision')
  print("Precision: %0.2f (+/- %0.2f)" % (scores_precision.mean(), scores_precision.std() * 2))
  scores_recall = cross_val_score(classifier, counts, list_labels, cv=k_fold, scoring='recall')
  print("Recall: %0.2f (+/- %0.2f)" % (scores_recall.mean(), scores_recall.std() * 2))
  scores_accuracy = cross_val_score(classifier, counts, list_labels, cv=k_fold, scoring='accuracy')
  print("Accuracy: %0.2f (+/- %0.2f)\n" % (scores_accuracy.mean(), scores_accuracy.std() * 2))

def main():
  read_dataset()
  vectorizer = useTFIDF()
  counts = vectorizer.fit_transform(list_descriptions)
  classifier = MultinomialNB()
  classifier.fit(counts, list_labels)
  #crossValidate(classifier, counts, list_labels)
  
  with open("performancewords.txt") as f:
    words = f.readlines()
  words = [x.strip() for x in words]
  
  with open("repositories.txt") as f:
    repositories = f.readlines()
  repositories = [x.strip() for x in repositories]
  
  username = input("Enter Github username: ")
  password = getpass.getpass("Enter your password: ")
  g = Github(username, password)

  for i in range(0, len(repositories)):
    r = g.get_repo(repositories[i])
    total_issues = 0
    total_performance = 0
    total_keyword_issues = 0

    for issue in r.get_issues(state="all"):
      if issue.pull_request != None:
        continue
      total_issues+=1
      text = issue.title
      keywordFound = False
      text = text.lower()
      for word in words:
        if text.find(word) != -1:
          keywordFound = True
      if keywordFound == False:
        continue
      input_counts = vectorizer.transform([text])
      prediction = classifier.predict(input_counts)
      total_keyword_issues += 1
      #If the prediction is performance-related
      if prediction[0] == 1:
        total_performance+=1

    if total_issues == 0:
      print("%s - Performance:%.2f" % (repositories[i], 0.00))
    else:
      print("%s - Performance: %.2f" % (repositories[i], total_performance/total_issues*100))

if __name__ == "__main__":
  main()