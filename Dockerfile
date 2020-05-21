FROM tiangolo/uvicorn-gunicorn:python3.8
MAINTAINER Mark Vander Stel <mvndrstl@gmail.com>

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir --requirement /tmp/requirements.txt

ENV MODULE_NAME=slack_api

COPY . /app
WORKDIR /app
