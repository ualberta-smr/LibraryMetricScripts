
from librarycomparison.models import Domain, Library, Issue, LibraryRelease, MetricsEntry, Metric, Chart
from scripts.License.license import loadLicenseData
from scripts.LastModificationDate.lastmodificationdate import loadLastModificationDateData
from scripts.LastDiscussedOnStackOverflow.lastdiscussedSO import loadLastDiscussedSOData
from datetime import datetime, timezone, date
from dateutil.relativedelta import *
import pygal
import pickle
from scripts.CommonUtilities import Common_Utilities
import traceback
import pytz

def saveData(data, filename):
  with open("scripts/" + filename, 'wb') as output:
    pickle.dump(data, output, pickle.DEFAULT_PROTOCOL)

def get_latest_metrics_entry(library):
    try:
        metricsentry = MetricsEntry.objects.filter(library=library).latest('created_on')
        return metricsentry
    except:
        # This occurs because it doesn’t find a metric entry. Popularity is the first metric to be entered
        # If an entry was created today then it is used, otherwise it creates a new one
        print("INFO: no previous metric entry found for library. Popularity will create a new entry")
        return None

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

def create_popularity_chart(domain):
  
  line_chart  = pygal.DateTimeLine(x_label_rotation=45, height=200, width=1000,x_value_formatter=lambda dt: dt.strftime('%b %d, %Y'))
   
  line_chart.title = "Number of top 1000 GitHub projects using this library on given date"
  
  end_date = MetricsEntry.objects.latest('created_on').created_on
  start_date = end_date - relativedelta(years=1)
  
  
  libraries = domain.libraries.all()#('created_on')# data_set.filter(run_time__gte=start_date).filter(run_time__lte=end_date).order_by('year').order_by('month')
 
  domain_dic = {}
  for library in libraries:   
    metrics = library.metrics.filter(created_on__gte=start_date).filter(created_on__lte=end_date).order_by('created_on')

    if metrics == None:
        continue

    for metric in metrics:

      if library.name in domain_dic.keys():
        domain_dic[library.name].append((metric.created_on.date(),metric.popularity))
      else:
        popularity_data_arr = []
        popularity_data_arr.append((metric.created_on.date(),metric.popularity))
        domain_dic[library.name] = popularity_data_arr
  
  #line_chart.x_labels = map(str, create_date_range(start_date,end_date))
  

  for key, value in domain_dic.items(): 
    line_chart.add(key, value)
  
  data = line_chart.render_data_uri()
  saveData(data, domain.name + '_popularity_chart.pkl')
  
  save_chart_in_db(line_chart, domain, metric_name="popularity")

def save_chart_in_db(pygal_chart, domain, metric_name):
    #save chart in DB

    metric = Metric.objects.get(name=metric_name)

    if not metric:
        print("No metric object found for metric: ", metric)
        return

    chart = Chart.objects.filter(domain=domain).filter(metric=metric)

    #create new chart if it doesn't exist. Otherwise, update entry
    if not chart.exists():
        chart = Chart()
        chart.domain = domain
        chart.metric = metric
    else:
        chart = Chart.objects.filter(domain=domain).get(metric=metric)

    chart.chart = Common_Utilities.chart_to_blob(pygal_chart)#domain.name + chart_suffix)
    chart.save()

def create_release_chart(domain):
    domain_name = domain.name
    line_chart = pygal.Line(x_label_rotation=90, height = 200, show_minor_x_labels=False)
    selected_domain = Domain.objects.get(name=domain_name)
    libraries = selected_domain.libraries.all()
    releases_dict = {}
    release_date_set = set()
    for library in libraries:
        for release in library.releases.all():
            release_date_set.add(release.release_date.date())

    release_date_list = sorted(list(release_date_set))
    line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), release_date_list)

    #create x-axis labels at each year in interval
    x_label_list = []
    min_date =  release_date_list[0]
    max_date = release_date_list[-1]

    x_label_list.append(min_date.strftime('%b %d %Y'))
    curr_date = min_date + relativedelta(years=1)
    while curr_date <= max_date:
        #if datetime(curr_date.year, 1, 1) < curr_date: #in case first date is already beyond january, don't append same year again
        x_label_list.append(datetime(curr_date.year, 1, 1).strftime('%b %d %Y'))
        curr_date = curr_date + relativedelta(years=1)

    x_label_list.append(max_date.strftime('%b %d %Y'))

    line_chart.x_labels_major = x_label_list #[release_date_list[0].strftime('%b %d %Y'), release_date_list[-1].strftime('%b %d %Y')]
    line_chart.title = 'Timeline of Releases'

    library_id = 1
    y_labels = []

    for library in libraries:
        releases = library.releases.all()
        release_list = []
        for i in range(0, len(release_date_list)):
            found = False;
            for j in range(0, len(releases)):
                if release_date_list[i] == releases[j].release_date.date():
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
    saveData(data, domain_name + '_release_chart.pkl')
    save_chart_in_db(line_chart, domain, metric_name="release frequency")

