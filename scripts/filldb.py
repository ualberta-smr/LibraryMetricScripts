import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'librarycomparison.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "librarycomparison.settings")
import django
import pickle
import pygal
django.setup()

from librarycomparison.models import Domain, Library, Issue, Release, Data

from ReleaseFrequency.releasefrequency import ReleaseData, loadReleaseFrequencyData
from License.license import loadLicenseData
from LastModificationDate.lastmodificationdate import loadLastModificationDateData
from LastDiscussedOnStackOverflow.lastdiscussedSO import loadLastDiscussedSOData
from IssueMetrics.issues import loadData, IssueData
from datetime import datetime, timezone, date
from dateutil.relativedelta import *

def saveData(data, filename):
  with open(filename, 'wb') as output:
    pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

def create_date_range(start_date, end_date):
  
  months = ['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
  
  date_ranges = []
  my_date = start_date
  
  while my_date <= end_date:
    msg = months[my_date.month-1]
    msg = msg + " '" + str(my_date.year)[2:]
    date_ranges.append(msg)
    my_date = my_date + relativedelta(months=+1) 
  
  return date_ranges

def create_popularity_chart(domain,entrymonth,entryyear):
  
  line_chart  = pygal.Line(x_label_rotation=45, height=200, width=1000)
  selected_domain = Domain.objects.get(name=domain)  
  
  end_date = datetime(2021, 2, 1) #datetime.now() 
  
  default_start_date = datetime(2019, 6, 1)
  start_date = end_date + relativedelta(months=-24)
  
  if start_date < default_start_date:
    start_date = default_start_date
  
  libraries = selected_domain.data_set.filter(run_time__gte=start_date).filter(run_time__lte=end_date).order_by('year').order_by('month')
 
  domain_dic = {}
  for library in libraries:    
    
    if library.name in domain_dic.keys():
      domain_dic[library.name].append(library.popularity)
    else:
      popularity_data_arr = []
      popularity_data_arr.append(library.popularity)
      domain_dic[library.name] = popularity_data_arr
  
  line_chart.x_labels = map(str, create_date_range(start_date,end_date))
  line_chart.title = domain 
  for keys, values in domain_dic.items():    
    line_chart.add(keys, values)
  
  data = line_chart.render_data_uri()
  line_chart.render_in_browser()
  saveData(data, domain + '_popularity_chart.pkl')
  
  return data

def create_release_chart(domain):
	line_chart = pygal.Line(x_label_rotation=90, height = 200, show_minor_x_labels=False)
	selected_domain = Domain.objects.get(name=domain)
	libraries = selected_domain.library_set.all()
	releases_dict = {}
	release_date_set = set()
	for release in Release.objects.all():
		release_date_set.add(release.release_date)

	release_date_list = sorted(list(release_date_set))
	line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), release_date_list)
	line_chart.x_labels_major = [release_date_list[0].strftime('%b %d %Y'), release_date_list[-1].strftime('%b %d %Y')]
	line_chart.title = 'Timeline of Releases'

	library_id = 1
	y_labels = []

	for library in libraries:
		releases = library.release_set.all()
		release_list = []
		for i in range(0, len(release_date_list)):
			found = False;
			for j in range(0, len(releases)):
				if release_date_list[i] == releases[j].release_date:
					print(library.name)
					found = True
					release_list.append(library_id)
					break
			if found == False:
				release_list.append(None)
		line_chart.add(library.name, release_list)
		y_labels.append({'label' : library.name, 'value' : library_id})
		library_id += 1
	line_chart.y_labels = y_labels
	data = line_chart.render_data_uri()
	saveData(data, domain + '_release_chart.pkl')
	return data

def parseDateString(date_string):
	strings = date_string.split(';')
	dates = []
	for date in strings:
		dates.append(datetime.strptime(date, '%m/%d/%Y'))
	return dates

