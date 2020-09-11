FROM python:3.8 AS base

ENV VIRTUAL_ENV=/opt/venv

RUN pip install virtualenv

RUN virtualenv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .

RUN pip install -r requirements.txt

FROM python:3.8-slim AS prod

RUN apt update && apt install httpie

ENV VIRTUAL_ENV=/opt/venv
COPY --from=base $VIRTUAL_ENV $VIRTUAL_ENV

COPY . /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# check every 5s to ensure this service returns HTTP 200
HEALTHCHECK --interval=5s --timeout=3s --start-period=30s --retries=3 \ 
    CMD http http://localhost:5000/healthz || exit 1

CMD ["./scripts/run.sh"]

