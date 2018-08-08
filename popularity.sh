#!/bin/bash

while IFS= read -r line
do
    cd "PopularityRepositories"
    git clone "$line"

    #junit4
    if grep -r --include '*.java' "org.junit" "$line";then
	
    fi

    if grep -r --include '*.java' "org.testng" "$line"; then
    fi

    if grep -r --include '*.java' "org.slf4j" "$line"; then
    fi
       
done < file


