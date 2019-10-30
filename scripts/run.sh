#!/bin/bash
alembic upgrade head
gunicorn -b 0.0.0.0:5000 --threads 4 run:app
