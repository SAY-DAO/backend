#!/bin/bash

set -e

# docker pull $BASE_IMAGE || true
# docker build \
#     --build-arg ENVIRONMENT=$ENVIRONMENT \
#     --cache-from $BASE_IMAGE \
#     --target base \
#     -t $BASE_IMAGE \
#     .

# docker pull $CONTAINER_IMAGE || true
# docker build \
#     --build-arg ENVIRONMENT=$ENVIRONMENT \
#     --cache-from $BASE_IMAGE \
#     --cache-from $CONTAINER_IMAGE \
#     --target prod \
#     -t $CONTAINER_IMAGE \
#     .

COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 \
USER_ID="$(id -u)" GROUP_ID="$(id -g)" \
docker-compose \
    -f docker-compose.yml \
    -f docker-compose-dev.yml \
    build

