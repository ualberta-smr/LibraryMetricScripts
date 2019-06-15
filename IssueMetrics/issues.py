#Description:
# - This file extracts the Issue Closing Time (in days), the Issue Response Time, and the Performance and Security metrics of a library
# based on its Github repository.
#
#Requirements: 
# - You will need to install PyGithub
# - You will need to input your Github credentials to make use of the Github API
#Input:
# - github_bug_repositories.txt - the list of repositories whose bug reports are hosted on Github
# - jiralibraries.txt - a list of libraries whose bug reports are hosted on JIRA
# - performanceclassifier.py - the machine learning performance classifier used to classify performance issues
# - securityclassifier.py - the machine learning performance classifier used to classify security issues
# - performancedataset.xlsx, performancewords.txt, securitydataset.xlsx, securitywords.txt <- files needed for the classifiers
#Output:
# issuedata.pkl - a pickle file containing a dictionary where the key is a repository and its value is a list of IssueData objects (see class)
# issueresponsetime.pkl a piclkle file containing a dictionary where the key is a repository and its value is the issue response time in days (stored as float)
# issueclosingtime.pkl a piclkle file containing a dictionary where the key is a repository and its value is the issue closing time in days (stored as float)
#
#How to run: 
# - Just run the script (make sure the input files are in the same directory)

import getpass
import sys
import pickle
import os.path
import urllib.request
import xml.etree.ElementTree
import time
from datetime import datetime
from github import Github, Repository
from github.GithubException import UnknownObjectException, RateLimitExceededException, GithubException
from IssueMetrics.performanceclassifier import PerformanceClassifier
from IssueMetrics.securityclassifier import SecurityClassifier

class IssueData:

  def __init__(self, issue_id):
    self.issue_id = issue_id
    self.title = None
    self.closing_date = None
    self.first_comment_date = None
    self.creation_date = None
    self.performance_issue = None
    self.security_issue = None
    self.state = None

  def addState(self, state):
    self.state = state

  def addFirstResponseDate(self, date):
    self.first_comment_date = date

  def addCreationDate(self, date):
    self.creation_date = date

  def addClosingDate(self, date):
    self.closing_date = date

  def addTitle(self, title):
    self.title = title

  def setPerformanceIssue(self, value):
    self.performance_issue = value

  def setSecurityIssue(self, value):
    self.security_issue = value

  def __str__(self):
    return self.issue_id


def loadData(filename):
  data = {}
  if os.path.isfile(filename):
    with open(filename, 'rb') as input:
      try:
        data = pickle.load(input)
      except EOFError:
        print("Error loading data")
  return data

def saveData(data, filename):
  with open(filename, 'wb') as output:
    pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)


def calculateAverageClosingTime():
  issue_data = loadData('issuedata.pkl')
  issue_closing_times = {}
  for repo, issues in issue_data.items():
    total_closing_time = 0
    total_closed_issues = 0
    for issue in issues:
      if issue.closing_date == None:
        continue
      closing_time = int((issue.closing_date - issue.creation_date).total_seconds())
      total_closing_time += closing_time
      total_closed_issues += 1
    issue_closing_times[repo] = float(total_closing_time/total_closed_issues/86400)
  saveData(issue_closing_times, 'issueclosingtime.pkl')

def calculateAverageResponseTime():
  issue_data = loadData('issuedata.pkl')
  issue_response_times = {}
  for repo, issues in issue_data.items():
    total_response_time = 0
    total_issues_with_comments = 0
    for issue in issues:
      if issue.first_comment_date == None:
        continue
      response_time = int((issue.first_comment_date - issue.creation_date).total_seconds())
      total_response_time += response_time
      total_issues_with_comments += 1
    issue_response_times[repo] = float(total_response_time/total_issues_with_comments/86400)
  saveData(issue_response_times, 'issueresponsetime.pkl')

