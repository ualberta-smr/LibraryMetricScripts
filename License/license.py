#Description: 
# - Extracts the license of a Github repository.
#Requirements: 
# - You will need to enter your Github credentials
#Input:
# File SharedFiles/repositories.txt with the list of library repositories
#Output:
# A pickle file called license.pkl, which will contain a dictionary where the key is a library repository, and the value of each key is
#a string containing the license used in the repository:
#[library repository] => [repository license]
#How to run: 
# - Just run the script.

import os
import sys
import pickle
from github import Github, Repository, GitTag
from github.GithubException import UnknownObjectException
import getpass

def loadLicenseData():
	data = {}
	filename = 'license.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading data")
				data = pickle.load(input)
			except EOFError:
				print("Failed to load pickle file")
	return data

def saveData(data):
	with open('license.pkl', 'wb') as output:
		pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def getLicenses(username, password):
        data = loadLicenseData()

        rel_path = "SharedFiles/repositories.txt"
        if os.path.isdir('SharedFiles'):
                file_path = rel_path
        else:
                file_path = os.path.join(os.pardir, rel_path)
        with open(file_path) as f:
                repositories = f.readlines()
        repositories = [x.strip() for x in repositories]

        g = Github(username, password)

        for repository in repositories:
                if repository in data:
                        continue
                try:
                        r = g.get_repo(repository)
                        print(repository)
                        data[repository] = r.get_license().license.name
                        saveData(data)
                except UnknownObjectException:
                        data[repository] = 'None'
                        saveData(data)


def main():
        if len(sys.argv) == 3:
                username = sys.argv[1]
                password = sys.argv[2]
        else:
                username = input("Enter Github username: ")
                password = getpass.getpass("Enter your password: ")
        getLicenses(username, password)

if __name__ == "__main__":
        main()

