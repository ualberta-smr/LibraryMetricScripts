#!/bin/bash

echo -n Username:
read username
echo -n Password:
read -s password

echo "Making sure all libraries are in the database..."
python3 addlibraries.py

echo "Obtaining Popularity..."
cd Popularity
rm *.txt
python3 GitHub_Phase1.py
python3 GitHub_Phase2.py
cd ..

echo "Obtaining Release Frequency..."
cd ReleaseFrequency
rm *.pkl
python3 releasefrequency.py $username $password
cd ..

echo "Obtaining License Information..."
cd License
rm *.pkl
python3 license.py $username $password
cd ..

echo "Obtaining Last Modification Date..."
cd LastModificationDate
rm *.pkl
python3 lastmodificationdate.py $username $password
cd ..

echo "Obtaining Last Discussed on Stack Overflow..."
cd LastDiscussedOnStackOverflow
rm *.pkl
python3 lastdiscussedSO.py
cd ..

echo "Obtaining issue metrics..."
cd IssueMetrics
rm *.pkl
python3 issues.py $username $password
cd ..

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
    cp ../../breakingchanges/*.csv .
    cd ../LibraryMetricScripts/scripts 
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
python3 filldb.py
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
