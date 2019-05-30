#!/bin/bash

#Description: This metric counts the number of client projects of the libraries in library.txt by searching for import statements through codes on GitHub
#How to use: ./popularity 
#Input: library.txt (file with library packages)
#Output: resultsDATE1-DATE2.txt (file which will have the results of the popularity for each of the libraries)

python3 GitHub_Library_Search.py
