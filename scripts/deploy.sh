#!/bin/sh

set -e

apk update && apk add openssh
eval $(ssh-agent -s)
echo "$SERVER_PRIVATE_KEY" | tr -d '\r' | ssh-add - > /dev/null

mkdir -p ~/.ssh
chmod 700 ~/.ssh

ssh-keyscan $SERVER >> ~/.ssh/known_hosts

cd /builds/$CI_PROJECT_NAMESPACE/
tar -zcvf /tmp/$CI_PROJECT_NAME.tar.gz $CI_PROJECT_NAME

cd /tmp
scp $CI_PROJECT_NAME.tar.gz $SERVER_USER@$SERVER:/tmp

ssh -t $SERVER_USER@$SERVER "
cd /tmp &&
tar -xvf $CI_PROJECT_NAME.tar.gz &&
cd $CI_PROJECT_NAME &&
docker build -t $REPO_UPLOAD_ADD . &&
cd /home/server/say-installer &&
docker-compose up -d &&
docker image prune -af
"
echo 'DONE'
