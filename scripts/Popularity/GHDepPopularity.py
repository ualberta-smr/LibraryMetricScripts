import requests
from bs4 import BeautifulSoup
import re 
import json  
from scripts.CommonUtilities import Common_Utilities
from scripts.SharedFiles.utility_tool import read_json_file

"""Gets number of dependent repos as calculated by github dependency graph https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-the-dependency-graph#:~:text=The%20dependency%20graph%20is%20a,packages%20that%20depend%20on%20it

	Parameters
	----------
	repo : str
		Github repo represented as user/repo
  
	Returns
	-------
	num_dependents
		number of dependents
"""
def get_num_dependents(repo):
	#inspired from Bertrand Martel's answer on https://stackoverflow.com/questions/58734176/how-to-use-github-api-to-get-a-repositorys-dependents-information-in-github
	url = 'https://github.com/{}/network/dependents'.format(repo)
	dependent_href = '/{}/network/dependents?dependent_type=REPOSITORY'.format(repo)
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")

	if len(soup.body.findAll("We haven’t found any dependents for this repository yet.")) != 0:
		return 0

	dependents = soup.find('a', href= dependent_href) #returns, for example, "1,234,000 Repositories"
	#regex from https://www.regexpal.com/98336
	num_dependents = re.search(r'(\d{0,3},)?(\d{3},)?\d{0,3}', dependents.text.strip()).group(0)
	print(num_dependents)
	return num_dependents

def read_libraries(file_path):
	libdict = {}
	f = read_json_file(file_path)
	for line in f:
		libdict[line['Package']]=line['FullRepoName']          
			
	return libdict

def send_totals_to_file(output_file, keyword, num_found):
	output_file = open(output_file, "a")  
	output_file.write(keyword + ":" + str(num_found) + "\n")
	output_file.close() 

def get_popularity():
	print("Getting popularity")
	config_dict = Common_Utilities.read_config_file() # read all config data  
	
	library_dict = read_libraries(config_dict["LIBRARY_LIST"]) # read all libraries to search against

	output_file_name = config_dict["POPULARITY_OUTPUT_FILE"] # this is the output file that we are going to send libraries with their total counts to
	
	output_file = open(output_file_name, "w")  
	output_file.close()  

	for keyword,repo in library_dict.items():
		print("for lib", repo)  
		num_dependents = get_num_dependents(repo)
		send_totals_to_file(output_file_name, repo, num_dependents)
	   

if __name__ == "__main__":
	get_popularity()