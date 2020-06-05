# Description:
# - Records release data of a library. Actual release frequency is calculated in filldb
#
#Requirements: 
# - You will need to install PyGithub
#Input:
# - nothing needed; reads data from DB
#Output:
# - no file output. Release data will be stored in the DB
#How to run: 
# - Just run the script.

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
django.setup()

from librarycomparison.models import Library, LibraryRelease, MetricsEntry


def getReleaseDates(token):
	
	github = Github(token)
	libraries = Library.objects.all()
	
	for library in libraries:
		
		print("Getting release data for ", library.name)

		repo = github.get_repo(library.github_repo)
		
		for tag in repo.get_tags():
			lib_releases = library.releases.filter(name__exact=tag.name)
			if not lib_releases:
				release = LibraryRelease()
				release.library = library
				release.name = tag.name
				release.release_date = tag.commit.commit.author.date
				release.save()


def get_release_freq():
		config_dict = Common_Utilities.read_config_file() # read all config data 
        
		getReleaseDates(config_dict["TOKEN"])

if __name__ == "__main__":
	get_release_freq()