#!/bin/bash

set -e
docker-compose \
    -f docker-compose.yml \
    -f docker-compose-dev.yml \
    run backend bash