def parseDateString(date_string, is_jira_dates=False):
    strings = date_string.split(';')
    dates = []
    for date in strings:
        if is_jira_dates: #uses offset
            dates.append(datetime.strptime(date, "%m/%d/%Y, %H:%M:%S %z").date())
        else:
            dates.append(datetime.strptime(date, "%m/%d/%Y, %H:%M:%S %Z").date())
    return dates

def create_last_discussed_chart(domain):
    domain_name = domain.name
    line_chart = pygal.Line(x_label_rotation=90, height = 200, show_minor_x_labels=False, dots_size=5)
    selected_domain = Domain.objects.get(name=domain_name)
    libraries = selected_domain.libraries.all()
    date_set = set()
    for library in libraries:
        metricsentry = get_latest_metrics_entry(library)
        if metricsentry == None:
            continue

        if metricsentry.last_discussed_so_dates == None or metricsentry.last_discussed_so_dates == '':
            continue
        dates = parseDateString(metricsentry.last_discussed_so_dates)
        date_set.update(dates)

    date_list = sorted(list(date_set))

    if len(date_list) == 0:
        print("not creating last discussed chart for", domain.name)
        return
    line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), date_list)
    line_chart.x_labels_major = [date_list[0].strftime('%b %d %Y'), date_list[-1].strftime('%b %d %Y')]
    line_chart.title = 'The last 10 questions were asked in these dates:'

    library_id = 1
    y_labels = []

    for library in libraries:
        metricsentry = get_latest_metrics_entry(library)
        if metricsentry == None:
            continue

        if metricsentry.last_discussed_so_dates == None or metricsentry.last_discussed_so_dates == '':
            continue
        dates = parseDateString(metricsentry.last_discussed_so_dates)
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
    saveData(data, domain_name + '_last_discussed_chart.pkl')
    save_chart_in_db(line_chart, domain, metric_name="last discussed on so")

