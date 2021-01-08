FROM tiangolo/uvicorn-gunicorn:python3.8-slim
MAINTAINER Mark Vander Stel <mvndrstl@gmail.com>

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir --requirement /tmp/requirements.txt

ENV MODULE_NAME=slack_api \
    MAX_WORKERS=1 \
    HOST='[::]'

RUN mkdir -p /var/db && \
    echo "{}" > /var/db/users.json && \
    ln -s /var/db/users.json /app/users.json
VOLUME /var/db

COPY . /app
WORKDIR /app
