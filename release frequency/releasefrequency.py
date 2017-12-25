from github import Github, Repository, GitTag
import getpass

def getReleaseFrequency(repository_name, github_object):
  r = github_object.get_repo(repository_name)
  print(r.description)
  dates = []

  for tag in r.get_tags():
    dates.append(tag.commit.commit.author.date)
  
  dates.sort()
  number_of_differences = len(dates)-1
  total_seconds = 0
  for i in range(1, len(dates)):
    total_seconds += int((dates[i] - dates[i-1]).total_seconds())
  #divide the average by the number of seconds per day
  print("Release Frequency Average: %.2f days" % float(total_seconds/number_of_differences/86400))

def main():
  with open("repositories.txt") as f:
    repositories = f.readlines()
  repositories = [x.strip() for x in repositories]
  
  with open("librarynames.txt") as f:
    libraries = f.readlines()
  library = [x.strip('\n') for x in libraries]
  
  username = input("Enter Github username: ")
  password = getpass.getpass("Enter your password: ")
  g = Github(username, password)

  i = 0
  for repository in repositories:
    print("%s: " % library[i])
    getReleaseFrequency(repository, g)
    i += 1

if __name__ == "__main__":
  main()
