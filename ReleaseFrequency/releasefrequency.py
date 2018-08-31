#Obtains the Release Frequency (in days) of a library based on its Github repository.
#
#Requirements: 
# - You will need to install PyGithub
# - You will need to input your Github credentials to make use of the Github API
# - Needs a file with the library repository names (repositories.txt)
#How to run: 
# - Just run the script with repositories.txt in the same directory.

from github import Github, Repository, GitTag
import getpass

def getReleaseFrequency(repository_name, github_object):
  r = github_object.get_repo(repository_name)
  dates = []

  #Obtain the date of the git tag
  for tag in r.get_tags():
    dates.append(tag.commit.commit.author.date)
  
  dates.sort()
  number_of_differences = len(dates)-1
  total_seconds = 0
  for i in range(1, len(dates)):
    total_seconds += int((dates[i] - dates[i-1]).total_seconds())

  #divide the average by the number of seconds per day
  return float(total_seconds/number_of_differences/86400)

def main():
  
  with open("repositories.txt") as f:
    repositories = f.readlines()
  repositories = [x.strip() for x in repositories]

  username = input("Enter Github username: ")
  password = getpass.getpass("Enter your password: ")
  g = Github(username, password)

  for repo in repositories:
    print("%s - Release Frequency: %.2f" % (repo, getReleaseFrequency(repo, g)))

if __name__ == "__main__":
  main()
