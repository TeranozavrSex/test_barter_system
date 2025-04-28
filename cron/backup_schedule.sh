#!/bin/bash
export HOME=/home/app
cd /home/app/
/usr/local/bin/poetry run python /home/app/cron/backup_schedule.py
