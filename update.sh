#!/bin/bash

echo -n Username:
read username
echo -n Password:
read -s password

echo "Obtaining Popularity..."
#./Popularity/popularity.sh search_results.txt

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

echo "Obtaining Backwards Compatibility..."
cd breakingchanges
rm breakingchanges.csv
./mainScript.sh
cd ..

echo "Updating database..."
cp ReleaseFrequency/*.pkl .
cp License/*.pkl .
cp LastModificationDate/*.pkl
cp LastDiscussedOnStackOverflow/*.pkl
cp IssueMetrics/*.pkl .
cp breakingchanges/*.csv .
python3 filldb.py
