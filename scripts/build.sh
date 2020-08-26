#!/bin/bash

set -e

export BASE_IMAGE=${BASE_IMAGE?not set}
export CONTAINER_IMAGE=${CONTAINER_IMAGE?not set}
export LATEST_IMAGE=${LATEST_IMAGE?not set}
export CI_COMMIT_REF_SLUG=$CI_COMMIT_REF_SLUG

export LATEST_BRANCH="master"

if [ $CI_COMMIT_REF_SLUG == $LATEST_BRANCH ]; then
	export LATEST_TAG="-t $LATEST_IMAGE"
else
	export LATEST_TAG=""
fi

docker pull $BASE_IMAGE || true
docker build --cache-from $BASE_IMAGE --target base -t $BASE_IMAGE .
docker build --cache-from $BASE_IMAGE --target prod -t $CONTAINER_IMAGE $LATEST_TAG .

