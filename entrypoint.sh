#!/bin/bash

: "${GUNICORN_BIND:=0.0.0.0:3000}"
: "${GUNICORN_WORKERS:=1}"
: "${GUNICORN_ACCESS_LOG:=-}"   # default to STDOUT
: "${GUNICORN_ERROR_LOG:=-}"    # default to STDERR
: "${GUNICORN_GRACEFUL_TIMEOUT:=30}"


# Start Gunicorn
exec gunicorn --bind "$GUNICORN_BIND" \
              --workers "$GUNICORN_WORKERS" \
              --access-logfile "$GUNICORN_ACCESS_LOG" \
              --error-logfile "$GUNICORN_ERROR_LOG" \
              --graceful-timeout "$GUNICORN_GRACEFUL_TIMEOUT"\
              wsgi:app

