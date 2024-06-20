FROM python:3.8.0-slim

# Install OpenJDK 11
ENV DEBIAN_FRONTEND=noninteractive
RUN mkdir -p /usr/share/man/man1 /usr/share/man/man2
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-11-jre
# Prints installed java version, just for checking
RUN java --version

WORKDIR /main

COPY . /main

ENV PYTHONPATH="/main/scripts:${PYTHONPATH}"

RUN apt-get update; \
    apt-get -y install sudo; \
    sudo apt-get -y install default-libmysqlclient-dev \
    gcc \
    default-mysql-client \
    default-mysql-server \
    git \
    libpangocairo-1.0-0; \
    pip install --trusted-host pypi.python.org -r requirements.txt;

ENTRYPOINT [ "bash", "./docker/start.sh" ]
