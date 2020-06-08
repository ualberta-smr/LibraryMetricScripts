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
from scripts.CommonUtilities import Common_Utilities
from scripts.SharedFiles.utility_tool import read_json_file

import django
import pickle
import pygal

from librarycomparison.models import Library

def loadLicenseData():
	data = {}
	filename = 'scripts/License/license.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading data")
				data = pickle.load(input)
			except EOFError:
				print("Failed to load pickle file")
	return data

def saveData(data):
	with open('scripts/License/license.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.DEFAULT_PROTOCOL)

def getLicenses():
	config_dict = Common_Utilities.read_config_file() # read all ini data 
	token = config_dict["TOKEN"]
	data = loadLicenseData()

	github = Github(token)
	libraries = Library.objects.all()
	
	for library in libraries:
		try:
			repo = github.get_repo(library.github_repo)
			data[library.github_repo] = repo.get_license().license.name
			saveData(data)
		except UnknownObjectException:
			print("ERROR: could not get license for lib", library.name)
			traceback.print_exc()
			data[library.github_repo] = 'None'
			saveData(data)

if __name__ == "__main__":
        getLicenses()

