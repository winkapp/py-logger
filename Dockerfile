FROM python:2.7.13-alpine

RUN pip install -U pytest

WORKDIR /usr/app

COPY . /usr/app
