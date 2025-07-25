# Backend of SAY App and Panel

[![Build, Test and Deploy](https://github.com/SAY-DAO/backend/actions/workflows/pipeline.yml/badge.svg)](https://github.com/SAY-DAO/backend/actions/workflows/pipeline.yml)
[![codecov](https://codecov.io/gh/SAY-DAO/backend/branch/master/graph/badge.svg?token=RXJ4EXVIR0)](https://codecov.io/gh/SAY-DAO/backend)

### Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker-Compose](https://docs.docker.com/compose/install/)

### Commands

#### Run Server

```bash
./scripts/up.sh
```


    Server Address: http://127.0.0.1:5000/
    API Doc: http://127.0.0.1:5000/apidocs/#/

#### Build Image

You need build manually when changing `DOCKERFILE` or `requirements`.

```bash
./scripts/build.sh
```

#### Run Tests

```bash
./scripts/test.sh
```

#### Access Shell

```bash
./scripts/bash.sh
```
