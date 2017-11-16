from datetime import datetime, timedelta

def getTime(sec):
    sec = timedelta(seconds=sec)
    d = datetime(1,1,1) + sec

    print("DAYS:HOURS:MIN:SEC")
    print("%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second))

from github import Github, Repository

def getAverageClosingTime(repository_name):
  g = Github("user", "password")
  r = g.get_repo(repository_name)
  print(r.description)

  total_closing_time = 0
  total_issues = 0

  for issue in r.get_issues(state="closed"):
    closing_time = issue.closed_at - issue.created_at
    total_closing_time += closing_time.seconds
    total_issues += 1
  getTime(total_closing_time/total_issues)

import sys

def main():
  for arg in sys.argv[1:]:
    print(arg + ": ")
    getAverageClosingTime(arg)

if __name__ == "__main__":
  main()
