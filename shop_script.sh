#!/bin/bash

cd
cd Documents/portfolio/shop
source venv/bin/activate
cd shop
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
open http://127.0.0.1:8000
