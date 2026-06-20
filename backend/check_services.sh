#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="/Users/katykim/Desktop/Finnect-challenge/cvt-detection-project"
ENV_FILE="$ROOT_DIR/backend/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

curl -s "http://127.0.0.1:${CVT_API_PORT}/health"
echo
curl -s -u "${CVT_OPS_USERNAME}:${CVT_SHARED_PASSWORD}" "http://127.0.0.1:${CVT_OPS_PORT}/"
echo
