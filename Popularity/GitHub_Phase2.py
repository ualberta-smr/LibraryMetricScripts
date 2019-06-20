'''
This script searches the 1500 repositories in Top_Repo.txt for import statements of all the library packages in library.txt
Requires:   A configuration file called GitHubSearch.ini
            Ensure a GitHub token generated by your account is in the configuration account so that the script may connect to github 
            
Output:     A text file called popularity_results.txt which has each library along with a number representing how many distinct repositories it was in 
'''

import random
from github import Github
import json  
import Common_Utilities

#This makes the utility_tool visible from this file
import sys
sys.path.append('../')
from SharedFiles.utility_tool import read_json_file

#This is where the search happens, an api query is used to collect results. 
#The query looks like this: "import LIBRARY-NAME" language:java repo:REPO-NAME
#For each Query, if we get ANY results then that means the library was used in that repo
#If we get ZERO results, it means it was not used in that repo
def search_code_in_repo(query, github, quick_sleep, error_sleep, max_size, Repo_Array):
   
  roll_back = True
  while roll_back:
    roll_back = False
    frequency = 0
    #check github for rate limit 
    try:
    
      rate_limit = github.get_rate_limit()
      rate = rate_limit.search            
      # this reate limit is not accurate as github may stop you before you reach your limit.
      print ("search limit: " + str(rate) + ". Reset Time: " + str(rate.reset))
      if rate.remaining == 0:
        #print(f'You have 0/{rate.limit} API calls remianing. Reset time: {rate.reset}')            
        Common_Utilities.go_to_sleep("No more resources to use, Go to sleep for ", error_sleep)  
           
      index = 0
      tracking_counter = 1
      arraysize = len(Repo_Array)     
      while index < arraysize:      
        try:
          tracking_counter = tracking_counter + 1                    
          query_final = query + " repo:"+Repo_Array[index] 
          index = index + 1
          msg = str(index) + " out of " + str (arraysize) + " Query : " + query_final
          print (msg)
          result = None
          result = github.search_code(query_final)        
          num_found = result.totalCount      
          if  num_found > 0:
            frequency =  frequency + 1      
          if tracking_counter % 15 == 0:
            Common_Utilities.go_to_sleep("Force to sleep after each iteration, Go to sleep for ", quick_sleep)          
        except:             
          index = index - 1
          Common_Utilities.go_to_sleep("Error: Internal abuse detection mechanism detected,Go to sleep for ", error_sleep)
      
    except:
      Common_Utilities.go_to_sleep("Error: abuse detection mechanism detected,Go to sleep for ", error_sleep)
      roll_back = True # -1 means a problem detected and we need to re-read the same pages again after sleep. no change of date
   
  return frequency 
   
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

def read_repos():
    repo_array = []
    with open("Top_Repo.txt", "r") as f:
        for line in f:          
            repo_array.append(line.rstrip())
    return repo_array
  
def main():
    
    config_dict = Common_Utilities.read_ini_file() # read all ini data
    repo_array = read_repos()    
    
    quick_sleep = int (config_dict["QUICK_SLEEP"]) # regular sleep after each iteration
    error_sleep = int (config_dict["ERROR_SLEEP"]) # Sleep after a serious issue is detected from gitHib, should be around 10min, ie 600 sec
    max_size = int (config_dict["MAXSIZE"]) # max number of results returned per gitHub call, for now it is 1500, but could be changed in the future
    
    g = None
    g = Github(config_dict["TOKEN"])   # pass the connection token 
    
    library_dict = read_libraries(config_dict["LIBRARY_LIST"]) # read all libraries to search against

    output_file_name = config_dict["OUTPUT_FILE"] # this is the output file that we are going to send libraries with their total counts to
    
    output_file = open(output_file_name, "w")  
    output_file.close()  
    
    for keyword,repo in library_dict.items():  
      
      query = "\"import " + keyword + "\" "  + config_dict["SEARCHTERM"]  
      frequency = search_code_in_repo(query, g, quick_sleep, error_sleep, max_size, repo_array) 
      send_totals_to_file(output_file_name, repo, frequency )
       
    print ("\n Finally ..... Execution is over \n")    
    
main()