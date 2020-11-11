#!/bin/bash

set -e

docker pull $BASE_IMAGE || true
docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    --cache-from $BASE_IMAGE \
    --target base \
    -t $BASE_IMAGE \
    .

docker pull $CONTAINER_IMAGE || true
docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    --cache-from $BASE_IMAGE \
    --cache-from $CONTAINER_IMAGE \
    --target prod \
    -t $CONTAINER_IMAGE \
    .
