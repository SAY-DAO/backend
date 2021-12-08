# COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 \
# USER_ID="$(id -u)" GROUP_ID="$(id -g)" \
docker-compose \
    -f docker-compose.yml \
    -f docker-compose-dev.yml \
    up --remove-orphans backend