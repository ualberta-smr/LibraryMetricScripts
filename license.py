import os
import pickle
from github import Github, Repository, GitTag
import getpass

def printData(data):
	for repo, dates in data.items():
		print(repo)
		print(dates)
		print("")

def loadData():
	data = {}
	filename = 'license.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading data")
				data = pickle.load(input)
				#print(data)
				printData(data)
			except EOFError:
				print("Failed to load pickle file")
	return data

def saveData(data):
	with open('license.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def getLicenses():
	data = loadData()

	with open("repositories.txt") as f:
		repositories = f.readlines()
	repositories = [x.strip() for x in repositories]

	username = input("Enter Github username: ")
	password = getpass.getpass("Enter your password: ")
	g = Github(username, password)

	for repository in repositories:
		if repository in data:
			continue

		r = g.get_repo(repository)

		data[repository] = r.get_license().license.name
		saveData(data)


def main():
	getLicenses()

if __name__ == "__main__":
  main()

