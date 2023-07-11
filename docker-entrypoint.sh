#!/bin/sh

echo "Running makemigrations"
python manage.py makemigrations core
python manage.py makemigrations store
python manage.py makemigrations tags

echo "Running migrate"
python manage.py migrate

echo "Create Super User"
# python manage.py createsuperuser --no-input --username admin --email admin@admin.com

if [ "$CREATE_SUPER_USER" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

echo "Running django server"
# gunicorn -c config/gunicorn/dev.py
python manage.py runserver 0.0.0.0:5001
