#! /bin/bash

set -ex

./manage.py migrate --no-color
./manage.py runserver -v3 --no-color "$@" 2>&1