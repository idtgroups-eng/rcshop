#!/usr/bin/env bash
python manage.py makemigrations main
python manage.py migrate
python manage.py collectstatic --noinput
