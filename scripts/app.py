import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'librarycomparison.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "librarycomparison.settings")
import django
django.setup()
from scripts.addlibraries import addlibraries
from scripts.CommonUtilities import Common_Utilities
from scripts.Popularity.GitHub_Phase1 import get_top_repos
from scripts.Popularity.GitHub_Phase2 import search_top_repos
from scripts.ReleaseFrequency.releasefrequency import get_release_freq
from scripts.License.license import getLicenses
from scripts.LastModificationDate.lastmodificationdate import getLastModificationDates
from scripts.LastDiscussedOnStackOverflow.lastdiscussedSO import getLastDiscussedDates
from scripts.IssueMetrics.issues import get_issues
from scripts.BreakingChanges.breakingchanges import get_breaking_changes
from scripts.filldb import filldb
import shutil
import glob
import os
import subprocess

def run():
    addlibraries()
    get_top_repos()
    search_top_repos()
    get_release_freq()
    getLicenses()
    getLastModificationDates()
    getLastDiscussedDates()
    get_issues()
    get_breaking_changes() #must be called after releases are fetched so after release frequency metric
 
    config_dict = Common_Utilities.read_config_file()
    output_path = config_dict["OUTPUT_PATH"]

    shutil.copy2('scripts/Popularity/popularity_results.txt', output_path)
    
    for file in glob.glob(r'scripts/License/*.pkl'):
        shutil.copy2(file, output_path)

    for file in glob.glob(r'scripts/LastModificationDate/*.pkl'):
        shutil.copy2(file, output_path)

    for file in glob.glob(r'scripts/LastDiscussedOnStackOverflow/*.pkl'):
        shutil.copy2(file, output_path)

    filldb()

    try:
        os.mkdir(output_path + "charts")
    except:
        print("Charts directory already exists")

    for file in glob.glob(output_path + r'*_chart.pkl'):
        shutil.copy2(file, output_path + "charts")

    for file in glob.glob(output_path + r'*.pkl'):
        os.remove(file)

    os.remove(output_path + "popularity_results.txt")
