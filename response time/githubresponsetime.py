#Include the repositories as command line arguments, e.g. python githubresponsetime.py google/keyczar

from datetime import datetime, timedelta

def getTime(sec):
    sec = timedelta(seconds=sec)
    d = datetime(1,1,1) + sec

    print("Response time: %d:%d:%d:%d (D:H:M:S)\n" % (d.day-1, d.hour, d.minute, d.second))

from github import Github, Repository
import math

def getResponseTime(repository_name, any_response_flag):
  g = Github("user", "password")
  r = g.get_repo(repository_name)
  print(r.description)

  contributor_logins = set()
  list_of_contributors = []
  number_of_contributors = 0
  total_response_time = 0
  total_issues = 0
  
  if any_response_flag == False:
    for contributor in r.get_contributors():
      list_of_contributors.append(contributor.login)
      number_of_contributors += 1

    for i in range(0, int(math.ceil(number_of_contributors/2))):
      contributor_logins.add(list_of_contributors[i])

  for issue in r.get_issues(state="all"):
    for comment in issue.get_comments():
      if any_response_flag == True or comment.user.login in contributor_logins:
          response_time = comment.created_at - issue.created_at
          total_response_time += response_time.seconds
          total_issues += 1
          break
  getTime(total_response_time/total_issues)

import sys

def main():
  for arg in sys.argv[1:]:
    print(arg + ": ")
    getResponseTime(arg, True)

if __name__ == "__main__":
  main()
