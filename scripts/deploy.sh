#!/bin/sh

set -e
export IMAGE_NAME=$REPO_UPLOAD_ADD

apk update && apk add openssh
eval $(ssh-agent -s)
echo "$SERVER_PRIVATE_KEY" | tr -d '\r' | ssh-add - > /dev/null

mkdir -p ~/.ssh
chmod 700 ~/.ssh

ssh-keyscan $SERVER >> ~/.ssh/known_hosts

cd /builds/$CI_PROJECT_NAMESPACE/
tar -zcvf /tmp/$CI_PROJECT_NAME.tar.gz --exclude=.git $CI_PROJECT_NAME

cd /tmp
scp $CI_PROJECT_NAME.tar.gz $SERVER_USER@$SERVER:/tmp

ssh -t $SERVER_USER@$SERVER "
cd /tmp &&
tar -xvf $CI_PROJECT_NAME.tar.gz &&
cd $CI_PROJECT_NAME &&
docker build -t $IMAGE_NAME . &&
cd .. &&
rm -rf $CI_PROJECT_NAME $CI_PROJECT_NAME.tar.gz &&
cd /home/server/say-installer &&
docker-compose up -d
"
echo 'DONE'
