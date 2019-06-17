#This file adds libraries from the LibraryData.json file

import os
import sys
import json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'metricwebsite.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metricwebsite.settings")
import django
django.setup()

from librarycomparison.models import Domain,Library


lines = []
with open('LibraryData.json', 'r') as myfile:
    lines = json.loads(myfile.read())    
    
for line in lines:
    library_name = line['LibraryName']
    domain_name = line['Domain']
    repository = line['FullRepoName']
    tag = line['SOtags']    
    
    domain = Domain.objects.filter(name=domain_name)
    if not domain.exists():
        domain = Domain()
        domain.name = domain_name
        domain.save()
    else:
        domain = Domain.objects.get(name=domain_name)
    library = Library.objects.filter(name=library_name)
    if not library.exists():
        library = Library()
        library.name = library_name
        library.tag = tag
        library.repository = repository
        library.domain = domain
        library.save()
        domain.library_set.add(library)
        domain.save()
        
