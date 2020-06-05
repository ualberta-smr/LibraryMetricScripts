#Description: 
# - Extracts the license of a Github repository.
#Requirements: 
# - You will need to enter your Github credentials
#Input:
# File LibraryData.json which contains all the library repositories
#Output:
# A pickle file called license.pkl, which will contain a dictionary where the key is a library repository, and the value of each key is
#a string containing the license used in the repository:
#[library repository] => [repository license]
#How to run: 
# - Just run the script.

import os
import pickle
from github import Github, Repository, GitTag
from github.GithubException import UnknownObjectException
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

def loadLicenseData():
	data = {}
	filename = 'License/license.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading data")
				data = pickle.load(input)
			except EOFError:
				print("Failed to load pickle file")
	return data

def saveData(data):
	with open('License/license.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def getLicenses(token):
	data = loadLicenseData()

	github = Github(token)
	libraries = Library.objects.all()
	
	for library in libraries:
		if library.github_repo in data:
			continue
		try:
			repo = github.get_repo(library.github_repo)
			data[library.github_repo] = repo.get_license().license.name
			saveData(data)
		except UnknownObjectException:
			data[library.github_repo] = 'None'
			saveData(data)

def main():
        config_dict = Common_Utilities.read_config_file() # read all ini data 
        getLicenses(config_dict["TOKEN"])

if __name__ == "__main__":
        main()

