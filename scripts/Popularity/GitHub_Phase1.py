'''
This script queries for 1000 repositories pushed in the last year. 
This 1000 is a configurable parameter which can be changed from the GitHubSearch.ini file by changing the variable max_size. 
These repo's are sorted from most to least stars. 
Requires:   A configuration file called GitHubSearch.ini
            Ensure a GitHub token generated by your account is in the configuration account so that the script may connect to github 
            
Output:     A text file called Top_repo.txt which has all the 1000 repository full names (which will be used in GitHub_Phase2.py)
'''

import datetime
import random
import sys
from github import Github
from datetime import date
import Common_Utilities

#Outputs all the repositories found into a text file
def output_to_file(repos_file, repo_set):
    file_name = open(repos_file, "a")
    for repo in repo_set:
        file_name.write(str(repo))
        file_name.write("\n")
    file_name.close()
             
#This is where we query for the top repositories 
def query_repo(output_file_name, base_query, github, quick_sleep, error_sleep, max_size):
    
    try: #check github for rate limit 
        rate_limit = github.get_rate_limit()
        rate = rate_limit.search
        print(f'The rate limit is {rate.limit}')
    
        if rate.remaining == 0:
            print(f'You have 0/{rate.limit} API calls remianing. Reset time: {rate.reset}')
            return 
        else:
            print(f'You have {rate.remaining}/{rate.limit} API calls remaining')
      
        print (base_query)
        final_query = base_query
    
        cnt_General = 1
        repo_set = set() 
        
        while cnt_General < max_size:
            print (final_query)
            result = github.search_repositories(final_query, sort='stars', order='desc')
            cnt = 1
            pgno = 1      
            # 300 is how many repo's the script reads at a time (it was kept at 300 as reading more than that may result in a crash of the Github object 
            while cnt <= 300:            
                for repo in result.get_page(pgno):
                    repo_set.add(repo.full_name) 
                    cnt = cnt + 1
                    cnt_General = cnt_General + 1
          
                    stars = repo.stargazers_count
                pgno = pgno + 1  
            final_query =  base_query + " stars:<=" + str(stars)
            Common_Utilities.go_to_sleep("Force to sleep after each iteration, Go to sleep for ", quick_sleep)
        
        output_to_file(output_file_name, repo_set)
        
    
    # error detection, just in case
    except:
        Common_Utilities.go_to_sleep("Error: abuse detection mechanism detected,Go to sleep for ", error_sleep)

#Main function where we set the variables from the configuration file and connect to github 
def main():
    
    config_dict = Common_Utilities.read_ini_file() # read all ini data    
    
    time_span = int(config_dict["TIME_SPAN"])
    start_Date =  date.today() - datetime.timedelta(days=time_span) 
    
    quick_sleep = int (config_dict["QUICK_SLEEP"]) # regular sleep after each iteration
    error_sleep = int (config_dict["ERROR_SLEEP"]) # Sleep after a serious issue is detected from gitHib, should be around 10min, ie 600 sec
    max_size = int (config_dict["MAXSIZE"]) # max pages returned per gitHub call, for now it is 1000, but could be changed in the future
    
    github = None
    github = Github(config_dict["TOKEN"])   # pass the connection token 
    
    output_file_name = "Top_Repo.txt"  # this is the output file that we are going to send repo names to
    
    output_file = open(output_file_name, "w")  
    output_file.close()      
    
    query = "pushed:>" + str(start_Date) + " " + config_dict["SEARCHTERM"]          
    print (query)
   
    query_repo(output_file_name, query, github, quick_sleep, error_sleep, max_size) 
             
    print ("\nFinally ..... Execution is over \n")
      
main()