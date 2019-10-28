FROM python:3.7.5-alpine3.10

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt  .

RUN set -e; \
    apk add --no-cache --virtual .build-deps \
      build-base \
      libffi-dev \
      openssl-dev \
      libxml2-dev \
      libxslt-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY app.py .
COPY resource_module_explorer resource_module_explorer
COPY templates templates
COPY static static
CMD [ "python", "./app.py" ]
