import os
import pickle
from github import Github, Repository, GitTag
import getpass

class ReleaseData:
	def __init__(self, repository):
		self.repository = repository
		release_dates = []
		release_names = []

	def addReleaseName(name):
		self.release_name.append(name)

	def addReleaseDate(date):
		self.release_date.append(date)

	def calculateReleaseFrequency():
		self.release_dates.sort()
		number_of_differences = len(dates)-1
		total_seconds = 0
		for i in range(1, len(release_dates)):
			total_seconds += int((release_dates[i] - release_dates[i-1]).total_seconds())
		#divide the average by the number of seconds per day
		self.release_frequency_average = float(total_seconds/number_of_differences/86400)


def printData(data):
	for repo, dates in data.items():
		print(repo)
		print(dates)
		print("")

def loadData():
	data = {}
	filename = 'releasefrequency.pkl'
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
	with open('releasefrequency.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def getReleaseDates():
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

		release_data = ReleaseData(repository)

		#Obtain the date of the git tag
		for tag in r.get_tags():
			release_data.addReleaseDate(tag.commit.commit.author.date)
			release_data.addReleaseDate(names.append(tag.name))
		release_data.calculateReleaseFrequency()

		data.append(release_data)
		saveData(data)


def main():
	getReleaseDates()

if __name__ == "__main__":
  main()

