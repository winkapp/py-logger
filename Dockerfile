FROM python:2.7.13-alpine
LABEL maintainer "Jonathan Hosmer <jonathan@wink.com>"

WORKDIR /usr/app

COPY requirements-test.txt /usr/app

RUN pip install -r requirements-test.txt

COPY . /usr/app
