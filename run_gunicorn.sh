#!/usr/bin/env bash

PORT=5123
WORKERS=3
APP_MODULE="app:app"
LOGFILE="app.log"

fuser -k ${PORT}/tcp 2>/dev/null

nohup gunicorn \
  -w ${WORKERS} \
  -b 127.0.0.1:${PORT} \
  ${APP_MODULE} \
  > ${LOGFILE} 2>&1 &

disown
