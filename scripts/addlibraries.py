#This file adds libraries from the LibraryData.json file

#This makes the utility_tool visible from this file
import sys
from scripts.SharedFiles.utility_tool import read_json_file

import json
import datetime 
from librarycomparison.models import Domain,Library

def addlibraries():
    lines = []
    date = datetime.date.today()
    entrymonth = date.month
    entryyear = date.year

    repositories = []
    libraries = read_json_file("scripts/SharedFiles/LibraryData.json")
        
    for entry in libraries:
        domain_name = entry['Domain']
        library_name = entry['LibraryName']

        domain = Domain.objects.filter(name=domain_name)
        if not domain.exists():
            domain = Domain()
            domain.name = domain_name
            domain.save()
        else:
            domain = Domain.objects.get(name=domain_name)
        
        library = Library.objects.filter(name=library_name)
        
        #create new lib if it doesn't exist. Otherwise, update entry
        if not library.exists():
            library = Library()
        else:
            library = Library.objects.get(name=library_name)
        
        library.name = library_name
        library.so_tag = entry['SOtags']
        library.domain = domain
        library.package = entry['Package']
        library.github_repo = entry['FullRepoName']
        library.github_url = entry['GitHubURL']
        library.jira_url = entry['JIRAURL']
        library.save()

if __name__ == "__main__":
    addlibraries()