#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
REMOTE_DIR="vacancy-bot"

usage() {
  echo "Способ 1 (gcloud): $0 INSTANCE ZONE"
  echo "  Пример:          $0 vacancy-bot us-central1-a"
  echo ""
  echo "Способ 2 (ssh):    $0 USER@IP"
  echo "  Пример:          $0 myuser@34.123.45.67"
  exit 1
}

[[ $# -ge 1 ]] || usage

echo "==> Подготовка каталога на сервере"

if [[ "$1" == *"@"* ]]; then
  TARGET="$1"
  SSH_OPTS=(-o StrictHostKeyChecking=accept-new)

  ssh "${SSH_OPTS[@]}" "$TARGET" "mkdir -p ${REMOTE_DIR}/data"

  rsync -avz -e "ssh ${SSH_OPTS[*]}" \
    --exclude '.venv' --exclude '__pycache__' --exclude '.DS_Store' \
    --exclude '.env8859745184*' \
    "$PROJECT_DIR/bot" \
    "$PROJECT_DIR/requirements.txt" \
    "$PROJECT_DIR/deploy" \
    "${TARGET}:${REMOTE_DIR}/"

  [[ -f "$PROJECT_DIR/.env" ]] && scp "${SSH_OPTS[@]}" "$PROJECT_DIR/.env" "${TARGET}:${REMOTE_DIR}/.env"
  [[ -f "$PROJECT_DIR/data/vacancies.db" ]] && scp "${SSH_OPTS[@]}" "$PROJECT_DIR/data/vacancies.db" "${TARGET}:${REMOTE_DIR}/data/"

  echo ""
  echo "На сервере: ssh $TARGET"
  echo "cd ~/vacancy-bot && bash deploy/gcp/setup-server.sh"

elif command -v gcloud >/dev/null 2>&1; then
  INSTANCE="$1"
  ZONE="${2:-us-central1-a}"

  gcloud compute ssh "$INSTANCE" --zone="$ZONE" --command="mkdir -p ${REMOTE_DIR}/data"

  gcloud compute scp --recurse \
    "$PROJECT_DIR/bot" \
    "$PROJECT_DIR/requirements.txt" \
    "$PROJECT_DIR/deploy" \
    "${INSTANCE}:${REMOTE_DIR}/" \
    --zone="$ZONE"

  if [[ -f "$PROJECT_DIR/.env" ]]; then
    gcloud compute scp "$PROJECT_DIR/.env" "${INSTANCE}:${REMOTE_DIR}/.env" --zone="$ZONE"
  fi
  if [[ -f "$PROJECT_DIR/data/vacancies.db" ]]; then
    gcloud compute scp "$PROJECT_DIR/data/vacancies.db" "${INSTANCE}:${REMOTE_DIR}/data/" --zone="$ZONE"
    echo "База vacancies.db скопирована"
  fi

  echo ""
  echo "На сервере:"
  echo "gcloud compute ssh $INSTANCE --zone=$ZONE"
  echo "cd ~/vacancy-bot && bash deploy/gcp/setup-server.sh"
else
  echo "gcloud не установлен: brew install --cask google-cloud-sdk"
  echo "Или используйте IP: $0 USER@EXTERNAL_IP"
  exit 1
fi
