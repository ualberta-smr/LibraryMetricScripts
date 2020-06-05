'''
This script queries for 1000 repositories pushed in the last year. 
This 1000 is a configurable parameter which can be changed from the Config.json file by changing the variable max_size. 
These repo's are sorted from most to least stars. 
Requires:   A configuration file called Config.json
            Ensure a GitHub token generated by your account is in the configuration account so that the script may connect to github 
            
Output:     A text file called Top_repo.txt which has all the 1000 repository full names (which will be used in GitHub_Phase2.py)
'''
#wasn't working on new computer without this
import sys
import os
sys.path.append(os.getcwd())

import datetime
import random
import sys
from github import Github, GithubException
from datetime import date
from CommonUtilities import Common_Utilities

#Outputs all the repositories found into a text file
def output_to_file(repos_file, repo_set):
    print("Writing ", len(repo_set), " repos to file")
    file_name = open(repos_file, "a")
    for repo in repo_set:
        file_name.write(str(repo))
        file_name.write("\n")
    file_name.close()
             
#This is where we query for the top repositories 
def query_repo(output_file_name, base_query, github, quick_sleep, error_sleep, max_size):
    
    repo_set = set()
    try: #check github for rate limit 
        rate_limit = github.get_rate_limit()
        rate = rate_limit.search
        print("The rate limit is %d" % rate.limit)
    
        if rate.remaining == 0:
            print('You have 0/%d API calls remianing. Reset time: %d' % (rate.limit, rate.reset ))
            Common_Utilities.go_to_sleep("Reached API limit per minute, Going to sleep for ", quick_sleep) 
        else:
            print('You have %d/%d API calls remaining' % (rate.remaining/rate.limit))
      
        print ('Base query: %' % base_query)
        curr_query = base_query + " stars:>100"

            
           
        while len(repo_set) < max_size:
            print ("Collected ", len(repo_set), " repos so far")
            print (curr_query)
            result = github.search_repositories(curr_query, sort='stars', order='desc')
            cnt = 0
            pgno = 1      
            
            # 300 is how many repo's the script reads at a time (it was kept at 300 as reading more than that may result in a crash of the Github object 
            while cnt <= 300:
                try:          
                    for repo in result.get_page(pgno):
                        repo_set.add(repo.full_name) 
                        cnt = cnt + 1
          
                        stars = repo.stargazers_count

                        if len(repo_set) == max_size:
                            break
                except:
                    Common_Utilities.go_to_sleep("API limit exceeded, Going to sleep for ", quick_sleep)
                    continue

                if len(repo_set) == max_size:
                    break

                pgno = pgno + 1  
            
            curr_query =  base_query + " stars:100.." + str(stars)
            

        output_to_file(output_file_name, repo_set)

    # error detection, just in case
    except Exception as e:
        output_to_file(output_file_name, repo_set)
        print("Error: abuse detection mechanism detected.. outputting what we have...")
        print(e)

#Main function where we set the variables from the configuration file and connect to github 
def main():

    print("Retrieving list of top repos... \n")
    
    config_dict = Common_Utilities.read_config_file() # read all ini data    
    
    #find top repos that have pushed in the last X days
    time_span = int(config_dict["TIME_SPAN"]) 
    push_date =  date.today() - datetime.timedelta(days=time_span) 
    
    quick_sleep = int (config_dict["QUICK_SLEEP"]) # regular sleep after each iteration
    error_sleep = int (config_dict["ERROR_SLEEP"]) # Sleep after a serious issue is detected from gitHib, should be around 10min, ie 600 sec
    max_size = int (config_dict["MAXSIZE"]) # maximum number of repos to look for (top X); configured in config file
    
    github = None
    github = Github(config_dict["TOKEN"])   # pass the connection token 
    
    output_file_name = "Popularity/Top_Repo.txt"  # this is the output file that we are going to send repo names to
    
    output_file = open(output_file_name, "w")  
    output_file.close()      
    
    query = "pushed:>" + str(push_date) + " " + config_dict["REPO_SEARCH_QUERY"]          
    print (query)
   
    query_repo(output_file_name, query, github, quick_sleep, error_sleep, max_size) 
             
    print ("\nFinally ..... Execution is over \n")
      
main()