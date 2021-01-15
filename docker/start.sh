#!/bin/bash

echo "alias start='python ./librarycomparisonswebsite/manage.py runserver 0.0.0.0:8000'" >> ~/.bashrc
echo "alias migrate='python ./librarycomparisonswebsite/manage.py migrate'" >> ~/.bashrc
echo "alias make='python ./librarycomparisonswebsite/manage.py makemigrations'" >> ~/.bashrc
echo "alias createsuperuser='python ./librarycomparisonswebsite/manage.py createsuperuser'" >> ~/.bashrc
echo "alias updatemetrics='./LibraryMetricScripts/updatemetrics.sh'" >> ~/.bashrc

/bin/bash
