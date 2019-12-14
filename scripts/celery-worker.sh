#!/bin/bash
celery -A say.api.celery worker --loglevel=DEBUG --concurrency 4
