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
from CommonUtilities import Common_Utilities

#This makes the utility_tool visible from this file
import sys
sys.path.append('../')
from SharedFiles.utility_tool import read_json_file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'librarycomparison.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "librarycomparison.settings")
import django
import pickle
import pygal
django.setup()

from librarycomparison.models import Library

def loadLastModificationDateData():
	data = {}
	filename = 'LastModificationDate/lastmodificationdate.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading data")
				data = pickle.load(input)
			except EOFError:
				print("Failed to load pickle file")
	return data

def saveData(data):
	with open('LastModificationDate/lastmodificationdate.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def getLastModificationDates(token):
	
	data = loadLastModificationDateData()
	  
	github = Github(token)
	libraries = Library.objects.all()
	
	for library in libraries:
		print ("getting data for" , library.name)
		repo = github.get_repo(library.github_repo)
		dates_string = ""
		i = 0
		for c in repo.get_commits():
			if i == 10:
				break
			if i > 0:
				dates_string += ';'
			dates_string += c.commit.author.date.strftime('%m/%d/%Y')
			i += 1
		data[library.github_repo] = dates_string
		saveData(data)

def main():
        config_dict = Common_Utilities.read_config_file() # read all config data 
        getLastModificationDates(config_dict["TOKEN"])
        
if __name__ == "__main__":
  main()

