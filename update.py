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

    subprocess.call("rm *.pkl", shell=True)
    print("Obtaining Release Frequency...")
    releasefrequency.getReleaseDates(username, password)
    print("Obtaining License Information...")
    license.getLicenses(username, password)
    print("Obtaining Last Modification Date...")
    lastmodificationdate.getLastModificationDates(username, password)
    print("Obtaining Last Discussed in Stack Overflow...")
    lastdiscussedSO.getLastDiscussedDates()
    print("Obtaining issue information...")
    issues.getIssueDataJIRA()
    issues.getIssueData(username, password)
    issues.calculateAverageResponseTime()
    issues.calculateAverageClosingTime()
    issues.applyClassifiers()
    print("Obtaining Backwards Compatibility information...")
    subprocess.call("breakingchanges/mainScripts.sh", shell=True)
    subprocess.call("python3 filldb.py", shell=True)

if __name__ == "__main__":
    main()
