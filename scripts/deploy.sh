#!/bin/bash

set -e

if [ $ENVIRONMENT = 'prod' ]
then
    OVERRIDE_IF_PROD='-f docker-compose-prod.yml'
else
    OVERRIDE_IF_PROD=''
fi

docker-compose \
    -f docker-compose.yml \
    $OVERRIDE_IF_PROD \
    config > docker-stack.yml

docker stack deploy \
    --prune \
    --with-registry-auth \
    --resolve-image=always \
    -c docker-stack.yml \
    $STACK_NAME