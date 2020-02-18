#!/bin/bash
alembic upgrade head
gunicorn -b 0.0.0.0:5000 --threads 2 --workers 4 run:app --reload
