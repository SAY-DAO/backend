FROM python:3.8 AS compile-image

# We copy just the requirements.txt first to leverage Docker cache

ENV VIRTUAL_ENV=/opt/venv

RUN pip install virtualenv

RUN virtualenv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .

RUN pip install -r requirements.txt

FROM python:3.8-slim AS ready-image

ENV VIRTUAL_ENV=/opt/venv
COPY --from=compile-image $VIRTUAL_ENV $VIRTUAL_ENV

FROM ready-image AS runtime-image

ENV VIRTUAL_ENV=/opt/venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . /app

WORKDIR /app

CMD ["./scripts/run.sh"]

