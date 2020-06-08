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
from scripts.CommonUtilities import Common_Utilities
from scripts.SharedFiles.utility_tool import read_json_file
import django
import pickle
import pygal


from librarycomparison.models import Library

def loadLastModificationDateData():
	data = {}
	filename = 'scripts/LastModificationDate/lastmodificationdate.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading last modification data")
				data = pickle.load(input)
			except EOFError:
				print("Failed to load pickle file")
	return data

def saveData(data):
	with open('scripts/LastModificationDate/lastmodificationdate.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.DEFAULT_PROTOCOL)

def getLastModificationDates():
	config_dict = Common_Utilities.read_config_file() # read all config data 
	token = config_dict["TOKEN"]
	
	data = loadLastModificationDateData()
	  
	github = Github(token)
	libraries = Library.objects.all()
	
	for library in libraries:
		repo = github.get_repo(library.github_repo)
		dates_string = ""
		i = 0
		for c in repo.get_commits():
			if i == 10:
				break
			if i > 0:
				dates_string += ';'
			dates_string += c.commit.author.date.strftime("%m/%d/%Y, %H:%M:%S")
			i += 1
		data[library.github_repo] = dates_string
		saveData(data)

        
if __name__ == "__main__":
  getLastModificationDates()