def getIssueData(username, password):
  with open("github_bug_repositories.txt") as f:
    repositories = f.readlines()
  repositories = [x.strip() for x in repositories]
  
  issue_data = loadData('issuedata.pkl')

  if issue_data == None:
    issue_data = {}

  g = Github(username, password)

  for repository in repositories:
    first_issue = 1
    print("Current repository: ", repository)

    try:
      r = g.get_repo(repository)

      max_issue_number = r.get_issues(state="all")[0].number
    except RateLimitExceededException:
      print("Rate Limit Exceeded... Sleeping 1 hour")
      time.sleep(60*60)
      g = Github(username, password)
      r = g.get_repo(repository)
      max_issue_number = r.get_issues(state="all")[0].number

    for i in range(first_issue, max_issue_number):
      try:
        issue = r.get_issue(i)
      except UnknownObjectException:
        continue
      except RateLimitExceededException:
        print("Rate Limit Exceeded... Sleeping 1 hour") 
        time.sleep(60*60)
        g = Github(username, password)
        r = g.get_repo(repository)
        i -= 1
        continue
      except:
        continue
      if issue == None:
        continue
      if issue.pull_request != None:
        continue

      new_issue = IssueData(i)
      new_issue.addTitle(issue.title)
      new_issue.addCreationDate(issue.created_at)
      new_issue.addClosingDate(issue.closed_at)

      while True:
        try:
          for comment in issue.get_comments():
            if comment.user == issue.user:
              continue
            new_issue.addFirstResponseDate(comment.created_at)
            break
          break
        except RateLimitExceededException:
          print("Rate Limit Exceeded... Sleeping 1 hour")
          time.sleep(60*60)
          g = Github(username, password)
          r = g.get_repo(repository)
          issue = r.get_issue(i)
        except Exception as e:
          print(e)
          continue
        
      if repository in issue_data:
        issue_data[repository].append(new_issue)
      else:
        issue_data[repository] = [new_issue]
      saveData(issue_data, 'issuedata.pkl')

def getIssueDataJIRA():
  dict = {}
  file_path = 'jiralibraries.txt'
  with open(file_path) as f:
    urls = f.readlines()
  urls = [x.strip() for x in urls]

  issue_data = loadData('issuedata.pkl')

  for line in urls:
    strings = line.split('|')
    dict[strings[0]] = strings[1]

  for repository, url in dict.items():
    print("Current repository: ", repository)
    xmlString = urllib.request.urlopen(url).read().decode('utf-8')
    root = xml.etree.ElementTree.fromstring(xmlString)
    channel = root.find('channel')

    closed_issues = 0
    commented_issues = 0
    total_closing_time = 0
    total_response_time = 0

    for issue in channel.findall('item'):
      new_issue = IssueData(issue.find('key').text)
      new_issue.addTitle(issue.find('summary').text)

      #response time/closing time
      created_date = datetime.strptime(issue.find('created').text, '%a, %d %b %Y %H:%M:%S %z')
      new_issue.addCreationDate(created_date)
      #response time
      resolved = issue.find('resolved')
      if resolved != None:
        resolved_date = datetime.strptime(resolved.text, '%a, %d %b %Y %H:%M:%S %z')
        new_issue.addClosingDate(resolved_date)

      issueReporter = issue.find('reporter').get('username')
      if issue.find('comments') != None:
        for comment in issue.find('comments'):
          if comment == None or comment.get('author') == issueReporter:
            continue
          first_comment_date = datetime.strptime(comment.get('created'), '%a, %d %b %Y %H:%M:%S %z')
          new_issue.addFirstResponseDate(first_comment_date)
          break
      if repository in issue_data:
        issue_data[repository].append(new_issue)
      else:
        issue_data[repository] = [new_issue]
      saveData(issue_data, 'issuedata.pkl')

def applyClassifiers():
  performance_classifier = PerformanceClassifier()
  security_classifier = SecurityClassifier()
  issue_data = loadData('issuedata.pkl')
  for repo, issues in issue_data.items():
    for issue in issues:
      if performance_classifier.classify(issue.title) == True:
        issue.performance_issue = True
      else:
        issue.performance_issue = False

      if security_classifier.classify(issue.title) == True:
        issue.security_issue = True
      else:
        issue.security_issue = False
  saveData(issue_data, 'issuedata.pkl')

def main():
  
  if len(sys.argv) == 3:
    username = sys.argv[1]
    password = sys.argv[2]
  else:
    username = input("Enter Github username: ")
    password = getpass.getpass("Enter your password: ")
  getIssueDataJIRA()
  getIssueData(username, password)
  calculateAverageResponseTime()
  calculateAverageClosingTime()
  applyClassifiers()

if __name__ == "__main__":
  main()
