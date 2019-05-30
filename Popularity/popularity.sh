#!/bin/bash

#Description: This metric counts the number of client projects of the libraries in library.txt by searching for import statements through codes on GitHub
#How to use: ./popularity 
#Input: library.txt (file with library packages)
#Output: A test file called Results-start_Date-end_Date.txt (file which will have the results of the popularity for each of the libraries) 
# The name of the results text file is dependant on the date that the script is run 

python3 GitHub_Library_Search.py
