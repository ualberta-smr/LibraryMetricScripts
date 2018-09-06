import getpass
import subprocess
import sys
from github import Github
sys.path.insert(0,'ReleaseFrequency/')
import releasefrequency
sys.path.insert(0,'LastModificationDate/')
import lastmodificationdate
sys.path.insert(0,'LastDiscussedOnStackOverflow/')
import lastdiscussedSO
sys.path.insert(0,'License/')
import license
sys.path.insert(0, 'IssueMetrics/')
import issues

def main():
    username = input("Enter Github username: ")
    password = getpass.getpass("Enter your password: ")

    print("Obtaining Popularity...")
    #subprocess.call("./popularity.sh search_results.txt", shell=True)

    print("Obtaining Release Frequency...")
    subprocess.call("rm ReleaseFrequency/*.pkl", shell=True)
    releasefrequency.getReleaseDates(username, password)

    print("Obtaining License Information...")
    subprocess.call("rm License/*.pkl", shell=True)
    license.getLicenses(username, password)

    print("Obtaining Last Modification Date...")
    subprocess.call("rm LastModificationDate/*.pkl", shell=True)
    lastmodificationdate.getLastModificationDates(username, password)

    print("Obtaining Last Discussed in Stack Overflow...")
    subprocess.call("rm LastDiscussedOnStackOverflow/*.pkl", shell=True)
    lastdiscussedSO.getLastDiscussedDates()

    print("Obtaining issue information...")
    subprocess.call("rm IssueMetrics/*.pkl", shell=True)
    issues.getIssueDataJIRA()
    issues.getIssueData(username, password)
    issues.calculateAverageResponseTime()
    issues.calculateAverageClosingTime()
    issues.applyClassifiers()

    print("Obtaining Backwards Compatibility information...")
    subprocess.call("rm breakingchanges/breakingchanges.csv", shell=True)
    subprocess.call(".breakingchanges/mainScript.sh", shell=True)

    print("Updating database...")
    subprocess.call("python3 filldb.py", shell=True)

if __name__ == "__main__":
    main()
