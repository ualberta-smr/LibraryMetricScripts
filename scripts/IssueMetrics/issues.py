#Description:
# - This file extracts the Issue Closing Time (in days), the Issue Response Time, and the Performance and Security metrics of a library
# based on its Github repository.
#
#Requirements: 
# - You will need to install PyGithub
# - You will need to input your Github credentials to make use of the Github API
#Input:
# - LibraryData.json - includes the list of repositories whose bug reports are hosted on Github and a list of libraries whose bug reports are hosted on JIRA
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
from performanceclassifier import PerformanceClassifier
from securityclassifier import SecurityClassifier
import json
from CommonUtilities import Common_Utilities


#This makes the utility_tool visible from this file
import sys
sys.path.append('../')
from SharedFiles.utility_tool import read_json_file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'librarycomparison.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "librarycomparison.settings")
import django
django.setup()
from librarycomparison.models import Library, Issue

issue_closing_time_pkl = 'IssueMetrics/issueclosingtime.pkl'
issue_data_pkl = 'IssueMetrics/issuedata.pkl'
issue_resp_time_pkl = 'IssueMetrics/issueresponsetime.pkl'

print("start classifiers")
performance_classifier = PerformanceClassifier()
security_classifier = SecurityClassifier()
print("end classifiers================")

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
  issue_data = loadData(issue_data_pkl)
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
  saveData(issue_closing_times, issue_closing_time_pkl)

##TODO: calculate this during filling db as aggregation
def calculateAverageResponseTime():
  # issue_data = loadData(issue_data_pkl)
  issue_response_times = {}
  for library in Library.objects.all():
    total_response_time = 0
    total_issues_with_comments = 0
    for issue in Issue.objects.get(library=library):
      if issue.first_response_date == None:
        continue
      response_time = int((issue.first_response_date - issue.creation_date).total_seconds())
      total_response_time += response_time
      total_issues_with_comments += 1
      #issue_response_times[repo] = float(total_response_time/total_issues_with_comments/86400)
      metricsentry = MetricsEntry.objects.filter(library=library)
      metricsentry.repsonse_time = float(total_response_time/total_issues_with_comments/86400)
  #saveData(issue_response_times, issue_resp_time_pkl)

def get_latest_issue_date(library):
  #get latest data we have about this repo
  
  print("got library", library.name)
  latest_issue_date = datetime(1700,1,1)
  issues = Issue.objects.filter(library=library)

  if issues:
    latest_issue_date = issues.latest('creation_date').creation_date

  return latest_issue_date

def sleep(github):
  github_limits = github.github.get_rate_limit()
  if github_limits.core.remaining == 0:
    Common_Utilities.go_to_sleep("API minute limit exceeded,Go to sleep for ", 3600)

  if github_limits.search.remaining == 0:
    Common_Utilities.go_to_sleep("API minute limit exceeded,Go to sleep for ", 61)


def getIssueData(token, arr):

  repositories = []
  for line in arr:    
    if line['JIRAURL'] == "":
      repositories.append(line['FullRepoName'])
 
  #issue_data = loadData(issue_data_pkl)

  #if issue_data == None:
  #  issue_data = {}

  github = Github(token)

  for repo_name in repositories:
    first_issue = 1
    print("========Current repository: ", repo_name)
    library = Library.objects.get(github_repo=repo_name)
    latest_issue_date = get_latest_issue_date(library)

    try:
      repo = github.get_repo(repo_name)
      max_issue_number = repo.get_issues(state="all", since=latest_issue_date)[0].number

    except RateLimitExceededException:
      sleep(github)

      repo = github.get_repo(repo_name)
      max_issue_number = r.get_issues(state="all",since=latest_issue_date)[0].number

    print("we have ", max_issue_number, "that we will loop through now")

    for i in range(first_issue, max_issue_number):
      print("**processing issue ", i)
      try:
        gh_issue = repo.get_issue(i)
      except UnknownObjectException:
        continue
      except RateLimitExceededException:
        Common_Utilities.go_to_sleep("API limit exceeded,Go to sleep for ", 60)
        #repo = g.get_repo(repo_name)
        i -= 1
        continue
      except:
        continue
      if gh_issue == None:
        continue
      if gh_issue.pull_request != None:
        continue

      print("starting to create issue")
      new_issue = Issue()
      new_issue.issue_id = str(gh_issue.id)
      new_issue.creation_date = gh_issue.created_at
      new_issue.closing_date = gh_issue.closed_at
      new_issue.library = library
      try:
        new_issue.title = gh_issue.title
        new_issue.performance_issue = performance_classifier.classify(new_issue.title)
        new_issue.security_issue = security_classifier.classify(new_issue.title)
      except:
        print("failed to create title for issue ", gh_issue.id)
      print("created basics")

      while True:
        print("processing comments")
        try:
          for comment in gh_issue.get_comments():
            if comment.user == gh_issue.user:
              continue
            new_issue.first_response_date = comment.created_at
            break
          break
        except RateLimitExceededException:
          Common_Utilities.go_to_sleep("API limit exceeded,Go to sleep for ", quick_sleep)
          #g = Github(token)
          #r = g.get_repo(repository)
          #issue = r.get_issue(i)
        except Exception as e:
          print(e)
          continue
       
      new_issue.save()
      #not sure if we need this: library.issue_set.add(issue) library.save()
    Common_Utilities.go_to_sleep("Sleeping before next library..Go to sleep for ", 180)

def getIssueDataJIRA(urls):
  dict = {}
  issue_data = loadData(issue_data_pkl)

  for line in urls:    
    if line['JIRAURL'] != "":     
      dict[line['FullRepoName']]=line['JIRAURL']  
  
 
  for repository, url in dict.items():
    print("Current repository in issues: ", repository)
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
      saveData(issue_data, issue_data_pkl)

def applyClassifiers():
  performance_classifier = PerformanceClassifier()
  security_classifier = SecurityClassifier()
  issue_data = loadData(issue_data_pkl)
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
  saveData(issue_data, issue_data_pkl)

def main():

  config_dict = Common_Utilities.read_config_file() # read all config data 
  
  lib_data_json = read_json_file("SharedFiles/LibraryData.json")

  print("Getting issue data")  
  getIssueDataJIRA(lib_data_json)
  print("Got jira issue data")
  getIssueData(config_dict["TOKEN"], lib_data_json)

  # print("Calculating avg response time")  
  # calculateAverageResponseTime()
  # print("Calculating avg closing time")  
  # calculateAverageClosingTime()
  # print("Applying classifiers")
  # applyClassifiers()

if __name__ == "__main__":
  main()
