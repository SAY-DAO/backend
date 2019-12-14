#!/bin/bash

celery -A say.api.celery beat -S redbeat.RedBeatScheduler