def create_last_discussed_chart(domain):
        line_chart = pygal.Line(x_label_rotation=90, height = 200, show_minor_x_labels=False, dots_size=5)
        selected_domain = Domain.objects.get(name=domain)
        libraries = selected_domain.library_set.all()
        date_set = set()
        for library in libraries:
                print(library.name)
                print(library.last_discussed_so_dates)
                if library.last_discussed_so_dates == '':
                        continue
                dates = parseDateString(library.last_discussed_so_dates)
                date_set.update(dates)

        date_list = sorted(list(date_set))
        line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), date_list)
        line_chart.x_labels_major = [date_list[0].strftime('%b %d %Y'), date_list[-1].strftime('%b %d %Y')]
        line_chart.title = 'The last 10 questions were asked in these dates:'

        library_id = 1
        y_labels = []

        for library in libraries:
                if library.last_discussed_so_dates == '':
                        continue
                dates = parseDateString(library.last_discussed_so_dates)
                question_list = []
                for i in range(0, len(date_list)):
                        found = False;
                        for j in range(0, len(dates)):
                                if date_list[i] == dates[j]:
                                        found = True
                                        question_list.append(library_id)
                                        break
                        if found == False:
                                question_list.append(None)
                line_chart.add(library.name, question_list)
                y_labels.append({'label' : library.name, 'value' : library_id})
                library_id += 1
        line_chart.y_labels = y_labels
        data = line_chart.render_data_uri()
        saveData(data, domain + '_last_discussed_chart.pkl')
        return data

def create_last_modification_chart(domain):
	line_chart = pygal.Line(x_label_rotation=90, height = 200, show_minor_x_labels=False, dots_size=5)
	selected_domain = Domain.objects.get(name=domain)
	libraries = selected_domain.library_set.all()
	date_set = set()
	for library in libraries:
		print(library.name)
		print(library.last_modification_dates)
		dates = parseDateString(library.last_modification_dates)
		date_set.update(dates)

	date_list = sorted(list(date_set))
	line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), date_list)
	line_chart.x_labels_major = [date_list[0].strftime('%b %d %Y'), date_list[len(date_list)//2].strftime('%b %d %Y'), date_list[-1].strftime('%b %d %Y')]
	line_chart.title = 'The last 10 modifications were done in these dates:'

	library_id = 1
	y_labels = []

	for library in libraries:
		dates = parseDateString(library.last_modification_dates)
		modification_list = []
		for i in range(0, len(date_list)):
			found = False;
			for j in range(0, len(dates)):
				if date_list[i] == dates[j]:
					found = True
					modification_list.append(library_id)
					break
			if found == False:
				modification_list.append(None)
		line_chart.add(library.name, modification_list)
		y_labels.append({'label' : library.name, 'value' : library_id})
		library_id += 1
	line_chart.y_labels = y_labels
	data = line_chart.render_data_uri()
	saveData(data, domain + '_last_modification_chart.pkl')
	return data

def create_breaking_changes_chart(domain):
	line_chart = pygal.Line(x_label_rotation=90, show_minor_x_labels=False)
	selected_domain = Domain.objects.get(name=domain)
	libraries = selected_domain.library_set.all()
	releases_dict = {}
	release_date_set = set()
	for release in Release.objects.all():
		release_date_set.add(release.release_date)

	release_date_list = sorted(list(release_date_set))
	line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), release_date_list)
	line_chart.x_labels_major = [release_date_list[0].strftime('%b %d %Y'), release_date_list[len(release_date_list)//2].strftime('%b %d %Y'),
	  release_date_list[-1].strftime('%b %d %Y')]
	line_chart.title = 'Breaking Changes in Releases. X_axis = Release Dates, Y_axis = Number of Breaking changes'

	for library in libraries:
		releases = library.release_set.all()
		release_list = []
		for i in range(0, len(release_date_list)):
			found = False;
			for j in range(0, len(releases)):
				if release_date_list[i] == releases[j].release_date:
					print(library.name)
					found = True
					release_list.append(releases[j].breaking_changes)
					#break
			if found == False:
				release_list.append(None)
		line_chart.add(library.name, release_list)
		print(library.name, len(release_list))
	data = line_chart.render_data_uri()
	saveData(data, domain + '_breaking_changes_chart.pkl')
	return data

def create_issue_response_chart(domain):
	line_chart = pygal.Line(x_label_rotation=90, show_minor_x_labels=False, height=300)
	selected_domain = Domain.objects.get(name=domain)
	libraries = selected_domain.library_set.all()
	issue_date_set = set()
	for issue in Issue.objects.all():
		if issue.first_response_date != None:
			issue_date_set.add(issue.creation_date)

	issue_date_list = sorted(list(issue_date_set))
	line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), issue_date_list)
	line_chart.x_labels_major = [issue_date_list[0].strftime('%b %d %Y'),
	  issue_date_list[-1].strftime('%b %d %Y')]
	line_chart.title = 'Issue Response Times. X_axis = issue creation date, Y_axis = number of days to respond'

	for library in libraries:
		issues = library.issue_set.all()
		issue_list = []
		for i in range(0, len(issue_date_list)):
			found = False;
			for j in range(0, len(issues)):
				if issues[j].first_response_date != None and issue_date_list[i] == issues[j].creation_date:
					found = True
					issue_list.append(int((issues[j].first_response_date - issues[j].creation_date).total_seconds())/86400)
			if found == False:
				issue_list.append(None)
		line_chart.add(library.name, issue_list)
	data = line_chart.render_data_uri()
	saveData(data, domain + '_issue_response_chart.pkl')
	return data

