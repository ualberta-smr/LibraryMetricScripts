import os
import sys
import pickle
from github import Github, Repository, GitTag
import getpass

def loadLastModificationDateData():
	data = {}
	filename = 'lastmodificationdate.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading data")
				data = pickle.load(input)
			except EOFError:
				print("Failed to load pickle file")
	return data

def saveData(data):
	with open('lastmodificationdate.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def getLastModificationDates(username, password):
        data = loadLastModificationDateData()

        rel_path = "SharedFiles/repositories.txt"
        if os.path.isdir('SharedFiles'):
                file_path = rel_path
        else:
                file_path = os.path.join(os.pardir, rel_path)
        
        with open(file_path) as f:
                repositories = f.readlines()
        repositories = [x.strip() for x in repositories]

        g = Github(username, password)

        for repository in repositories:
                r = g.get_repo(repository)
                dates_string = ""
                i = 0
                for c in r.get_commits():
                        if i == 10:
                                break
                        if i > 0:
                                dates_string += ';'
                        dates_string += c.commit.author.date.strftime('%m/%d/%Y')
                        i += 1
                data[repository] = dates_string
                saveData(data)


def main():
        if len(sys.argv) == 3:
                username = sys.argv[1]
                password = sys.argv[2]
        else:
                username = input("Enter Github username: ")
                password = getpass.getpass("Enter your password: ")
        getLastModificationDates(username, password)
        
if __name__ == "__main__":
  main()

