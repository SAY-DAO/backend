#!/bin/sh

set -e
export CI_PROJECT_NAME_NIGHTLY=$CI_PROJECT_NAME-nightly
export CI_PROJECT_DIR_NIGHTLY=/tmp/nightly

apk update && apk upgrade && apk add openssh
eval $(ssh-agent -s)
echo "$SERVER_PRIVATE_KEY" | tr -d '\r' | ssh-add - > /dev/null

mkdir -p ~/.ssh
chmod 700 ~/.ssh

ssh-keyscan $SERVER >> ~/.ssh/known_hosts

cd /builds/$CI_PROJECT_NAMESPACE/
#tar -zcf /tmp/$CI_PROJECT_NAME_NIGHTLY.tar.gz --exclude=.git $CI_PROJECT_NAME

#ssh -t $SERVER_USER@$SERVER "mkdir -p $CI_PROJECT_DIR_NIGHTLY"

#cd /tmp
#scp $CI_PROJECT_NAME_NIGHTLY.tar.gz $SERVER_USER@$SERVER:$CI_PROJECT_DIR_NIGHTLY

export STAGING_IMAGE_NAME=$DOCKER_REGISTRY/$CI_PROJECT_NAME:staging
cd $CI_PROJECT_NAME
docker build -t $STAGING_IMAGE_NAME . -f Dockerfile_nigthly
docker push	 $STAGING_IMAGE_NAME

#
#ssh -t $SERVER_USER@$SERVER "
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
