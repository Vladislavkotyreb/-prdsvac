#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Использование: $0 USER@SERVER_IP /path/to/ssh-key.pem"
  echo "Пример:       $0 ubuntu@123.45.67.89 ~/Downloads/ssh-key-2026.pem"
  exit 1
fi

TARGET="$1"
SSH_KEY="$2"
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
REMOTE_DIR="~/vacancy-bot"

SSH_OPTS=(-i "$SSH_KEY" -o StrictHostKeyChecking=accept-new)

echo "==> Загрузка проекта на $TARGET"
ssh "${SSH_OPTS[@]}" "$TARGET" "mkdir -p vacancy-bot/data"

rsync -avz -e "ssh ${SSH_OPTS[*]}" \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.DS_Store' \
  --exclude '.env8859745184*' \
  "$PROJECT_DIR/bot" \
  "$PROJECT_DIR/requirements.txt" \
  "$PROJECT_DIR/deploy" \
  "$TARGET:$REMOTE_DIR/"

if [[ -f "$PROJECT_DIR/.env" ]]; then
  scp "${SSH_OPTS[@]}" "$PROJECT_DIR/.env" "$TARGET:$REMOTE_DIR/.env"
else
  echo "ВНИМАНИЕ: .env не найден локально — создайте его на сервере вручную"
fi

if [[ -f "$PROJECT_DIR/data/vacancies.db" ]]; then
  scp "${SSH_OPTS[@]}" "$PROJECT_DIR/data/vacancies.db" "$TARGET:$REMOTE_DIR/data/"
  echo "База vacancies.db скопирована"
else
  echo "База не найдена — на сервере создастся новая при первом запуске"
fi

echo ""
echo "==> Файлы загружены. Теперь на сервере:"
echo "ssh -i \"$SSH_KEY\" $TARGET"
echo "cd ~/vacancy-bot && bash deploy/oracle/setup-server.sh"
