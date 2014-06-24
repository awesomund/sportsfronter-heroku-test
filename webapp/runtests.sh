#!/bin/bash

modules="management event"

python manage.py test $modules --settings=sportsfronter.settings_dev

