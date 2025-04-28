#!/bin/bash

source .env

until nc -z $POSTGRES_HOST 5432; do
    echo "$(date) - waiting for database..."
    sleep 2
done

set -e
NUM_WORKERS=3
PORT=8000

echo "USER"
whoami
cat /etc/group
ls -l ./

echo "Poetry install"
poetry lock
poetry install --no-root

echo "Collect static files"
poetry run python ./src/manage.py collectstatic --noinput

echo "First fix migrations if needed"
poetry run python ./src/manage.py makemigrations --merge --noinput

echo "Apply migrations"
poetry run python ./src/manage.py migrate

echo "Start cron backups schedule"
mkdir -p $HOME/backups
touch $HOME/logs/backups_log.log
chmod 777 -R $HOME/logs/backups_log.log
touch $HOME/logs/cron_log.log
chmod 777 -R $HOME/logs/cron_log.log
chmod 777 -R $HOME
crontab $HOME/cron/crontab_jobs

if [ "$DEBUG" == 0 ]; then
  echo "Start as PROD"
  cd src/
  cron && poetry run gunicorn settings.wsgi:application -w $NUM_WORKERS \
    --capture-output --reload \
    --bind 0.0.0.0:$PORT --chdir /home/app \
    --enable-stdio-inheritance \
    --log-config gunicorn-log.conf;
else
  echo "Start as LOCAL"
  cron && poetry run python3 ./src/manage.py runserver 0.0.0.0:$PORT
fi
