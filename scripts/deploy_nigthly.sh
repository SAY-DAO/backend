#!/bin/sh

set -e
export CI_PROJECT_NAME_NIGTHLY=$CI_PROJECT_NAME-nigthly
export CI_PROJECT_DIR_NIGTHLY=/tmp/nigthly
export IMAGE_NAME=$REPO_UPLOAD_ADD-nigthly
apk update && apk upgrade && apk add openssh
eval $(ssh-agent -s)
echo "$SERVER_PRIVATE_KEY" | tr -d '\r' | ssh-add - > /dev/null

mkdir -p ~/.ssh
chmod 700 ~/.ssh

ssh-keyscan $SERVER >> ~/.ssh/known_hosts

cd /builds/$CI_PROJECT_NAMESPACE/
tar -zcf /tmp/$CI_PROJECT_NAME_NIGTHLY.tar.gz --exclude=.git $CI_PROJECT_NAME

cd /tmp
scp $CI_PROJECT_NAME_NIGTHLY.tar.gz $SERVER_USER@$SERVER:$CI_PROJECT_DIR_NIGTHLY
ssh -t $SERVER_USER@$SERVER "
cd $CI_PROJECT_DIR_NIGTHLY &&
tar -xvf $CI_PROJECT_NAME_NIGTHLY.tar.gz &&
cd $CI_PROJECT_NAME &&
docker build -t $IMAGE_NAME . -f Dockerfile_nigthly &&
cd /home/server/say-installer-nigthly &&
docker-compose up -d &&
docker image prune -a
"
echo 'DONE'
