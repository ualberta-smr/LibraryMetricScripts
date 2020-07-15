#!/bin/bash

# set -e

now="$(date +'%d/%m/%Y')"
echo "Starting to update metrics at $now..."

#backup current database first (note that this relies on your DB username & password being stored in ~/.my.cnf)

echo "Backing up database first ... "

mkdir -p ~/DBBackups

today=$(date +'%m-%d-%Y')
file_name="~/DBBackups/libcomp-bkp-${today}.sql"
mysqldump --no-create-info --complete-insert --skip-triggers libcomp  Domain Library Issue Metric LibraryRelease MetricsEntry Chart ProjectType TeamType PluginUser PluginUser_groups PluginUser_projects PluginUser_teams PluginFeedback WebsiteFeedback > file_name

#invoke script
mkdir -p logs

echo "Invoking scripts..."

python3 -u -m scripts > logs/libcomp-${today}.log

echo "Finished running scripts.. now copying charts to website"

cp scripts/charts/*.pkl /var/www/librarycomparisonswebsite/charts/


echo "Finished whole process at $now..."
