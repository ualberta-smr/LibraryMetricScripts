'''
This file is for the metric breaking changes. 

It reads lib data from the DB and then calls the breaking changes java code
from Laerte Xavier to calculate breaking changes between each pair of releases

The number of breaking changes and non-breaking changes are directly saved in the DB
'''
import json

from librarycomparison.models import Library
from git import Repo
import os
import shutil
import subprocess
import glob

repos_dir = "scripts/BreakingChanges/Repositories"

def clone_release(library, release):

    repo_dir = repos_dir + "/" + library.name + "-" + release.name

    if not os.path.isdir(repo_dir):
        Repo.clone_from(library.github_url, repo_dir, branch=release.name)

    return repo_dir

def count_breaking_changes(library):

    releases = list(library.releases.all().order_by('release_date'))

    for index in range(len(releases)):
        if index == 0:
            continue

        curr_release = releases[index]
        prev_release = releases[index - 1]

        if curr_release.breaking_changes != -1: #i.e., already calculated this release before
            print("Skipping release ", curr_release.name)
            continue

        print("Calculating for ", curr_release.name)

        curr_release_dir = clone_release(library, curr_release)
        prev_release_dir = clone_release(library, prev_release)

        try:
            breaking_chg_output = subprocess.check_output(["java", "-Xmx12g", "-Xms12g", "-jar", "scripts/BreakingChanges/BreakingChangesJava.jar", prev_release_dir, curr_release_dir])
        except subprocess.CalledProcessError as error:
            print (error.output)
            return

        changes = breaking_chg_output.decode().split(",")
        curr_release.breaking_changes = int(changes[0])
        curr_release.non_breaking_changes  = int(changes[1])
        curr_release.save()

        shutil.rmtree(prev_release_dir)

    dir_pattern = repos_dir + "/" + library.name + "-*"
    for dir_name in glob.glob(dir_pattern):
       shutil.rmtree(dir_name)



def get_breaking_changes():

    if not os.path.isdir("scripts/BreakingChanges/"):
        print ("No breaking changes scripts found... skipping backwards compatibility")
        return

    try:
        os.remove("scripts/BreakingChanges/breakingchanges.csv")
    except FileNotFoundError:
        pass

    libraries = Library.objects.all()

    try:
        os.mkdir(repos_dir)
    except FileExistsError:
        pass #ignore if dir exists

    
    count = 0
    for library in libraries:
        lib_name = library.name
        print ("Getting breaking changes for ", lib_name)
        lib_name = library.name
        # repo = github.get_repo(library.github_repo)

        target_loc = repos_dir + "/" + lib_name

        if not os.path.isdir(target_loc):
            Repo.clone_from(library.github_url, target_loc)

        print ("Cloned repo")
        count_breaking_changes(library)


if __name__ == "__main__":
    get_breaking_changes()