def create_last_modification_chart(domain):
    domain_name = domain.name
    line_chart = pygal.Line(x_label_rotation=90, height = 200, show_minor_x_labels=False, dots_size=5)
    selected_domain = Domain.objects.get(name=domain_name)
    libraries = selected_domain.libraries.all()
    date_set = set()
    for library in libraries:
        metricsentry = get_latest_metrics_entry(library)
        if metricsentry == None:
            continue

        dates = parseDateString(metricsentry.last_modification_dates)
        date_set.update(dates)

    date_list = sorted(list(date_set))
    if len(date_list) == 0:
        print("not creating last modification chart for", domain.name)
        return

    line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), date_list)
    line_chart.x_labels_major = [date_list[0].strftime('%b %d %Y'), date_list[len(date_list)//2].strftime('%b %d %Y'), date_list[-1].strftime('%b %d %Y')]
    line_chart.title = 'The last 10 modifications were done in these dates:'

    library_id = 1
    y_labels = []

    for library in libraries:
        metricsentry = get_latest_metrics_entry(library)
        if metricsentry == None:
            continue

        dates = parseDateString(metricsentry.last_modification_dates)
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
    saveData(data, domain_name + '_last_modification_chart.pkl')
    save_chart_in_db(line_chart, domain, metric_name="last modification date")

def create_breaking_changes_chart(domain):
    domain_name = domain.name
    line_chart = pygal.Line(x_label_rotation=90, show_minor_x_labels=False)
    selected_domain = Domain.objects.get(name=domain_name)
    libraries = selected_domain.libraries.all()
    releases_dict = {}
    release_date_set = set()
    for library in libraries:
        for release in library.releases.all():
            release_date_set.add(release.release_date.date())

    release_date_list = sorted(list(release_date_set))
    line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), release_date_list)
    line_chart.x_labels_major = [release_date_list[0].strftime('%b %d %Y'), release_date_list[len(release_date_list)//2].strftime('%b %d %Y'),
      release_date_list[-1].strftime('%b %d %Y')]
    line_chart.title = 'Breaking Changes in Releases.'
    line_chart.x_title= ' Release Dates'
    line_chart.y_title = 'Number of Breaking changes'

    for library in libraries:
        releases = library.releases.all()
        release_list = []
        for i in range(0, len(release_date_list)):
            found = False;
            for j in range(0, len(releases)):
                if release_date_list[i] == releases[j].release_date.date():
                    found = True
                    release_list.append(releases[j].breaking_changes)
                    #break
            if found == False:
                release_list.append(None)
        line_chart.add(library.name, release_list)
    data = line_chart.render_data_uri()
    saveData(data, domain_name + '_breaking_changes_chart.pkl')
    save_chart_in_db(line_chart, domain, metric_name="breaking changes")

def create_issue_response_chart(domain):
    domain_name = domain.name
    line_chart = pygal.Line(x_label_rotation=90, show_minor_x_labels=False, height=300)
    selected_domain = Domain.objects.get(name=domain_name)
    libraries = selected_domain.libraries.all()
    issue_date_set = set()


    end_date = pytz.utc.localize(datetime.today())
    start_date = end_date - relativedelta(years=1)

    for library in libraries:
        for issue in library.issues.filter(creation_date__gte=start_date).filter(creation_date__lte=end_date).order_by('creation_date'):
            if issue.first_response_date:
                issue_date_set.add(issue.first_response_date.date())

    if len(issue_date_set) != 0:
        issue_date_list = sorted(list(issue_date_set))
        line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), issue_date_list)
        line_chart.x_labels_major = [issue_date_list[0].strftime('%b %d %Y'), issue_date_list[-1].strftime('%b %d %Y')]
        line_chart.title = 'Response Times for Issues Created in the Last Year'
        line_chart.x_title= 'Issue creation date'
        line_chart.y_title = 'Number of days to respond'

        for library in libraries:
            issues = library.issues.filter(creation_date__gte=start_date).filter(creation_date__lte=end_date).order_by('creation_date')
            issue_list = []
            for i in range(0, len(issue_date_list)):
                found = False;
                for j in range(0, len(issues)):
                    if issues[j].first_response_date != None and issue_date_list[i] == issues[j].first_response_date.date():
                        found = True
                        issue_list.append(int((issues[j].first_response_date - issues[j].creation_date).total_seconds())/86400)
                if found == False:
                    issue_list.append(None)
            line_chart.add(library.name, issue_list)
        data = line_chart.render_data_uri()
        saveData(data, domain_name + '_issue_response_chart.pkl')
        save_chart_in_db(line_chart, domain, metric_name="issue response")


def create_issue_closing_chart(domain):
    domain_name = domain.name
    line_chart = pygal.Line(x_label_rotation=90, show_minor_x_labels=False, height=300)
    selected_domain = Domain.objects.get(name=domain_name)
    libraries = selected_domain.libraries.all()
    issue_date_set = set()

    end_date = pytz.utc.localize(datetime.today())
    start_date = end_date - relativedelta(years=1)

    for library in libraries:
        for issue in library.issues.filter(creation_date__gte=start_date).filter(creation_date__lte=end_date).order_by('creation_date'):
            if issue.closing_date:
                issue_date_set.add(issue.closing_date.date())

    if len(issue_date_set) != 0:
        issue_date_list = sorted(list(issue_date_set))
        line_chart.x_labels = map(lambda d: d.strftime('%b %d %Y'), issue_date_list)
        line_chart.x_labels_major = [issue_date_list[0].strftime('%b %d %Y'),
          issue_date_list[-1].strftime('%b %d %Y')]
        line_chart.title = 'Closing Times for Issues Created in the Last Year'
        line_chart.x_title= 'Issue creation date'
        line_chart.y_title = 'Number of days to close'

        for library in libraries:
            issues = library.issues.filter(creation_date__gte=start_date).filter(creation_date__lte=end_date).order_by('creation_date')
            issue_list = []
            for i in range(0, len(issue_date_list)):
                found = False;
                for j in range(0, len(issues)):
                    if issues[j].closing_date != None and issue_date_list[i] == issues[j].creation_date.date():
                        found = True
                        issue_list.append(int((issues[j].closing_date - issues[j].creation_date).total_seconds())/86400)
                if found == False:
                    issue_list.append(None)
            line_chart.add(library.name, issue_list)
        data = line_chart.render_data_uri()
        saveData(data, domain_name + '_issue_closing_chart.pkl')
        save_chart_in_db(line_chart, domain, metric_name="issue closing")


