FROM python:3.10.5-slim-bullseye

RUN \
  apt-get update \
  && apt-get install -y libpq-dev \
  && apt-get clean

RUN pip install pip-tools==6.6.2
