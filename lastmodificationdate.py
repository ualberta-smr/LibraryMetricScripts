import os
import pickle
from github import Github, Repository, GitTag
import getpass

def printData(data):
	for repo, dates in data.items():
		print(repo)
		print(dates)
		print("")

def loadLastModificationDateData():
	data = {}
	filename = 'lastmodificationdate.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading data")
				data = pickle.load(input)
				#print(data)
				#printData(data)
			except EOFError:
				print("Failed to load pickle file")
	return data

def saveData(data):
	with open('lastmodificationdate.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def getLastModificationDates():
	data = loadLastModificationDateData()
	print(data)

	with open("repositories.txt") as f:
		repositories = f.readlines()
	repositories = [x.strip() for x in repositories]

	username = input("Enter Github username: ")
	password = getpass.getpass("Enter your password: ")
	g = Github(username, password)

	for repository in repositories:
		#if repository in data:
		#	continue

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
	getLastModificationDates()

if __name__ == "__main__":
  main()

