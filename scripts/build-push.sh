#!/bin/bash

set -e

sh ./scripts/build.sh

docker push $BASE_IMAGE
docker push $CONTAINER_IMAGE
