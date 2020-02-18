#!/bin/bash
alembic upgrade head
gunicorn -b 0.0.0.0:5000 --threads 1 --workers 2 run:app --reload
