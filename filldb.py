import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'metricwebsite.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metricwebsite.settings")
import django
import pickle
django.setup()

from librarycomparison.models import Domain, Library, Issue, Release

def loadReleaseFrequencyData():
	data = {}
	filename = 'releasefrequency.pkl'
	if os.path.isfile(filename):
		with open(filename, 'rb') as input:
			try:
				print("Loading data")
				data = pickle.load(input)
				print(data)
			except EOFError:
				print("Failed to load pickle file")
	return data

def fillReleaseFrequencyData():
	data = loadReleaseFrequencyData()
	#data is an array of ReleaseData objects 
	for release_data in data:
		library = Library.objects.get(repository=release_data.repository)
		for i in range(0, len(release_data.release_dates)):
			release = Release()
			release.release_date = release_data.release_dates[i]
			release.name = release_data.release_names[i]
			release.breaking_changes = i
			release.library = library
			release.save()
			library.release_set.add(release)
			library.save()

if __name__ == '__main__':
	fillReleaseFrequencyData()