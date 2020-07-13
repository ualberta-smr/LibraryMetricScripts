#!/bin/bash

now="$(date +'%d/%m/%Y')"
echo "Starting to update metrics at $now..."

#backup current database first (note that this relies on your DB password being stored in ~/.my.cnf)

echo "Backing up database first ... "

today=$(date +'%m-%d-%Y')

mysqldump -u libcomp --no-create-info --complete-insert --skip-triggers libcomp  Domain Library Issue Metric LibraryRelease MetricsEntry Chart ProjectType TeamType PluginUser PluginUser_groups PluginUser_projects PluginUser_teams PluginFeedback WebsiteFeedback > "/home/webfiles/DBBackups/libcomp-bkp-${today}.sql"

#invoke script
mkdir -p logs

nohup python3 -u scripts > logs/libcomp-${today}.log &

echo "Finished running scripts.. now copying charts"

cp scripts/charts/*.pkl /var/www/librarycomparisonswebsite/charts/


echo "Finished whole process at $now..."
