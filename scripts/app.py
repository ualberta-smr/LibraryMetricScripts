import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'librarycomparison.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "librarycomparison.settings")
import django
django.setup()
from scripts.addlibraries import addlibraries
from scripts.Popularity.GitHub_Phase1 import get_top_repos
from scripts.Popularity.GitHub_Phase2 import search_top_repos
from scripts.ReleaseFrequency.releasefrequency import get_release_freq
from scripts.License.license import getLicenses
from scripts.LastModificationDate.lastmodificationdate import getLastModificationDates

def run():
	addlibraries()
	get_top_repos()
	search_top_repos()
	get_release_freq()
	getLicenses()
	getLastModificationDates()