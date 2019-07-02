[![DOI](https://zenodo.org/badge/104284830.svg)](https://zenodo.org/badge/latestdoi/104284830)

# Library Metric Scripts

This repository contains the scripts used to extract various metrics to compare software libraries. 
These metrics are discussed in detail in our PROMISE '18 paper **An Empirical Study of Metric-based Comparisons of Software Libraries**, which can be found [here](https://dl.dropboxusercontent.com/s/v5hdbnywsycvt1q/LopezDeLaMoraPROMISE18.pdf). If you are looking for the exact scripts we used in the PROMISE '18 paper, along with the relevant README file, please take a look at the [promise18](https://github.com/ualberta-smr/LibraryMetricScripts/tree/promise18) tag, which also contains the data collected from the survey in a git submodule.

We have done a lot of refactoring and changes of the code since then, mainly to incorporate some of the feedback we got from the survey in our [library comparison](TODO) website.
This feedback includes graphs for some of the metrics, as well as new metrics.
For example, instead of having one folder for each of the 9 metrics, we combine the code for some of the metrics into the same folder and scripts to avoid computation redundany. 
The documentation below refers to the current version of the code.

# How to Run

The current output files for each metric, based on when they last ran, are included inside each directory.
Most of the output files are Python pickle files, while a few are text files.
Each script describes its input and output.
If you would like to get updated metric data, for the same list of libraries we have (found in `SharedFiles/LibraryData.json`, please follow the following steps:

- Go to `Popularity` and open `GitHubSearch.json`. For the parameter called `TOKEN`, add your own GitHub generated token.
- Go to `LastDiscussedOnStackOverflow` and open `lastdiscussedSO.py`. For the variable called `user_api_key`, you need to add your stack exchange key. 
- Run `update.sh` which will call all the metric scripts. Each metric produces its own output files which you can just look at. However, in addition, the `update.sh` scripts updates an sqlite database with all the results from all scripts. See notes below about the database schema. Note that you will be asked for your Github credentials in the process. 

# How to Add New Libraries

To add a new library, you need to go to `SharedData/LibraryData.json` and add one json entry (per library added) with the following information: 

* `LibraryName`: The library name is the word that comes after the slash (/) in a libraries' GitHub repository (i.e., not including the username). For example, the name of this repository is `LibraryMetricScripts`.

* `Domain`: The domain of the library you wish to enter. (i.e. databases, logging, testing etc.) If you're adding a library whose domain already exists in the file, make sure to use the same domain name so that both libraries appear in the same comparison table. 

* `FullRepoName`: The full repository name of the library. For example, the full name of this repository is `ualberta-smr/LibraryMetricScripts`.

* `SOtags`: This is the Stack Overflow tag of the library. To find the Stack Overflow tag, you will have to manually search it in Stack Overflow (e.g. search for tags with the library name).

* `Package`: This is the general Java package name of the library (e.g. org.testng). 

* `GitHubURL`: This is the github URL of the repository. Add it in the following format: `git://github.com/[full repository name].git`. For example, the line for testng would be: `git://github.com/cbeust/testng.git`

* `JIRAURL`: If the library that you're adding has its issue tracking system in Github, then leave this as an empty strong (i.e., ""), otherwise, if the issues are hosted on JIRA, then go to the JIRA website of the library. Go to 'View all issues and filters'. Make sure you only have the 'Bug' type selected in Issue type, and make sure to include issues for all status. Click 'Export XML'. This will take you to a website where an XML will be loaded. Copy the URL of that website and paste it here for the parameter `JIRAURL`.

# How to Add New Metrics
- Go to `librarycomparison/models.py`, and add new fields to classes `Domain` (feedback for the metric) and `Library`.
- Go to librarycomparison/scripts. After creating the scripts to collect your new metric, make sure to modify `filldb.py` to populate the fields you created in `models.py`.
- In the same folder, modify `update.sh` to add the code that will run your scripts to collect the data.
- Finally, go to librarycomparisonwebsite/templates, and modify `domains.html` to display your new metric in the table.

# Data Schema
- The data schema can be found in `librarycomparison/models.py`. The schema is simple:
- `Domain` stores information about a domain (e.g. name), as well as the metric feedback specific to that domain (latter part is not relevant for this repo per se, but relevant for us in our deployed website to know which metrics to display for which domain)
- `Library` stores the name, tag, and full repository of a library, as well as all the metric data related to that library. A library must also have a `Domain` object, which has the information about the library domain.
- `Issue` and `Release` store information about issues and releases of libraries, and are used for specific metrics.
- `Feedback` just stores text containing submitted user feedback through the website (not relevant if you just want to run the scripts)

# Contributors
- Fernando López de la Mora (lopezdel at ualberta dot ca)
- Sarah Nadi (nadi at ualberta dot ca)
- Rehab El-Hajj (relhajj at ualberta.ca)
