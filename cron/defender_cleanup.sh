#!/bin/bash
export HOME=/home/app
cd /home/app/
/usr/local/bin/poetry run python src/manage.py cleanup_django_defender
