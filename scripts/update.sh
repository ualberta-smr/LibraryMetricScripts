#!/bin/bash

#pass in the python command you want to use (depending on the version)
pythoncmd=$1 #python3.8

echo "Making sure all libraries are in the database..."
$pythoncmd addlibraries.py
#
#if [ $? -eq 0 ]; then
#    echo "Added libraries..."
#else
#    exit 1
#fi
#
#echo "Obtaining Popularity..."
#rm -f Popularity/*.txt
#$pythoncmd Popularity/GitHub_Phase1.py
#
#if [ $? -eq 0 ]; then
#    echo "Found top repos..."
#else
#    exit 1
#fi
#
#$pythoncmd Popularity/GitHub_Phase2.py
#
#if [ $? -eq 0 ]; then
#    echo "Got popularity... "
#else
#    exit 1
#fi

echo "Obtaining Release Frequency..."
$pythoncmd ReleaseFrequency/releasefrequency.py

if [ $? -eq 0 ]; then
    echo "Got release frequency..."
else
    exit 1
fi

echo "Obtaining License Information..."
rm -f License/*.pkl
$pythoncmd License/license.py

if [ $? -eq 0 ]; then
    echo "Got license info..."
else
    exit 1
fi

echo "Obtaining Last Modification Date..."
rm -f LastModificationDate/*.pkl
$pythoncmd LastModificationDate/lastmodificationdate.py

if [ $? -eq 0 ]; then
    echo "Got last modification date..."
else
    exit 1
fi

echo "Obtaining Last Discussed on Stack Overflow..."
rm -f LastDiscussedOnStackOverflow/*.pkl
$pythoncmd LastDiscussedOnStackOverflow/lastdiscussedSO.py

if [ $? -eq 0 ]; then
    echo "Got last discussed on SO..."
else
    exit 1
fi

echo "Obtaining issue metrics..."
$pythoncmd IssueMetrics/issues.py

if [ $? -eq 0 ]; then
    echo "Got issues..."
else
    exit 1
fi

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
cp License/*.pkl .
cp LastModificationDate/*.pkl .
cp LastDiscussedOnStackOverflow/*.pkl .
$pythoncmd filldb.py

if [ $? -eq 0 ]; then
    echo "Filled db with info..."
else
    exit 1
fi

DIR="../../../charts/"
if [ -d "$DIR" ]; then
    echo "Moving .pkl charts"
    mv *_chart.pkl ../../../charts/
else
    echo "${DIR} NOT found, creating local charts folder"
    mkdir -p charts
    mv *_chart.pkl charts/
fi

DIR="../../breakingchanges/"
if [ -d "$DIR" ]; then
    echo "removing breaking changes files"
    rm breakingchanges.csv
    rm -rf ../../breakingchanges/Repositories/*
else
    echo "No breaking changes files to remove"
fi

rm -f popularity_results.txt
rm *.pkl
