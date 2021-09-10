FROM python:3.8 AS base

ENV VIRTUAL_ENV=/opt/venv

RUN pip install virtualenv
RUN pip install --upgrade pip

RUN virtualenv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .

RUN pip install -r requirements.txt

FROM python:3.8-slim AS prod

RUN apt update && apt install curl -y

ENV VIRTUAL_ENV=/opt/venv
COPY --from=base $VIRTUAL_ENV $VIRTUAL_ENV

COPY . /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# check every 5s to ensure this service returns HTTP 200
HEALTHCHECK --interval=10s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -fs http://localhost:5000/api/healthz || exit 1

CMD ["./scripts/run.sh"]

FROM prod as development
COPY requirements-dev.txt .
RUN pip install virtualenv
RUN virtualenv $VIRTUAL_ENV
RUN pip install -r requirements-dev.txt
CMD ["./scripts/dev-run.sh"]
