#!/bin/bash
ln -sf /home/app/infra/supervisor-scheduler.ini /etc/supervisor.d/ &&
source /home/app/entrypoint/init_logs.sh

exec supervisord -n -c /etc/supervisord.conf
