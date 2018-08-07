import getpass
import subprocess
from github import Github
import releasefrequency
import lastmodificationdate
import lastdiscussedSO
import license
import issues

def main():
    username = input("Enter Github username: ")
    password = getpass.getpass("Enter your password: ")

    subprocess.Popen("rm *.pkl")
    releasefrequency.getReleaseDates(username, password)
    license.getLicenses(username, password)
    lastmodificationdate.getLastModificationDates(username, password)
    lastdiscussedSO.getLastDiscussedDates()
    issues.getIssueDataJIRA()
    issues.getIssueData(username, password)
    issues.calculateAverageResponseTime()
    issues.calculateAverageClosingTime()
    issues.applyClassifiers()
    subprocess.Popen("./compute_breaking_changes.sh")
    subprocess.Popen("python3 filldb.py")

if __name__ == "__main__":
    main()
