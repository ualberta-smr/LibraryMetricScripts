#This file adds libraries from the librarydata.txt file

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'metricwebsite.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metricwebsite.settings")
import django
django.setup()

from librarycomparison.models import Domain,Library

with open('librarydata.txt') as f:
    lines = f.readlines()
lines = [x.strip() for x in lines]

for line in lines:
    content = line.split(',')
    library_name = content[0]
    domain_name = content[1]
    repository = content[2]
    tag = content[3]
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
        
