FROM python:3.6.9-slim-stretch

WORKDIR /main

COPY . /main

RUN pip install --trusted-host pypi.python.org -r requirements.txt

WORKDIR scripts

CMD ["./update.sh"]