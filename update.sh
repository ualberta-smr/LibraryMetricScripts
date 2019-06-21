#!/bin/bash

echo -n Username:
read username
echo -n Password:
read -s password

echo "Obtaining Popularity..."
./Popularity/popularity.sh search_results.txt

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
echo "Obtaining Backwards Compatibility..."
cd breakingchanges
rm breakingchanges.csv
./mainScript.sh
cd ..

echo "Updating database..."
cp Popularity/popularity_results.txt .
cp ReleaseFrequency/*.pkl .
cp License/*.pkl .
cp LastModificationDate/*.pkl .
cp LastDiscussedOnStackOverflow/*.pkl .
cp IssueMetrics/*.pkl .
cp IssueMetrics/performanceclassifier.py .
cp IssueMetrics/securityclassifier.py .
cp breakingchanges/*.csv .
python3 filldb.py
rm performanceclassifier.py
rm securityclassifier.py
rm breakingchanges.csv
rm popularity_results.txt
mv *_chart.pkl ../charts
rm -rf breakingchanges/Repositories/*
rm *.pkl
