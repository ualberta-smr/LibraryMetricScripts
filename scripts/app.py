from scripts.addlibraries import addlibraries
from scripts.Popularity.GitHub_Phase1 import get_top_repos
from scripts.Popularity.GitHub_Phase2 import search_top_repos
from scripts.ReleaseFrequency.releasefrequency import get_release_freq

def run():
	addlibraries()
	get_top_repos()
	search_top_repos()
	get_release_freq()