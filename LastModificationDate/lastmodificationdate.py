#Description: obtains the Last 5 Modification Dates (last commit) of a library based on its Github repository.
#
#Requirements: 
# - You will need to install PyGithub
# - You will need to input your Github credentials to make use of the Github API
#Input:
# - A file with the library repository names (LibraryData.json)
#Output:
# A pickle file called lastmodificationdate.pkl, which will contain a dictionary where the key is a library repository, and the value is each key is
#a string containing dates in format %m/%d/%Y separated by semicolons:
#[library repository] => "%m/%d/%Y;%m/%d/%Y;%m/%d/%Y;%m/%d/%Y;%m/%d/%Y"
#How to run: 
# - Run the script with repositories.txt

import os
import pickle
from github import Github, Repository, GitTag
import getpass
import json

#This makes the utility_tool visible from this file
import sys
sys.path.append('../')
from SharedFiles.utility_tool import read_json_file

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
	  
	repositories = []
	LibraryData = read_json_file('../SharedFiles/LibraryData.json')
	for line in LibraryData:
		repositories.append(line['FullRepoName'])
	
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

