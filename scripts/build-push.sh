#!/bin/bash

set -e

export BASE_IMAGE=${BASE_IMAGE?not set}
export CONTAINER_IMAGE=${CONTAINER_IMAGE?not set}
export LATEST_IMAGE=${LATEST_IMAGE?not set}

sh ./scripts/build.sh

docker push $BASE_IMAGE
docker push $CONTAINER_IMAGE
docker push $LATEST_IMAGE || true