def create_issue_classification_chart(domain):
    domain_name = domain.name
    line_chart = pygal.StackedBar(height=200)
    line_chart.title = "Number of issues of each type per library"
    selected_domain = Domain.objects.get(name=domain_name)
    libraries = selected_domain.libraries.all()

    library_names = []
    performance_issues = []
    security_issues = []
    performance_security_issues = []
    no_classification_issues = []
    for library in libraries:
        library_names.append(library.name)
        performance_issues.append(library.issues.filter(performance_issue=True, security_issue=False).count())
        security_issues.append(library.issues.filter(security_issue=True, performance_issue=False).count())
        performance_security_issues.append(library.issues.filter(security_issue=True, performance_issue=True).count())
        no_classification_issues.append(library.issues.filter(security_issue=False, performance_issue=False).count())
    line_chart.x_labels = library_names
    line_chart.add('Performance', performance_issues)
    line_chart.add('Security', security_issues)
    line_chart.add('Both', performance_security_issues)
    line_chart.add('None', no_classification_issues)
    data = line_chart.render_data_uri()
    saveData(data, domain_name + '_issue_classification_chart.pkl')
    save_chart_in_db(line_chart,domain, metric_name="issue classification")

def fillPopularityData():
  with open("scripts/popularity_results.txt") as f:
    lines = f.readlines()
  lines = [x.strip() for x in lines]
  for line in lines:
    strings = line.split(':')
    repository = strings[0]
    popularity = strings[1]
    library = Library.objects.get(github_repo=repository)
    metricsentry = get_latest_metrics_entry(library)

    #Only create a new entry if we have not already created an entry today
    #can happen if we need to re-run due to previous errors
    if metricsentry == None or metricsentry.created_on.date() != datetime.today().date():
        metricsentry = MetricsEntry()
        metricsentry.library = library
        metricsentry.popularity = int(popularity)
        metricsentry.save()
    else:
        print("DID NOT CREATE new entry for:", library.name)

def calculateReleaseFrequency():
    for library in Library.objects.all():
        print("calculating release frequency for library.. ", library.name)
        metricsentry = get_latest_metrics_entry(library)
        if metricsentry == None:
            print("ERROR: in release frequency, could not find a metrics entry for library", library.name)
            continue

        metricsentry.breaking_changes = 0
        libreleases = library.releases.order_by('release_date')
        number_of_differences = len(libreleases)-1
        total_seconds = 0
        for i in range(1, len(libreleases)):
            total_seconds += int((libreleases[i].release_date - libreleases[i-1].release_date).total_seconds())
        #divide the average by the number of seconds per day
        if number_of_differences <= 0:
            metricsentry.release_frequency = -1 #if there was no release data, record -1
        else:
            metricsentry.release_frequency = float(total_seconds/number_of_differences/86400)
        metricsentry.save()


def fillLastModificationDateData():
    data = loadLastModificationDateData()
    for repo, dates in data.items():
        try:
            library = Library.objects.get(github_repo=repo)
        except:
            print("ERROR: Could not find library listed in last modification data.. skipping", repo)
            continue
        metricsentry = get_latest_metrics_entry(library)
        if metricsentry == None:
            continue
        metricsentry.last_modification_dates = dates
        try:
            metricsentry.last_modification_date = pytz.utc.localize(datetime.strptime(dates.split(';')[0], "%m/%d/%Y, %H:%M:%S %Z"))
        except:
            print("Failed to parse last modification date date: ", dates.split(';')[0])
        metricsentry.save()

def fillIssueData():
    
    libraries = Library.objects.all()

    for library in libraries:

        total_issues = 0
        total_performance_issues = 0
        total_security_issues = 0
        total_closing_time = 0
        total_closed_issues = 0
        total_response_time = 0
        total_issues_with_comments = 0
        metricsentry = get_latest_metrics_entry(library)

        if metricsentry == None:
            print("ERROR: in issue data, could not find a metrics entry for library", library.name)
            continue

        lib_issues = library.issues.all()

        #if we don't have issue data for whatever reason, record as -1
        if lib_issues.count() == 0:
            metricsentry.issue_closing_time = -1
            metricsentry.issue_response_time = -1
            metricsentry.performance = -1
            metricsentry.security = -1
            metricsentry.save()
            continue

        for issue in lib_issues:
            if issue.performance_issue == True:
                total_performance_issues += 1
            if issue.security_issue == True:
                total_security_issues += 1
            if issue.closing_date is not None:
                closing_time = int((issue.closing_date - issue.creation_date).total_seconds())
                total_closing_time += closing_time
                total_closed_issues += 1
            
            if issue.first_response_date is not None:
                response_time = int((issue.first_response_date - issue.creation_date).total_seconds())
                total_response_time += response_time
                total_issues_with_comments += 1

            total_issues += 1

        try:
            if total_closed_issues > 0:
                metricsentry.issue_closing_time = float(total_closing_time/total_closed_issues/86400)
            if total_issues_with_comments > 0:
                metricsentry.issue_response_time = float(total_response_time/total_issues_with_comments/86400)
            metricsentry.performance = total_performance_issues/total_issues*100
            metricsentry.security = total_security_issues/total_issues*100
            metricsentry.save()
        except Exception as e:
            print("Could not calculate issue values for ", library.name)
            traceback.print_exc()

