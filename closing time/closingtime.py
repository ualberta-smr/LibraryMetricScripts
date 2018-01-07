import getpass
from github import Github, Repository

def getAverageClosingTime(repository_name, github_object):
  r = github_object.get_repo(repository_name)
  print(r.description)

  total_closing_time = 0
  total_response_time = 0
  total_issues_with_comments = 0
  total_closed_issues = 0

  for issue in r.get_issues(state="all"):
    if issue.pull_request != None:
      continue
    for comment in issue.get_comments():
       response_time = int((comment.created_at - issue.created_at).total_seconds())
       total_response_time += response_time
       total_issues_with_comments += 1
       break
    if issue.state != "closed":
      continue
    closing_time = int((issue.closed_at - issue.created_at).total_seconds())
    total_closing_time += closing_time
    total_closed_issues += 1
  print("Average Closing Time: %.2f days" % float(total_closing_time/total_closed_issues/86400))
  print("Average Response Time: %.2f days" % float(total_response_time/total_issues_with_comments/86400))
  return float(total_closing_time/total_closed_issues/86400), float(total_response_time/total_issues_with_comments/86400)

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

  f1 = open('averageclosingtime.txt', 'w')
  f2 = open('averageresponsetime.txt', 'w')
  for i in range(0, len(repositories)):
    closing_time, response_time = getAverageClosingTime(repositories[i], g)
    f1.write("%s:%.2f\n" % (library[i], closing_time))
    f2.write("%s:%.2f\n" % (library[i], response_time))
  f1.close()
  f2.close()

if __name__ == "__main__":
  main()
