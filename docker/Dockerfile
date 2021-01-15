FROM python:3.8.0-slim

WORKDIR /main

COPY ./LibraryMetricScripts /main/LibraryMetricScripts
COPY ./librarycomparisonswebsite /main/librarycomparisonswebsite

ENV PYTHONPATH="/main/LibraryMetricScripts/scripts:${PYTHONPATH}"

RUN apt-get update; \
    apt-get -y install sudo; \
    sudo apt-get -y install default-libmysqlclient-dev \
    gcc \
    default-mysql-client \
    default-mysql-server; \
    pip install --trusted-host pypi.python.org -r ./LibraryMetricScripts/requirements.txt; \
    pip install --trusted-host pypi.python.org -r ./librarycomparisonswebsite/requirements.txt;

ENTRYPOINT [ "bash", "./LibraryMetricScripts/docker/start.sh" ]
