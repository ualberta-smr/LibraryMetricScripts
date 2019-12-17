FROM python:3.8.0-slim

WORKDIR /main

COPY . /main

ENV PYTHONPATH="/main/scripts:${PYTHONPATH}"

RUN pip install --trusted-host pypi.python.org -r requirements.txt

WORKDIR ./scripts

CMD ./update.sh python
