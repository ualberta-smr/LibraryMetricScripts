#Description:
# - Extracts the Issue Response Time (in days) of a library based on its Github repository.
#
#Requirements: 
# - You will need to install PyGithub
# - You will need to input your Github credentials to make use of the Github API
#Input:
# A file with the library repository names (repositories.txt)
#Output:
# - A line with the the average Issue Response Time in days for each repository in
#   repositories.txt in the following format (printed to stdout):
#[repository] - Issue Response Time: [average number of days]
#How to run: 
# - Just run the script with repositories.txt in the same directory.

import getpass
from github import Github, Repository

def getAverageResponseTime(repository_name, github_object):
  r = github_object.get_repo(repository_name)

  total_response_time = 0
  total_issues_with_comments = 0

  for issue in r.get_issues(state="all"):
    if issue.pull_request != None:
      continue
    for comment in issue.get_comments():
       if comment.user == issue.user:
         continue
       response_time = int((comment.created_at - issue.created_at).total_seconds())
       total_response_time += response_time
       total_issues_with_comments += 1
       break
  return float(total_response_time/total_issues_with_comments/86400)

def main():
  with open("repositories.txt") as f:
    repositories = f.readlines()
  repositories = [x.strip() for x in repositories]
  
  username = input("Enter Github username: ")
  password = getpass.getpass("Enter your password: ")
  g = Github(username, password)

  for repo in repositories:
    response_time = getAverageResponseTime(repo, g)
    print("%s - Issue Response Time: %.2f" %(repo, response_time))

if __name__ == "__main__":
  main()
