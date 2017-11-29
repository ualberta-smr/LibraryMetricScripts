from datetime import datetime, timedelta

def getTime(sec):
    sec = timedelta(seconds=sec)
    d = datetime(1,1,1) + sec

    print("Release frequency average: %d:%d:%d:%d (D:H:M:S)\n" % (d.day-1, d.hour, d.minute, d.second))

from github import Github, Repository, GitTag
import math

def getReleaseFrequency(repository_name):
  g = Github("yourusername", "yourpassword")
  r = g.get_repo(repository_name)
  print(r.description)
  dates = []

  for tag in r.get_tags():
    #print(tag.name)
    #print(tag.commit.commit.author.date)
    dates.append(tag.commit.commit.author.date)
  
  dates.sort()
  number_of_differences = len(dates)-1
  total_seconds = 0
  for i in range(1, len(dates)):
    total_seconds += int((dates[i] - dates[i-1]).total_seconds())
  print(total_seconds)
  getTime(total_seconds/number_of_differences)

def main():
  with open("repositories.txt") as f:
    repositories = f.readlines()
  repositories = [x.strip() for x in repositories]
  
  for repository in repositories:
    print(repository + ": ")
    getReleaseFrequency(repository)

if __name__ == "__main__":
  main()
