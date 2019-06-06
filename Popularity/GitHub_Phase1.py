'''
This script queries for 1500 repositories pushed in the last year 
These repo's are sorted from most to least stars. 

Requires:   A configuration file called GitHubSearch.ini
            Ensure a GitHub token generated by your account is in the configuration account so that the script may connect to github 
            
Output:     A text file called Top_repo.txt which has all the 1500 repository full names (which will be used in GitHub_Phase2.py)
'''

import time
import datetime
import random
import sys
from github import Github
from datetime import date


#This is a sleep function so pause the script since GitHub does not allow frequent calls.
def GotoSleep (msg, timeofSleep):
  
  ts = time.time()
  st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')   
  ErrorMsg = "....    " + msg + str(timeofSleep) + " seconds, Sleeping @ " + st
  print (ErrorMsg) 
  
  time.sleep( timeofSleep )  # actual Sleep
  
  ts = time.time()  
  st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') 
  ErrorMsg = "....    " + "Waked up @ " + st
  print (ErrorMsg) 


#Outputs all the repositories found into a text file
def outputtofile(f, repo):
    filename = open(f, "a")
    filename.write(str(repo))
    filename.write("\n")
    filename.close()
        
       
#This is where we query for the top repositories 
def QueryRepo(foutname, interval,QUERY, g, sleep1, sleep2, max_size):
   
  #check github for rate limit 
  try:
    
    #check github for rate limit 
    rate_limit =g.get_rate_limit()
    rate = rate_limit.search
    print("The rate limit is "+ str(rate.limit))
    if rate.remaining == 0:
      print(f'You have 0/{rate.limit} API calls remianing. Reset time: {rate.reset}')
      return 
    else:
      print(f'You have {rate.remaining}/{rate.limit} API calls remaining')
      
    # max_size
    print (QUERY)
    Final_Q = QUERY
    
    cnt_General = 1
    while cnt_General < max_size:
      print (Final_Q)
      result = g.search_repositories(Final_Q, sort='stars', order='desc')
      cnt = 1
      pgno = 1      
      while cnt <= 300:            
        for repo in result.get_page(pgno):
          outputtofile(foutname, repo.full_name)
          #res = str(pgno)+ "--" + str(cnt)+ ":" + repo.full_name + "("+str(repo.stargazers_count)+")"
          cnt = cnt + 1
          cnt_General = cnt_General + 1
          
          #res is the results THIS IS ONLY HERE FOR NOW so that I can see the script results during the run  
          res = str(cnt_General)+ ":" + str(cnt) + "in page " + str(pgno) + " Stars " + str(repo.stargazers_count) 
          print(res)
          
          stars = repo.stargazers_count
        pgno = pgno + 1  
      Final_Q =  QUERY + " stars:<" + str(stars)
   
      GotoSleep("Force to sleep after each iteration, Go to sleep for ", sleep1)

    # error detection, just in case
  except:
    GotoSleep("Error: abuse detection mechanism detected,Go to sleep for ", sleep2)
    
    return -1 # -1 means a problem detected and we need to re-read the same pages again after sleep
  
#Reads the ini file data into dict.
#NOTE TO SELF: REMOVE THIS FUNCTION AND ADD A LIBRARY THAT CAN DO THIS FOR ME ----------
def readIniFile():
    dictKeys = {}
    with open("GitHubSearch.ini", "r") as f:
        for line in f:
            line = line.rstrip()
            loc = line.index("]")
            keyword = line[1:loc]
            line = line[loc+2:]
            loc = line.index("]")
            valuekey = line[:loc]
            dictKeys[keyword] = valuekey
    return dictKeys

#Main function where we set the variables from the configuration file and connect to github 
def main():
    
    dictContst = readIniFile() # read all ini data    
    start_Date =  date.today() - datetime.timedelta(days=365) 
    
    sleep1 = int (dictContst["SLEEP1"]) # regular sleep after each iteration
    sleep2 = int (dictContst["SLEEP2"]) # Sleep after a serious issue is detected from gitHib, should be around 10min, ie 600 sec
    interval = int(dictContst["INTERVAL"]) # the time span between each iteration
    max_size = int (dictContst["MAXSIZE"]) # max pages returned per gitHub call, for now it is 1000, but could be changed in the future
    
    g = None
    g = Github(dictContst["TOKEN"])   # pass the connection token 
    
    foutname = "Top_Repo.txt"  # this is the output file that we are going to send libraries with their total counts to. No duplications here
    
    fout = open(foutname, "w")  
    fout.close()      
    
    Query = "pushed:>" + str(start_Date) + " " + dictContst["SEARCHTERM"]          
    print (Query)
   
    QueryRepo(foutname, interval, Query, g, sleep1, sleep2, max_size) 
             
    print ("\n Finally ..... Execution is over \n")
      
main()