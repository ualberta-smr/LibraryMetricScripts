from github import Github, Repository, Commit
import getpass

def getLastCommitDate(repository_name, github_object):
  r = github_object.get_repo(repository_name)
  c = r.get_commits()[0]
  return c.commit.author.date


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

  f = open('lastcommitdate.txt', 'w')
  for i in range(0, len(repositories)):
    date = getLastCommitDate(repositories[i], g)
    print("%s:%s\n" % (library[i], date))
    f.write("%s:%s\n" % (library[i], date))
  f.close()

if __name__ == "__main__":
  main()
