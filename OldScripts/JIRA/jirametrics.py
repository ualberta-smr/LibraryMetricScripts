#Description:
# - This script will extract the Issue Response Time, Issue Closing Time, Performance, and Security metrics for JIRA libraries
#  The list of libraries can be found in the 'dict' dictionary of this file. 
#Input: 
# - The list of security keywords (securitywords.txt)
# - The performance keywords (performancewords.txt)
# - The security dataset (securitydataset.xlsx)
# - The performance dataset (performancedataset.xlsx)
#Output:
#The following lines will be printed to stdout for each of the libraries in the dict dictionary of this file:
#[library] - Issue Response Time: [average number of days]
#[library] - Issue Closing Time: [average number of days]
#[library] - Security: [percentage of detected security issues in the issue tracking system]
#[library] - Performance [percentage of detected performance issues in the issue tracking system]
#HOW TO USE: Just run the script.
#             To use with another library, add another entry to this dict with its corresponding JIRA issues URL in XML format


import urllib.request
import xml.etree.ElementTree
from datetime import datetime

import re
import nltk

from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from github import Github, Repository
import string

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

def read_dataset(filename):
  from openpyxl import load_workbook
  wb = load_workbook(filename)
  
  list_descriptions = []
  list_labels = []

  for sheet in wb:
    for i in range(1, len(sheet['B'])):
      #Get the value from the classification column
      classification = sheet[('B' + str(i))].value
      #Get the value from the summary column
      summary = sheet[('A'+str(i))].value.encode('utf-8').decode('utf-8')
      lowers = summary.lower()
      no_punctuation = lowers.translate(str.maketrans('','',string.punctuation))
      list_descriptions.append(no_punctuation)
      if classification == 1: #1 stands for Security/Performance issue
        list_labels.append(1)
      else:
        list_labels.append(0)
  return list_descriptions, list_labels

def useTFIDF():
  tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english', min_df=.01)
  return tfidf

def useCounts():
  cv = CountVectorizer(tokenizer=tokenize, stop_words='english', min_df=100)
  return cv

def crossValidate(classifier, counts, list_labels):
  from sklearn.model_selection import StratifiedKFold, cross_val_score

  #print("Performing cross validation...")
  k_fold = StratifiedKFold(n_splits=10, shuffle=True, random_state=1)
  scores_precision = cross_val_score(classifier, counts, list_labels, cv=k_fold, scoring='precision')
  #print("Precision: %0.2f (+/- %0.2f)" % (scores_precision.mean(), scores_precision.std() * 2))
  scores_recall = cross_val_score(classifier, counts, list_labels, cv=k_fold, scoring='recall')
  #print("Recall: %0.2f (+/- %0.2f)" % (scores_recall.mean(), scores_recall.std() * 2))
  scores_accuracy = cross_val_score(classifier, counts, list_labels, cv=k_fold, scoring='accuracy')
  #print("Accuracy: %0.2f (+/- %0.2f)\n" % (scores_accuracy.mean(), scores_accuracy.std() * 2))

dict = {'slf4j': 'https://jira.qos.ch/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+SLF4J+AND+issuetype+%3D+Bug+ORDER+BY+priority+DESC%2C+updated+DESC&tempMax=1000',
        'log4j2' : 'https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+LOG4J2+AND+issuetype+%3D+Bug+ORDER+BY+key+DESC&tempMax=1000&field=summary&field=created&field=reporter&field=resolved&field=comments',
        'logback': 'https://jira.qos.ch/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+LOGBACK+AND+issuetype+%3D+Bug+ORDER+BY+priority+DESC%2C+updated+DESC&tempMax=1000&field=summary&field=reporter&field=created&field=resolved&field=comments',		
        'apache-commons-logging': 'https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+LOGGING+AND+issuetype+%3D+Bug+ORDER+BY+key+DESC&tempMax=1000&field=summary&field=reporter&field=created&field=resolved&field=comments',
        'apache-commons-lang': 'https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+LANG+AND+issuetype+%3D+Bug+ORDER+BY+key+DESC&tempMax=1000&field=summary&field=reporter&field=created&field=resolved&field=comments',
        'apache-commons-crypto': 'https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+CRYPTO+AND+issuetype+%3D+Bug+ORDER+BY+key+DESC&tempMax=1000&field=summary&field=reporter&field=created&field=resolved&field=comments',
        'derby': 'https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+DERBY+AND+issuetype+%3D+Bug+ORDER+BY+key+DESC&tempMax=1000&field=summary&field=reporter&field=created&field=resolved&field=comments',
        'shiro': 'https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+SHIRO+AND+issuetype+%3D+Bug+ORDER+BY+key+DESC&tempMax=1000&field=summary&field=reporter&field=created&field=resolved&field=comments',
        'hibernate-orm': 'https://hibernate.atlassian.net/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+HHH+AND+issuetype+%3D+Bug+order+by+created+DESC&tempMax=1000&field=summary&field=reporter&field=created&field=resolved&field=comments',
		'xercesj': 'https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project+%3D+XERCESJ+AND+issuetype+%3D+Bug+ORDER+BY+priority+DESC%2C+updated+DESC&tempMax=1000&field=summary&field=reporter&field=created&field=resolved&field=comments'}

