#Description:
# - This file retrieves new issue data from github or Jira for the libraries in the DB. 
# - Assumes that addlibraries was already run to add any new libraries in the LibraryData.json file.
# - It first checks the last issue stored in the DB and retrieves new issues since then
#
#Requirements: 
# - You will need to install PyGithub
#Input:
# - performanceclassifier.py - the machine learning performance classifier used to classify performance issues
# - securityclassifier.py - the machine learning performance classifier used to classify security issues
# - performancedataset.xlsx, performancewords.txt, securitydataset.xlsx, securitywords.txt <- files needed for the classifiers
#Output:
# - no file output. Issue data will be stored in the DB
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


print("start classifiers")
performance_classifier = PerformanceClassifier()
security_classifier = SecurityClassifier()
print("end classifiers================")

def get_latest_issue(library):
  #get latest issue we have for this repo

  latest_issue_date = datetime(1700,1,1)
  issues = Issue.objects.filter(library=library)

  if issues:
    #latest_issue_date = issues.latest('creation_date').creation_date
    return issues.latest('creation_date')

  return None

def sleep(github):
  github_limits = github.github.get_rate_limit()
  if github_limits.core.remaining == 0:
    Common_Utilities.go_to_sleep("API hour limit exceeded,Go to sleep for ", 3600)

  if github_limits.search.remaining == 0:
    Common_Utilities.go_to_sleep("API minute limit exceeded,Go to sleep for ", 61)


def getIssueData(token):

  libraries = Library.objects.filter(jira_url__exact="").exclude(jira_url__isnull=True)

  github = Github(token)

  for library in libraries:
    looped = False
    first_issue = 1
    print("========Current repository: ", library.name)
    
    latest_issue = get_latest_issue(library)
    latest_issue_date = datetime(1700,1,1)
    if latest_issue:
    	latest_issue_date = latest_issue.creation_date
    	first_issue = int(latest_issue.issue_id)


    try:
      repo = github.get_repo(library.github_repo)
      max_issue_number = repo.get_issues(state="all", since=latest_issue_date)[0].number

    except RateLimitExceededException:
      sleep(github)

      repo = github.get_repo(library.github_repo)
      max_issue_number = repo.get_issues(state="all",since=latest_issue_date)[0].number

    print("we will loop from issue ", first_issue, "to", max_issue_number, "that we will loop through now")
 
    for i in range(first_issue, max_issue_number):
      looped = True
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
      new_issue.issue_id = str(gh_issue.number) #the actual issue id on github is the number; not sure what the issue_id in PyGithub is
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

        except Exception as e:
          print(e)
          continue
      
      try: 
        new_issue.save()
      except: 
        print("failed to create title for issue ", gh_issue.id, "... replacing with blank")
        new_issue.title = ""
        new_issue.save()
      #not sure if we need this: library.issue_set.add(issue) library.save()
    
    #sleep only if requests to github have been made
    if looped:
      Common_Utilities.go_to_sleep("Sleeping before next library..Go to sleep for ", 180)

def getIssueDataJIRA(urls):
  dict = {}

  libraries = Library.objects.exclude(jira_url="")

  for library in libraries:
    issues_in_db = Issue.objects.filter(library=library)
    print("Current repository in jira issues: ", library.name)
    xmlString = urllib.request.urlopen(library.jira_url).read().decode('utf-8')
    root = xml.etree.ElementTree.fromstring(xmlString)
    channel = root.find('channel')

    print ("num jira issues:", len(channel.findall('item')))

    for issue in channel.findall('item'):
      issue_id = issue.find('key').text

      if issues_in_db.filter(issue_id=issue_id):
        #print("Skipping issue in db: ", issue_id)
        continue

      new_issue = Issue()
      new_issue.library = library
      new_issue.issue_id = issue_id
      new_issue.title = issue.find('summary').text
      new_issue.creation_date = datetime.strptime(issue.find('created').text, '%a, %d %b %Y %H:%M:%S %z')
      new_issue.performance_issue = performance_classifier.classify(new_issue.title)
      new_issue.security_issue = security_classifier.classify(new_issue.title)

      #closing date
      resolved = issue.find('resolved')
      if resolved != None:
        new_issue.closing_date = datetime.strptime(resolved.text, '%a, %d %b %Y %H:%M:%S %z')

      #response time
      issueReporter = issue.find('reporter').get('username')
      if issue.find('comments') != None:
        for comment in issue.find('comments'):
          if comment == None or comment.get('author') == issueReporter:
            continue
          new_issue.first_response_date = datetime.strptime(comment.get('created'), '%a, %d %b %Y %H:%M:%S %z')
          break
      new_issue.save()
      #saveData(issue_data, issue_data_pkl)
      #Common_Utilities.go_to_sleep("Sleeping before next library..Go to sleep for ", 180)

def main():

  config_dict = Common_Utilities.read_config_file() # read all config data 
  
  lib_data_json = read_json_file("SharedFiles/LibraryData.json")

  print("Getting JIRA issue data")  
  getIssueDataJIRA(lib_data_json)
  #print("Getting GitHub issue data")
  #getIssueData(config_dict["TOKEN"])

if __name__ == "__main__":
  main()
