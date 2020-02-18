#!/bin/bash
alembic upgrade head
gunicorn -b 0.0.0.0:5000 --threads 1 --workers 3 run:app --max-requests 100 --max-requests-jitter 132 --backlog 100

