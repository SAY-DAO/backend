#!/bin/bash
alembic upgrade head
gunicorn -b 0.0.0.0:5000 --workers 5 wsgi:app -t 60
