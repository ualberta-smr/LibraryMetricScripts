#THIS is not the final product, I will fix it up and add proper comments when done. Some of these comments are just for myself to keep track so if they don't make sense then just ask :)

#This code is for the popularity metric for the Library comparison website. It takes libraries from the library.txt file and variables from an ini file and retreives the number of times that each library was imported in Github in the previous year. 

import time
import datetime
import random
import sys
from github import Github
from datetime import date


# This is the main call for gitHub Object      
def gitHubStep1(f, termdic, QUERY, g, sleep1, sleep2, max_size):
  listwords = []
  
  #check github for rate limit 
  try:  
    rate_limit=g.get_rate_limit()
    rate = rate_limit.search
    
    #this reate limit is not accurate as github may stop you before you reach your limit.
    print ("search limit: " + str(rate) + ". Reset Time: " + str(rate.reset))
    if rate.remaining == 0:        
      GotoSleep("No more resources to use, Go to sleep for ", sleep2)  
    
    print(QUERY)
    result = None
    result = g.search_code(QUERY, order='desc')  
    
    # Error detection (just in case)
    try:
      msgbox = "Found " + str(result.totalCount) + " file(s)"
      print(msgbox)
    except:
      GotoSleep("Error Detected in files found, Go to sleep for ", sleep1) #I think change this to sleep2 i.e. 10 minutes, might make more sense --> test it out and see
            
    returnValue = result.totalCount
    if result.totalCount >= max_size:    
      print ("Error: max size exceeded ")
      return returnValue
    else:      
      #work from here with the github object
      result = result[:result.totalCount]      
      for file in result: 
        #stripResuls will remove any un-needed parts in the url link, keeping username/repository only
        listwords.append(stripResuls(file.download_url)) 
           
  except:
    GotoSleep("Error: abuse detection mechanism detected, Go to sleep for ", sleep2)
    
    return -1 # -1 means a problem was detected and we need to re-read the same pages again after sleep. Date will not be changed.
  
  outputtofile(f, termdic, listwords)  
      
  return returnValue

# sleep function as GitHub does not like frequent calls.
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

# output all found repositories into text files, one per library
def outputtofile(f, termdic, listwords):
    for word in listwords:
      filename = open(f, "a")
      filename.write(word)
      filename.write("\n")
      filename.close()
      # dict is used to force uniquness among reposirty/user
      termdic[word] = 0
          
# stripResuls will remove any none needed parts in the url link, keeping repositry name with useronly
def stripResuls(txt):
    
    x = txt.index(".com/")
    txt = txt[x+5:]
    x = txt.index("/")
    part1 = txt[:x]
    txt = txt[x+1:]
    x = txt.index("/")
    word = part1+ "/" + txt[:x]
    return word

# main gitHubCall, if the results are larger than the max size allowed per call, Re-call it again with smaller interval time (for now, hardcoded to 1 day).

#UPDATE THIS FUNCTION TO FIX THE QUERY SO THAT IT DOES NOT HAVE THE END DATE AND ADD PUSHED!!!-----------

def gitHubCall(f, termdic, current, interval,term, g, sleep1, sleep2, max_size):    
    Q_sub = term + "  " + formatDate(current,interval) 
    noofresults = gitHubStep1(f, termdic, Q_sub, g, sleep1, sleep2, max_size)
    
    if noofresults >= max_size:
        increment = 1
        print ("Exceeds max ")
        while increment < interval:
            Q_sub = term + "  " + formatDate(current,1)   
            noofresults = gitHubStep1(f, termdic, Q_sub, g, sleep1, sleep2, max_size)
            if (noofresults>-1):
              current = current + datetime.timedelta(days=1)
              increment = increment + 1
      
    return noofresults        
        
# show in string format the current range of dates the system is searching against in the current iteration
def formatDate(tempDate,interval):
    return str(tempDate) + " .. " + str(tempDate + datetime.timedelta(days=interval))


def QueryDates(f, termdic, current_Date, end_Date, interval,term, g, sleep1, sleep2, max_size):
     
    while (current_Date <= end_Date):
        
        x = gitHubCall(f, termdic, current_Date, interval,term, g, sleep1, sleep2, max_size)
        if x > -1:
          current_Date = current_Date + datetime.timedelta(days=interval)          
          GotoSleep("Force to sleep after each iteration, Go to sleep for ", sleep1)
                   


# function to open and read the text file that has all libraries    
def readLibraries(filenameLib):
    array = []
    with open(filenameLib, "r") as f:
        for line in f:
            array.append(line.rstrip())   
    return array

# save each library and its frequency in the provided search range
def sendtotalstofile(fout, keyword, nofound):
  fout = open(fout, "a")  
  fout.write(keyword + ":" + str(nofound) + "\n")
  fout.close()  

# read the ini file data into dict.
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

# convert string date to date object
def paersedate(line):
    
    line = line.rstrip()
    loc = line.index("/")
    keyword = line[:loc]
    line = line[loc+1:]
    c_year = int(keyword)
    
    loc = line.index("/")
    keyword = line[:loc]
    line = line[loc+1:]
    c_month = int(keyword)
    c_day = int(line)
    
    return (date(c_year, c_month, c_day))
  
def main():
    
    dictContst = readIniFile() # read all ini data
    
    if dictContst["YEARLY"] == "FALSE":
      start_Date = paersedate(dictContst["STARTDATE"])    # start date of the search
      end_Date = paersedate(dictContst["ENDDATE"])    # enddate date of the search
    else:
      start_Date =  datetime.datetime.now() - datetime.timedelta(days=365)
      end_Date = datetime.datetime.now()
      
    Size1 = int(dictContst["SIZE1"])
    Size2 = int(dictContst["SIZE2"])
    
    start_Date = paersedate(dictContst["STARTDATE"])    # start date of the search
    end_Date = paersedate(dictContst["ENDDATE"])    # enddate date of the search
    sleep1 = int (dictContst["SLEEP1"]) # regular sleep after each iteration
    sleep2 = int (dictContst["SLEEP2"]) # Sleep after a serious issue is detected from gitHib, should be around 10min, ie 600 sec
    max_size = int (dictContst["MAXSIZE"]) # max pages returned per gitHub call, for now it is 1000, but could be changed in the future
    
    g = None
    g = Github(dictContst["TOKEN"])   # pass the connection token 
    
    interval = int(dictContst["INTERVAL"]) # the time span between each iteration
    current_Date = start_Date # this is the current date that will change by interval after each successful iteration
    
    #Maps results to their respective libraries and outputs the results into popularity_results.txt
    resultDict = readLibraries(configDict["LIBRARY"]) # read all libraries to search against
    foutname = "popularity_results.txt"  # this is the output file that we are going to send libraries with their total counts to. No duplications here
   
    fout = open(foutname, "w")  
    fout.close()  
    
    for keyword,repo in resultDict.items(): 
      f = "Results-" + keyword + ".txt"  # this is a text file that will contain all repository founds per library, duplication occurs here
      term = "\"import " + keyword + "\" in:file" + " " + configDict["SEARCHTERM"]          
      filename = open(f, "w")
      filename.close()
      termdic = {}
      QuerySize(f, termdic, current_Date, end_Date, interval,term, g, sleep1, sleep2, max_size,Size1,Size2) 
      sendtotalstofile(foutname, repo, len(termdic.keys()))
             
    print ("\nFinally... Execution is over \n")

main()
