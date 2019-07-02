# Description:
# - Obtains the Release Frequency (in days) of a library based on its Github repository. Additionally, this script the date and name of
# all releases of a library (see class ReleaseData)
#
#Requirements: 
# - You will need to install PyGithub
# - You will need to input your Github credentials to make use of the Github API
#Input:
# - A file with the library repository names (LibraryData.json)
#Output:
# - A pickle file called releasefrequency.pkl which will contain a dictionary where the key is the name of the repository and the
#value is a ReleaseData object (which contains a list of names of releases with its dates)
#How to run: 
# - Just run the script.

import os
import pickle
from github import Github, Repository, GitTag
import getpass
import json

#This makes the utility_tool visible from this file
import sys
sys.path.append('../')
from SharedFiles.utility_tool import read_json_file

class ReleaseData:
	def __init__(self, repository):
		self.repository = repository
		self.release_dates = []
		self.release_names = []
		self.release_frequency_average = 0.0

	def addReleaseName(self, name):
		self.release_names.append(name)

	def addReleaseDate(self, date):
		self.release_dates.append(date)

	def calculateReleaseFrequency(self):
		self.release_dates.sort()
		number_of_differences = len(self.release_dates)-1
		total_seconds = 0
		for i in range(1, len(self.release_dates)):
			total_seconds += int((self.release_dates[i] - self.release_dates[i-1]).total_seconds())
		#divide the average by the number of seconds per day
		self.release_frequency_average = float(total_seconds/number_of_differences/86400)

def printData(data):
	for repo, dates in data.items():
		print(repo)
		print(dates)
		print("")

def loadReleaseFrequencyData():
	data = {}
	filename = 'releasefrequency.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading data")
				data = pickle.load(input)
				print("done")
				#print(data)
				printData(data)
			except EOFError:
				print("Failed to load pickle file")
	return data

def saveData(data):
	with open('releasefrequency.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def getReleaseDates(username, password):
	
	data = loadReleaseFrequencyData()

	repositories = []
	LibraryData = read_json_file('../SharedFiles/LibraryData.json')
	for line in LibraryData:
		repositories.append(line['FullRepoName'])
	
	g = Github(username, password)
	
	for repository in repositories:
		
		if repository in data:
			continue
		
		r = g.get_repo(repository)
		release_data = ReleaseData(repository)
		
		#Obtain the date of the git tag
		for tag in r.get_tags():
			release_data.addReleaseDate(tag.commit.commit.author.date)
			release_data.addReleaseName(tag.name)
		release_data.calculateReleaseFrequency()
		
		data[repository] = release_data
		saveData(data)

def main():
        if len(sys.argv) == 3:
                print(sys.argv[1])
                print(sys.argv[2])
                username = sys.argv[1]
                password = sys.argv[2]
        else:
                username = input("Enter your Github username: ")
                password = getpass.getpass("Enter your password: ")
        getReleaseDates(username, password)

if __name__ == "__main__":
	main()