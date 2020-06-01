#!/bin/bash

#pass in the python command you want to use (depending on the version)
pythoncmd=$1 #python3.8

echo "Making sure all libraries are in the database..."
$pythoncmd addlibraries.py

echo "Obtaining Popularity..."
rm -f Popularity/*.txt
$pythoncmd Popularity/GitHub_Phase1.py
$pythoncmd Popularity/GitHub_Phase2.py

echo "Obtaining Release Frequency..."
rm -f ReleaseFrequency/*.pkl
$pythoncmd ReleaseFrequency/releasefrequency.py

echo "Obtaining License Information..."
rm -f License/*.pkl
$pythoncmd License/license.py

echo "Obtaining Last Modification Date..."
rm -f LastModificationDate/*.pkl
$pythoncmd LastModificationDate/lastmodificationdate.py

echo "Obtaining Last Discussed on Stack Overflow..."
rm -f LastDiscussedOnStackOverflow/*.pkl
$pythoncmd LastDiscussedOnStackOverflow/lastdiscussedSO.py

echo "Obtaining issue metrics..."
rm -f IssueMetrics/*.pkl
$pythoncmd IssueMetrics/issues.py

#Not included in this library due to licensing issues
#This code was kindly shared with us by Laerte Xavier, but we
#do not have explicit permission to share it.
#Please contact laertexavier@dcc.ufmg.br for more information.

DIR="../../breakingchanges/"
if [ -d "$DIR" ]; then
    echo "Obtaining Backwards Compatibility..."
    cd ../../breakingchanges/
    rm breakingchanges.csv
    ./mainScript.sh
    cd ../LibraryMetricScripts/scripts
    cp ../../breakingchanges/*.csv .
else
    echo "${DIR} NOT found, will not compute backwards compatibility"
fi

echo "Updating database..."
cp Popularity/popularity_results.txt .
cp ReleaseFrequency/*.pkl .
cp License/*.pkl .
cp LastModificationDate/*.pkl .
cp LastDiscussedOnStackOverflow/*.pkl .
cp IssueMetrics/*.pkl .
cp IssueMetrics/performanceclassifier.py .
cp IssueMetrics/securityclassifier.py .
$pythoncmd filldb.py
rm -f performanceclassifier.py
rm -f securityclassifier.py
rm -f popularity_results.txt

DIR="../../../charts/"
if [ -d "$DIR" ]; then
    echo "Moving .pkl charts"
    mv *_chart.pkl ../../../charts/
else
    echo "${DIR} NOT found, creating local charts folder"
    mkdir charts
    mv *_chart.pkl charts/
fi
#
#DIR="../../breakingchanges/"
#if [ -d "$DIR" ]; then
#    echo "removing breaking changes files"
#    rm breakingchanges.csv
#    rm -rf ../../breakingchanges/Repositories/*
#else
#    echo "No breaking changes files to remove"
#fi
#
rm *.pkl
