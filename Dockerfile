FROM ubuntu:latest
LABEL authors="kira"

ENTRYPOINT ["top", "-b"]

FROM python:3.11
WORKDIR /app
RUN chmod 755 .

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
COPY . .