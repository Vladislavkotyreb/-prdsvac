# Деплой на Google Cloud (Always Free e2-micro, 24/7)

Бесплатная VM **навсегда** в регионах: `us-west1`, `us-central1`, `us-east1`.

> **Карта:** Google тоже просит карту для верификации. Виртуальные карты часто не проходят — попробуйте обычную дебетовую МИР/Visa. Если не получится → [deploy/github/README.md](../github/README.md) (без карты).

---

## Часть 1. Google Cloud — создать VM

### 1. Регистрация
1. [console.cloud.google.com](https://console.cloud.google.com)
2. Войти через Google-аккаунт
3. Активировать пробный период / привязать карту (Always Free e2-micro не списывает деньги в лимитах)

### 2. Новый проект
1. Вверху: **Select a project** → **New Project**
2. Имя: `vacancy-bot` → **Create**

### 3. Включить Compute Engine
1. Меню **☰** → **Compute Engine** → **VM instances**
2. Нажмите **Enable** (если просит)

### 4. Создать VM
**Create Instance:**

| Параметр | Значение |
|----------|----------|
| Name | `vacancy-bot` |
| Region | **us-central1** (Iowa) |
| Zone | `us-central1-a` |
| Machine type | **e2-micro** (0.25–2 vCPU, 1 GB) — **Eligible for free tier** |
| Boot disk | **Ubuntu 22.04 LTS**, 10–30 GB standard persistent disk |
| Firewall | ✅ Allow HTTP traffic — **не обязательно** (можно выключить) |
| | ✅ Allow HTTPS traffic — **не обязательно** |

**Advanced → Networking → Network interfaces → External IPv4:** **Ephemeral** (публичный IP).

**Create**.

> ⚠️ e2-micro бесплатен **только** в `us-west1`, `us-central1`, `us-east1`. Другие регионы — платные.

### 5. SSH-доступ
По умолчанию порт 22 открыт. Подключение:
- Кнопка **SSH** в консоли (браузер), или
- `gcloud compute ssh vacancy-bot --zone=us-central1-a`

Запомните **имя пользователя** в терминале (часто совпадает с Google-аккаунтом, например `vladislav`).

---

## Часть 2. Google Cloud SDK на Mac (опционально)

```bash
brew install --cask google-cloud-sdk
gcloud init
gcloud auth login
gcloud config set project vacancy-bot
```

Без SDK можно подключаться через **SSH в браузере** и загружать файлы через `scp` по внешнему IP.

---

## Часть 3. Загрузка бота

### Вариант A — через gcloud
```bash
cd "/Users/vladislavkotyrev/Desktop/тг бот парсер вакансий"
chmod +x deploy/gcp/upload-from-mac.sh
./deploy/gcp/upload-from-mac.sh vacancy-bot us-central1-a
```

### Вариант B — через IP
1. В консоли GCP скопируйте **External IP** VM
2. ```bash
   ./deploy/gcp/upload-from-mac.sh ВАШ_USER@EXTERNAL_IP
   ```
   `ВАШ_USER` — имя из SSH-сессии (не `root`).

---

## Часть 4. Установка на сервере

```bash
# через gcloud:
gcloud compute ssh vacancy-bot --zone=us-central1-a

# или:
ssh ВАШ_USER@EXTERNAL_IP

cd ~/vacancy-bot
chmod +x deploy/gcp/setup-server.sh
bash deploy/gcp/setup-server.sh
```

Проверка:
```bash
sudo systemctl status vacancy-bot
journalctl -u vacancy-bot -f
```

Telegram: `/start` → бот отвечает.

---

## Часть 5. Остановить бота на Mac

```bash
pkill -f "python -m bot.main"
```

---

## Обновление

```bash
./deploy/gcp/upload-from-mac.sh vacancy-bot us-central1-a
gcloud compute ssh vacancy-bot --zone=us-central1-a --command="cd ~/vacancy-bot && source .venv/bin/activate && pip install -r requirements.txt && sudo systemctl restart vacancy-bot"
```

---

## Полезные команды

| Действие | Команда |
|----------|---------|
| Статус VM | GCP Console → Compute Engine → VM instances |
| Статус бота | `sudo systemctl status vacancy-bot` |
| Логи | `journalctl -u vacancy-bot -f` |
| Перезапуск | `sudo systemctl restart vacancy-bot` |
| Остановить VM (экономия, бот offline) | GCP Console → Stop |

---

## Частые проблемы

**Карта не проходит** — попробуйте GitHub Actions ([deploy/github/README.md](../github/README.md)) или VPS с оплатой СБП (Timeweb ~200 ₽/мес).

**`e2-micro` не free tier** — проверьте регион (только US: west1, central1, east1).

**Out of memory** — e2-micro имеет 1 GB; боту хватает. Если падает: добавьте swap:
```bash
sudo fallocate -l 1G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
```

**HH.ru 403** — проверьте `HH_USER_AGENT` с email в `.env`.

**Два бота одновременно** — остановите процесс на Mac.

---

## Лимиты Always Free

- 1 × **e2-micro** VM в месяц (в разрешённых регионах)
- 30 GB standard persistent disk
- Исходящий трафик: 1 GB/мес из North America (для Telegram/API обычно хватает; следите в Billing)
