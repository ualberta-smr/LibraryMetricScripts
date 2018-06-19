import getpass
import pickle
import os.path
from github import Github, Repository

issues = {}
comments = {}

class IssueData:

  def __init__(self, issue_id):
    self.issue_id = issue_id

  def addFirstResponseDate(self, date):
    self.first_comment_date = date

  def addCreationDate(self, date):
    self.creation_date = date

  def addClosingDate(self, date):
    self.closing_date = date

  def addTitle(self, title):
    self.title = title

  def addClassification(self, classification):
    self.classification = classification

  def __str__(self):
    return self.issue_id


def loadIssueData():
  data = {}
  filename = 'issuedata.pkl'
  if os.path.isfile(filename):
    with open(filename, 'rb') as input:
      try:
        data = pickle.load(input)
      except EOFError:
        print("Error loading issue data")
  return data

def saveIssueData(issue_data):
  with open('issuedata.pkl', 'wb') as output:
    pickle.dump(issue_data, output, pickle.HIGHEST_PROTOCOL)

def loadCheckPoint():
  checkpoint = []
  filename = "checkpoint.pkl"
  if os.path.isfile(filename):
    with open(filename, 'rb') as input:
      try:
        checkpoint = pickle.load(input)
      except EOFError:
        print('Error loading file')
  return checkpoint

def saveCheckPoint(obj):
  with open('checkpoint.pkl', 'wb') as output:
    pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def getIssueData():
  with open("repositories.txt") as f:
    repositories = f.readlines()
  repositories = [x.strip() for x in repositories]

  issue_data = loadIssueData()
  print(issue_data)
  for key, values in issue_data.items():
    print(key)
    for n in values:
      print(n.issue_id)
    print()
  checkpoint = loadCheckPoint()
  print("Checkpoint: ", checkpoint)

  if len(checkpoint) == 0:
    checkpoint.append(repositories[0])
    checkpoint.append(1)

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
      issue = r.get_issue(i)
      if issue == None:
        continue
      if issue.pull_request != None:
        continue

      new_issue = IssueData(i)
      new_issue.addCreationDate = issue.created_at
      new_issue.addClosingDate = issue.closed_at

      for comment in issue.get_comments():
        if comment.user == issue.user:
           continue
        new_issue.addFirstResponseDate(comment.created_at)
        break
      if repository in issue_data:
        issue_data[repository].append(new_issue)
      else:
        issue_data[repository] = [new_issue]
      saveIssueData(issue_data)
      checkpoint[1] = i
      saveCheckPoint(checkpoint)


def main():
  getIssueData()

if __name__ == "__main__":
  main()