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
from scripts.LastDiscussedOnStackOverflow.lastdiscussedSO import getLastDiscussedDates
from scripts.IssueMetrics.issues import get_issues
from scripts.filldb import filldb
import shutil
import glob
import os

def run():
	addlibraries()
	get_top_repos()
	search_top_repos()
	get_release_freq()
	getLicenses()
	getLastModificationDates()
	getLastDiscussedDates()
	get_issues()
	#TODO: breaking changes

	shutil.copy2('scripts/Popularity/popularity_results.txt', 'scripts/')
	for file in glob.glob(r'scripts/License/*.pkl'):
		shutil.copy2(file, 'scripts/')

	for file in glob.glob(r'scripts/LastModificationDate/*.pkl'):
		shutil.copy2(file, 'scripts/')

	for file in glob.glob(r'scripts/LastDiscussedOnStackOverflow/*.pkl'):
		shutil.copy2(file, 'scripts/')

	filldb()

	for file in glob.glob(r'scripts/*_chart.pkl'):
		shutil.copy2(file, 'scripts/charts/')

	for file in glob.glob(r'scripts/*.pkl'):
		os.remove(file)

	os.remove("scripts/popularity_results.txt")