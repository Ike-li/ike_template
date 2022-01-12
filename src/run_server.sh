#!/bin/bash

# run flask
gunicorn -c extensions/gunicorn_config.py wsgi:app
