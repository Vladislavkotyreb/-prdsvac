#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/vacancy-bot}"
SERVICE_NAME="vacancy-bot"

echo "==> Установка зависимостей системы"
sudo apt-get update -qq
sudo apt-get install -y python3 python3-venv python3-pip

echo "==> Python venv и пакеты"
cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  echo "ОШИБКА: файл .env не найден в $APP_DIR"
  echo "Скопируйте .env с Mac перед запуском setup-server.sh"
  exit 1
fi

mkdir -p data

echo "==> systemd-сервис"
sudo cp deploy/gcp/vacancy-bot.service /etc/systemd/system/${SERVICE_NAME}.service
sudo sed -i "s|REPLACE_USER|${USER}|g" /etc/systemd/system/${SERVICE_NAME}.service

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo ""
echo "==> Готово!"
sudo systemctl status "${SERVICE_NAME}" --no-pager
echo ""
echo "Логи:  journalctl -u ${SERVICE_NAME} -f"
echo "Стоп:  sudo systemctl stop ${SERVICE_NAME}"
echo "Старт: sudo systemctl start ${SERVICE_NAME}"
