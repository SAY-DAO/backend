FROM python:3.8 AS base

ENV VIRTUAL_ENV=/opt/venv

RUN pip install virtualenv

RUN virtualenv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .

RUN pip install -r requirements.txt

FROM python:3.8-slim AS prod

ENV VIRTUAL_ENV=/opt/venv
COPY --from=base $VIRTUAL_ENV $VIRTUAL_ENV

COPY . /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ARG CI_COMMIT_REF_SLUG
LABEL traefik.backend=${CI_COMMIT_REF_SLUG}_api
LABEL traefik.frontend.rule=Host:api.${CI_COMMIT_REF_SLUG}.s.sayapp.company
LABEL traefik.docker.network=staging 
LABEL traefik.enable=true 
LABEL traefik.port=5000 
LABEL traefik.default.protocol=http

CMD ["./scripts/run.sh"]

