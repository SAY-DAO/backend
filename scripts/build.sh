#!/bin/bash

set -e

docker pull $BASE_IMAGE || true
docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    --cache-from $BASE_IMAGE \
    --target base \
    -t $BASE_IMAGE \
    .

docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    --cache-from $BASE_IMAGE \
    --target prod \
    -t $CONTAINER_IMAGE \
    .
