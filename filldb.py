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
from datetime import datetime, timezone

def fillPopularityData():
        with open("popularity_results.txt") as f:
                lines = f.readlines()
        lines = [x.strip() for x in lines]

        for line in lines:
                strings = line.split(':')
                repository = strings[0]
                popularity = strings[1]
                library = Library.objects.get(repository=repository)
                library.popularity = int(strings[1])
                library.save()

def fillReleaseFrequencyData():
        Release.objects.all().delete()
        data = loadReleaseFrequencyData()
        #data is an array of ReleaseData objects 
        for repo, release_data in data.items():
                library = Library.objects.get(repository=repo)
                library.breaking_changes = 0
                for i in range(0, len(release_data.release_dates)):
                        release = Release()
                        release.release_date = release_data.release_dates[i]
                        release.name = release_data.release_names[i]
                        release.breaking_changes = 0
                        release.library = library
                        release.save()
                        library.release_frequency = release_data.release_frequency_average
                        library.release_set.add(release)
                        library.save()


def fillLastModificationDateData():
	data = loadLastModificationDateData()
	for repo, dates in data.items():
		library = Library.objects.get(repository=repo)
		library.last_modification_dates = dates
		library.last_modification_date = datetime.strptime(dates.split(';')[0], '%m/%d/%Y')
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
                        issue.issue_id = str(i.issue_id)
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
        for tag, dates in data.items():
                print(tag)
                library = Library.objects.get(tag=tag)
                if(dates != None):
                        library.last_discussed_so = datetime.strptime(dates.split(';')[0], '%m/%d/%Y')
                        library.last_discussed_so_dates = dates
                else:
                        library.last_discussed_so = datetime.now()
                        library.last_discussed_so_dates = ''
                library.save()

def fillLicenseData():
	data = loadLicenseData()
	for repo, license in data.items():
		library = Library.objects.get(repository=repo)
		library.license = license
		library.save()


def fillBreakingChanges():
        with open("breakingchanges/breakingchanges.csv") as f:
                lines = f.readlines()
        lines = [x.strip() for x in lines]

        i = 0
        while i < len(lines):
                print(lines[i])
                splitline = lines[i].split(":")
                print(splitline)
                library = splitline[0]
                release = splitline[1]
                if release == '':
                        i += 2
                        continue
                if ';' not in lines[i+1]:
                        i += 1
                        allbreakingchanges = 0
                        allnonbreakingchanges = 0
                else:
                        splitline = lines[i+1].split(";")
                        allbreakingchanges = int(splitline[5])
                        allnonbreakingchanges = int(splitline[10])
                        i += 2
                target_library = Library.objects.get(name=library)
                target_release = target_library.release_set.all().get(name=release)
                target_release.breaking_changes = allbreakingchanges
                target_release.save()
                target_library.breaking_changes += allbreakingchanges
                target_library.non_breaking_changes += allnonbreakingchanges
                target_library.save()

        for library in Library.objects.all():
                release_count = library.release_set.all().count()
                if release_count == 0:
                        library.backwards_compatibility = 0
                else:
                        library.backwards_compatibility = library.breaking_changes/library.release_set.all().count()
                library.save()

def fillOverallScore():
        highestPopularity = 0
        number_of_metrics = 8
        max_score_value = 5

        for library in Library.objects.all():
                highestPopularity = max(highestPopularity, library.popularity)

        for library in Library.objects.all():
                score = 0.0
                score += library.popularity/max(1, highestPopularity)
                score += max(0, 1-library.release_frequency/365)
                score += max(0, 1-library.issue_closing_time/365)
                score += max(0, 1-library.issue_response_time/365)
                score += max(0, 1- (int((datetime.now(timezone.utc) - library.last_modification_date).total_seconds())/86400/365))
                score += library.non_breaking_changes/max(1,(library.breaking_changes+library.non_breaking_changes))
                score += (100-library.performance)/100
                score += (100-library.security)/100
                library.overall_score = score*max_score_value/number_of_metrics
                library.save()

if __name__ == '__main__':
        #fillPopularityData()
        #fillReleaseFrequencyData()
        #fillBreakingChanges()
        #fillLastModificationDateData()
        #fillLastDiscussedSOData()
        ##fillLicenseData()
        #fillIssueClosingTimeData()
        #fillIssueResponseTimeData()
        #fillIssueData()
        fillOverallScore()
