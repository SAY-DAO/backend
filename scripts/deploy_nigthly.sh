#!/bin/sh

set -e

ssh -t $SERVER_USER@$SERVER "
docker login $DOCKER_REGISTRY -u $REGISTRY_USER -p $REGISTRY_PASSWORD

#cd $CI_PROJECT_DIR_NIGHTLY &&
#tar -xvf $CI_PROJECT_NAME_NIGHTLY.tar.gz &&
#cd $CI_PROJECT_NAME &&
#docker build -t $NIGHTLY_IMAGE_NAME . -f Dockerfile_nigthly &&
#cd .. &&
#rm -rf $CI_PROJECT_NAME $CI_PROJECT_NAME_NIGHTLY.tar.gz &&
#cd /home/server/say-installer &&
#docker-compose up -d
#"
echo 'DONE'
