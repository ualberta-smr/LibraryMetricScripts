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

from releasefrequency import ReleaseData, loadReleaseFrequencyData
from license import loadLicenseData
from lastmodificationdate import loadLastModificationDateData
from lastdiscussedSO import loadLastDiscussedSOData
from issues import loadData, IssueData

def fillPopularityData():
	with open("popularitydata.txt") as f:
		lines = f.readlines()
	lines = [x.strip() for x in lines]

	for line in lines:
		strings = line.split(':')
		library = strings[0]
		popularity = strings[1]
		library = Library.objects.get(name=library)
		library.popularity = int(strings[1])
		library.save()


def fillReleaseFrequencyData():
	Release.objects.all().delete()
	data = loadReleaseFrequencyData()
	#data is an array of ReleaseData objects 
	for repo, release_data in data.items():
		library = Library.objects.get(repository=repo)
		for i in range(0, len(release_data.release_dates)):
			release = Release()
			release.release_date = release_data.release_dates[i]
			release.name = release_data.release_names[i]
			release.breaking_changes = i
			release.library = library
			release.save()
			library.release_frequency = release_data.release_frequency_average
			library.release_set.add(release)
			library.save()


def fillLastModificationDateData():
	data = loadLastModificationDateData()
	for repo, date in data.items():
		library = Library.objects.get(repository=repo)
		library.last_modification_date = date
		library.save()

def fillIssueClosingTimeData():
	data = loadData('issueclosingtime.pkl')
	for repo, closing_time in data.items():
		library = Library.objects.get(repository=repo)
		library.issue_closing_time = closing_time
		library.save()

def fillIssueResponseTimeData():
	data = loadData('issueresponsetime.pkl')
	for repo, response_time in data.items():
		library = Library.objects.get(repository=repo)
		library.issue_response_time = response_time
		library.save()

def fillIssueData():
	Issue.objects.all().delete()
	data = loadData('issuedata.pkl')
	for repo, issues in data.items():
		total_issues = 0
		total_performance_issues = 0
		total_security_issues = 0
		library = Library.objects.get(repository=repo)
		for i in issues:
			total_issues += 1
			issue = Issue()
			issue.issue_id = i.issue_id
			issue.creation_date = i.creation_date
			issue.closing_date = i.closing_date
			issue.first_response_date = i.first_comment_date
			issue.performance_issue = i.performance_issue
			issue.security_issue = i.security_issue
			if issue.performance_issue == True:
				total_performance_issues += 1
			if issue.security_issue == True:
				total_security_issues += 1
			issue.library = library
			issue.save()
			library.issue_set.add(issue)
			library.save()
		library.performance = total_performance_issues/total_issues*100
		library.security = total_security_issues/total_issues*100
		library.save()


def fillLastDiscussedSOData():
	data = loadLastDiscussedSOData()
	print(data)
	for repo, date in data.items():
		library = Library.objects.get(repository=repo)
		library.last_discussed_so = date
		library.save()

def fillLicenseData():
	data = loadLicenseData()
	for repo, license in data.items():
		library = Library.objects.get(repository=repo)
		library.license = license
		library.save()

if __name__ == '__main__':
	fillPopularityData()
	#fillReleaseFrequencyData()
	#fillLastModificationDateData()
	#fillLastDiscussedSOData()
	#fillLicenseData()
	#fillIssueClosingTimeData()
	#fillIssueResponseTimeData()
	#fillIssueData()
