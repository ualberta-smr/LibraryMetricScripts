#!/bin/bash

set -e

cd ~/LibraryMetricScripts/ #assumes that's where this repo is

now="$(date +'%d/%m/%Y')"
echo "Starting to update metrics at $now..."

#backup current database first (note that this relies on your DB username & password being stored in ~/.my.cnf)

echo "Backing up database first ... "

mkdir -p ~/DBBackups

today=$(date +'%m-%d-%Y')
file_name="/home/webfiles/DBBackups/libcomp-bkp-${today}.sql"
mysqldump --no-tablespaces --no-create-info --complete-insert --skip-triggers libcomp  Domain Library Issue Metric LibraryRelease MetricsEntry Chart ProjectType TeamType PluginUser PluginUser_groups PluginUser_projects PluginUser_teams PluginFeedback WebsiteFeedback > $file_name

#pull latest repo changes but stash first to maintain config changes
git stash
git pull
git stash pop

#invoke script
mkdir -p logs

echo "Invoking scripts..."

python3 -u -m scripts > logs/libcomp-${today}.log 2>&1

echo "Finished running scripts.. now copying charts to website"

cp scripts/charts/*.pkl /var/www/librarycomparisonswebsite/charts/


echo "Finished whole process at $now..."
