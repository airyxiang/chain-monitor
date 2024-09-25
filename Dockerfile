ARG BASE_IMAGE="python:3.8.20-slim-bullseye"
FROM ${BASE_IMAGE}

ARG FURY_AUTH

WORKDIR /home/app

RUN mkdir -p /home/configurations

# Install expensive things
RUN \
  apt-get update \
  && apt-get install -y libpq-dev g++ linux-headers-generic libffi-dev libssl-dev vim \
  && pip install pip==22.1.2 pip-tools==6.6.2 \
  && apt-get clean

COPY requirements /requirements

RUN pip-sync /requirements/requirements.txt

# Copy rest of files
COPY . /home/app

RUN mkdir /etc/supervisor.d && ln -s /home/app/infra/supervisord.conf /etc/ && \
    mkdir /var/log/supervisor && \
    groupadd web && useradd web -g web

RUN pip install -e .

RUN chmod 444 /home/app/chain_monitor/configurations/scheduler.py && chmod -R 444 /home/app/infra/ && chmod -R 555 /home/app/entrypoint/

CMD "/home/app/entrypoint/run-scheduler.sh"