def createClassifierModel(dataset):
  list_descriptions, list_labels = read_dataset(dataset)
  vectorizer = useTFIDF()
  counts = vectorizer.fit_transform(list_descriptions)
  classifier = MultinomialNB()
  classifier.fit(counts, list_labels)
  crossValidate(classifier, counts, list_labels)
  return vectorizer, classifier

def main():
  security_vectorizer, security_classifier = createClassifierModel('securitydataset.xlsx')
  performance_vectorizer, performance_classifier = createClassifierModel('performancedataset.xlsx')
  
  with open("securitywords.txt") as f:
    security_words = f.readlines()
  security_words = [x.strip() for x in security_words]
  
  with open("performancewords.txt") as f:
    performance_words = f.readlines()
  performance_words = [x.strip() for x in performance_words]
  
  for library, url in dict.items():
    xmlString = urllib.request.urlopen(url).read().decode('utf-8')
    root = xml.etree.ElementTree.fromstring(xmlString)
    channel = root.find('channel')

    closed_issues = 0
    commented_issues = 0
    total_closing_time = 0
    total_response_time = 0
    security_issues = 0
    performance_issues = 0
    total_issues = 0

    for issue in channel.findall('item'):
      #performance/security
      total_issues += 1
      performance_keyword_found = False
      security_keyword_found = False
      summary_text = issue.find('summary').text
      summary_text = summary_text.lower()
      for word in performance_words:
        if summary_text.find(word) != -1:
          performance_keyword_found = True
          break
      if performance_keyword_found == True:
        input_counts = performance_vectorizer.transform([summary_text])
        prediction = performance_classifier.predict(input_counts)
        performance_issues += prediction[0] == 1

      for word in security_words:
        if summary_text.find(word) != -1:
          security_keyword_found = True
          break
      if security_keyword_found == True:
        input_counts = security_vectorizer.transform([summary_text])
        prediction = security_classifier.predict(input_counts)
        security_issues += prediction[0] == 1

      #response time/closing time
      created_date = datetime.strptime(issue.find('created').text, '%a, %d %b %Y %H:%M:%S %z')
      #response time
      resolved = issue.find('resolved')
      if resolved != None:
        resolved_date = datetime.strptime(resolved.text, '%a, %d %b %Y %H:%M:%S %z')
        closed_issues += 1
        total_closing_time += int((resolved_date - created_date).total_seconds())

      issueReporter = issue.find('reporter').get('username')
      if issue.find('comments') != None:
        for comment in issue.find('comments'):
          if comment == None or comment.get('author') == issueReporter:
            continue
          first_comment_date = datetime.strptime(comment.get('created'), '%a, %d %b %Y %H:%M:%S %z')
          commented_issues += 1
          total_response_time += int((first_comment_date - created_date).total_seconds())
          break
    print("%s - Issue Response Time: %.2f" % (library, total_response_time/commented_issues/86400))
    print("%s - Issue Closing Time: %.2f" % (library, total_closing_time/closed_issues/86400))
    print("%s - Security: %.2f" % (library, security_issues/total_issues*100))
    print("%s - Performance %.2f" % (library, performance_issues/total_issues*100))

if __name__ == "__main__":
  main()
