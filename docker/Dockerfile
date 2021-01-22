FROM python:3.8.0-slim

WORKDIR /main

COPY . /main

ENV PYTHONPATH="/main/scripts:${PYTHONPATH}"

RUN apt-get update; \
    apt-get -y install sudo; \
    sudo apt-get -y install default-libmysqlclient-dev \
    gcc \
    default-mysql-client \
    default-mysql-server; \
    pip install --trusted-host pypi.python.org -r requirements.txt;

ENTRYPOINT [ "bash", "./docker/start.sh" ]
