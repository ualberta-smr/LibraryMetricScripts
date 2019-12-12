#!/bin/bash

pythoncmd=python3.8

echo "Making sure all libraries are in the database..."
$pythoncmd addlibraries.py

echo "Obtaining Popularity..."
#cd Popularity
#rm -f Popularity/*.txt
#$pythoncmd Popularity/GitHub_Phase1.py
$pythoncmd Popularity/GitHub_Phase2.py
#cd ..

echo "Obtaining Release Frequency..."
#cd ReleaseFrequency
rm -f ReleaseFrequency/*.pkl
$pythoncmd ReleaseFrequency/releasefrequency.py
#cd ..

echo "Obtaining License Information..."
#cd License
rm -f License/*.pkl
$pythoncmd License/license.py
#cd ..

echo "Obtaining Last Modification Date..."
#cd LastModificationDate
rm -f LastModificationDate/*.pkl
$pythoncmd LastModificationDate/lastmodificationdate.py
#cd ..

echo "Obtaining Last Discussed on Stack Overflow..."
#cd LastDiscussedOnStackOverflow
rm -f LastDiscussedOnStackOverflow/*.pkl
$pythoncmd LastDiscussedOnStackOverflow/lastdiscussedSO.py
#cd ..

echo "Obtaining issue metrics..."
#cd IssueMetrics
rm -f IssueMetrics/*.pkl
$pythoncmd IssueMetrics/issues.py
#cd ..

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
rm performanceclassifier.py
rm securityclassifier.py
rm popularity_results.txt

DIR="../../../charts/"
if [ -d "$DIR" ]; then
    echo "Moving .pkl charts"
    mv *_chart.pkl ../../../charts/
else
    echo "${DIR} NOT found, .pkl files will not be moved"
    rm -f *_chart.pkl
fi

DIR="../../breakingchanges/"
if [ -d "$DIR" ]; then
    echo "removing breaking changes files"
    rm breakingchanges.csv
    rm -rf ../../breakingchanges/Repositories/*
else
    echo "No breaking changes files to remove"
fi

rm *.pkl
