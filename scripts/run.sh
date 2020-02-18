#!/bin/bash
alembic upgrade head
gunicorn -b 0.0.0.0:5000 --threads 2 --workers 4 run:app --max-requests 100 -max_requests_jitter 42 --backlog 100
