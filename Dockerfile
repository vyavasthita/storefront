FROM python:3.11.3-alpine3.18

WORKDIR /app
EXPOSE 5001

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add --no-cache mariadb-dev

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install mysqlclient

COPY ./storefront /app/storefront
COPY ./store /app/store
COPY ./tags /app/tags
# COPY ./migrations /app/migrations
COPY manage.py .
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]