def fillLastDiscussedSOData():
    data = loadLastDiscussedSOData()
    for tag, dates in data.items():
        print("getting last discussed date for", tag)
        try:
            library = Library.objects.get(so_tag=tag)
        except:
            print("ERROR: Could not find library listed in SO data.. skipping", tag)
            continue
        
        metricsentry = get_latest_metrics_entry(library)
        if metricsentry == None:
            continue
        if dates:
            metricsentry.last_discussed_so = pytz.utc.localize(datetime.strptime(dates.split(';')[0], "%m/%d/%Y, %H:%M:%S %Z"))
            metricsentry.last_discussed_so_dates = dates
        else:
            metricsentry.last_discussed_so_dates = ''
        metricsentry.save()

def fillLicenseData():
    data = loadLicenseData()
    for repo, license in data.items():
        try:
            library = Library.objects.get(github_repo=repo)
        except:
            print("Could not get library in license data",  repo)
            continue
        metricsentry = get_latest_metrics_entry(library)
        if metricsentry == None:
            continue
        metricsentry.license = license
        metricsentry.save()


def fillBreakingChanges():

    for library in Library.objects.all():
        metricsentry = get_latest_metrics_entry(library)
        if metricsentry == None:
           continue

        total_breaking_changes = 0
        total_non_breaking_changes = 0
        release_count = library.releases.all().count()

        for release in library.releases.all():
            total_breaking_changes += release.breaking_changes
            total_non_breaking_changes += release.non_breaking_changes

        metricsentry.breaking_changes = total_breaking_changes
        metricsentry.non_breaking_changes = total_non_breaking_changes

        if release_count == 0:
            metricsentry.backwards_compatibility = -1
        else:
            metricsentry.backwards_compatibility = metricsentry.breaking_changes/release_count
        metricsentry.save()

def fillOverallScore():


    for domain in Domain.objects.all():
        highestPopularity = 0
        number_of_metrics = 8
        max_score_value = 5
        domain_libs = domain.libraries.all()

        for library in domain_libs:
            metricsentry = get_latest_metrics_entry(library)
            if metricsentry == None:
                continue
            highestPopularity = max(highestPopularity, metricsentry.popularity)

        for library in domain_libs:
            metricsentry = get_latest_metrics_entry(library)
            if metricsentry == None:
                continue
            score = 0.0
            score += metricsentry.popularity/max(1, highestPopularity)
            score += max(0, 1-metricsentry.release_frequency/365)
            score += max(0, 1-metricsentry.issue_closing_time/365)
            score += max(0, 1-metricsentry.issue_response_time/365)
            score += max(0, 1- (int((datetime.now(timezone.utc) - metricsentry.last_modification_date).total_seconds())/86400/365))
            score += metricsentry.non_breaking_changes/max(1,(metricsentry.breaking_changes+metricsentry.non_breaking_changes))
            score += (100-metricsentry.performance)/100
            score += (100-metricsentry.security)/100
            metricsentry.overall_score = score*max_score_value/number_of_metrics
            metricsentry.save()

def createCharts():
  
  for domain in Domain.objects.all():  
    create_popularity_chart(domain)
    create_release_chart(domain)
    create_breaking_changes_chart(domain)
    create_issue_response_chart(domain)
    create_issue_closing_chart(domain)
    create_issue_classification_chart(domain)
    create_last_discussed_chart(domain)
    create_last_modification_chart(domain)

def filldb():
    print("Filling popularity...")
    fillPopularityData()
    print("Calculating release frequency...")
    calculateReleaseFrequency()
    print("Calculating breaking changes...")
    fillBreakingChanges()
    print("Filling last modification data...")
    fillLastModificationDateData()
    print("Filling last discussed on SO....")
    fillLastDiscussedSOData()
    print("Filling license data...")
    fillLicenseData()
    print("Calculating issue data...")
    fillIssueData()
    print("Calculating overall score...")
    fillOverallScore()
    print("Creating charts...")
    createCharts()

if __name__ == '__main__':
    filldb()
  