def create_issue_closing_chart(domain):
	line_chart = pygal.Line(x_label_rotation=90, show_minor_x_labels=False, height=300)
	selected_domain = Domain.objects.get(name=domain)
	libraries = selected_domain.library_set.all()
	issue_date_set = set()
	for issue in Issue.objects.all():
		if issue.first_response_date != None:
			issue_date_set.add(issue.creation_date)

	issue_date_list = sorted(list(issue_date_set))
	line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), issue_date_list)
	line_chart.x_labels_major = [issue_date_list[0].strftime('%b %d %Y'),
	  issue_date_list[-1].strftime('%b %d %Y')]
	line_chart.title = 'Issue Closing Times. X_axis = issue creation date, Y_axis = number of days to close'

	for library in libraries:
		issues = library.issue_set.all()
		issue_list = []
		for i in range(0, len(issue_date_list)):
			found = False;
			for j in range(0, len(issues)):
				if issues[j].closing_date != None and issue_date_list[i] == issues[j].creation_date:
					found = True
					issue_list.append(int((issues[j].closing_date - issues[j].creation_date).total_seconds())/86400)
			if found == False:
				issue_list.append(None)
		line_chart.add(library.name, issue_list)
	data = line_chart.render_data_uri()
	saveData(data, domain + '_issue_closing_chart.pkl')
	return data


def create_issue_classification_chart(domain):
	line_chart = pygal.StackedBar(height=200)
	selected_domain = Domain.objects.get(name=domain)
	libraries = selected_domain.library_set.all()

	library_names = []
	performance_issues = []
	security_issues = []
	performance_security_issues = []
	no_classification_issues = []
	for library in libraries:
		library_names.append(library.name)
		performance_issues.append(library.issue_set.all().filter(performance_issue=True, security_issue=False).count())
		security_issues.append(library.issue_set.all().filter(security_issue=True, performance_issue=False).count())
		performance_security_issues.append(library.issue_set.all().filter(security_issue=True, performance_issue=True).count())
		no_classification_issues.append(library.issue_set.all().filter(security_issue=False, performance_issue=False).count())
	line_chart.x_labels = library_names
	line_chart.add('Performance', performance_issues)
	line_chart.add('Security', security_issues)
	line_chart.add('Both', performance_security_issues)
	line_chart.add('None', no_classification_issues)
	data = line_chart.render_data_uri()
	saveData(data, domain + '_issue_classification_chart.pkl')
	return data

def fillPopularityData(entrymonth,entryyear):
  with open("popularity_results.txt") as f:
    lines = f.readlines()
  lines = [x.strip() for x in lines]
  for line in lines:
    strings = line.split(':')
    repository = strings[0]
    popularity = strings[1]
    print (repository)
    library = Data.objects.get(repository=repository, month=entrymonth,year=entryyear)
    library.popularity = int(strings[1])
    library.run_time = date.today()    
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

def createCharts(entrymonth,entryyear):
  
  for domain in Domain.objects.all():  
    create_popularity_chart(domain.name,entrymonth,entryyear)
    create_release_chart(domain.name)
    create_breaking_changes_chart(domain.name)
    create_issue_response_chart(domain.name)
    create_issue_closing_chart(domain.name)
    create_issue_classification_chart(domain.name)
    create_last_discussed_chart(domain.name)
    create_last_modification_chart(domain.name)

if __name__ == '__main__':
  d = date.today()
  entrymonth = d.month
  entryyear = d.year
  
  fillPopularityData(entrymonth,entryyear)
  createCharts(entrymonth,entryyear)
  fillReleaseFrequencyData()
  fillBreakingChanges()
  fillLastModificationDateData()
  fillLastDiscussedSOData()
  fillLicenseData()
  fillIssueClosingTimeData()
  fillIssueResponseTimeData()
  fillIssueData()
  fillOverallScore()