#Extracts the Issue Closing Time (in days) of a library based on its Github repository.
#
#Requirements: 
# - You will need to install PyGithub
# - You will need to input your Github credentials to make use of the Github API
# - Needs a file with the library repository names (repositories.txt)
#How to run: 
# - Just run the script with repositories.txt in the same directory.

import getpass
from github import Github, Repository

def getAverageClosingTime(repository_name, github_object):
  r = github_object.get_repo(repository_name)

  total_closing_time = 0
  total_closed_issues = 0

  for issue in r.get_issues(state="all"):
    #Ignore pull requests
    if issue.pull_request != None:
      continue

    if issue.state != "closed":
      continue
    closing_time = int((issue.closed_at - issue.created_at).total_seconds())
    total_closing_time += closing_time
    total_closed_issues += 1
  return float(total_closing_time/total_closed_issues/86400)

def main():
  with open("repositories.txt") as f:
    repositories = f.readlines()
  repositories = [x.strip() for x in repositories]
  
  username = input("Enter Github username: ")
  password = getpass.getpass("Enter your password: ")
  g = Github(username, password)

  for repo in repositories:
    closing_time = getAverageClosingTime(repo, g)
    print("%s - Issue Closing Time: %.2f" % (repo, closing_time))

if __name__ == "__main__":
  main()
