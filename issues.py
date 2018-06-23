import getpass
import pickle
import os.path
from github import Github, Repository
from github.GithubException import UnknownObjectException
from performanceclassifier import PerformanceClassifier
from securityclassifier import SecurityClassifier

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
  data = None
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

def getIssueData():
  with open("repositories.txt") as f:
    repositories = f.readlines()
  repositories = [x.strip() for x in repositories]

  issue_data = loadData('issuedata.pkl')
  checkpoint = loadData('checkpoint.pkl')
  print("Checkpoint: ", checkpoint)

  if issue_data == None:
    issue_data = {}

  if checkpoint == None:
    checkpoint = [repositories[0], 1]

  username = input("Enter Github username: ")
  password = getpass.getpass("Enter your password: ")
  g = Github(username, password)
  first_flag = True

  for repository in repositories:
    if first_flag == True and repository != checkpoint[0]:
      continue
    if first_flag == False:
      checkpoint[1] = 1

    first_flag = False
    checkpoint[0] = repository
    first_issue = checkpoint[1]

    r = g.get_repo(repository)


    max_issue_number = r.get_issues(state="all")[0].number;
    for i in range(first_issue, max_issue_number):
      try:
        issue = r.get_issue(i)
      except UnknownObjectException:
        continue
      if issue == None:
        continue
      if issue.pull_request != None:
        continue

      new_issue = IssueData(i)
      new_issue.addTitle(issue.title)
      new_issue.addCreationDate(issue.created_at)
      new_issue.addClosingDate(issue.closed_at)

      for comment in issue.get_comments():
        if comment.user == issue.user:
           continue
        new_issue.addFirstResponseDate(comment.created_at)
        break
      if repository in issue_data:
        issue_data[repository].append(new_issue)
      else:
        issue_data[repository] = [new_issue]
      saveData(issue_data, 'issuedata.pkl')
      checkpoint[1] = i
      saveData(checkpoint, 'checkpoint.pkl')

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
  getIssueData()
  calculateAverageResponseTime()
  calculateAverageClosingTime()
  applyClassifiers()

if __name__ == "__main__":
  main()