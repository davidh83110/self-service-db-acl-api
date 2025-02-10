FROM python:3.10-slim

WORKDIR /app

ARG APP_VERSION=0.1.0
ENV APP_VERSION=${APP_VERSION}

RUN apt-get update && \
    apt-get install redis-tools -y && \
    apt-get autoclean && apt-get autoremove -y

COPY . /app
COPY Pipfile ./
COPY Pipfile.lock ./

# Ignore Pipfile means we will use Pipfile.lock directly.
RUN pip install pipenv --no-cache-dir && \
    pipenv install --system --deploy --ignore-pipfile

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


EXPOSE 3000

ENTRYPOINT ["/entrypoint.sh"]