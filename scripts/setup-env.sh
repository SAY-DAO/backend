#!/bin/bash

set -e

if [ $CI_COMMIT_REF_SLUG == 'release' ]; then
    echo TAG='release'
    echo ENVIRONMENT='production'
    echo DOMAIN='sayapp.company'
elif [ $CI_COMMIT_REF_SLUG == 'master' ]; then
    echo TAG='release'
    echo ENVIRONMENT='staging'
    echo DOMAIN='s.sayapp.company'
else
    echo TAG='develop'
    echo ENVIRONMENT='development'
    echo DOMAIN='d.sayapp.company'
fi
