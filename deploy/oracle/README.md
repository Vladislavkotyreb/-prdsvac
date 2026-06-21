# Деплой на Oracle Cloud (бесплатно 24/7)

## Часть 1. Создание сервера в Oracle Cloud

### 1. Регистрация
1. Откройте [cloud.oracle.com](https://cloud.oracle.com) → **Sign Up**
2. Укажите страну, email, добавьте карту (верификация, списаний не будет в рамках Free Tier)
3. Выберите домашний регион (например **Germany Central** или **France Central**)

### 2. Создание VM
1. Меню **☰** → **Compute** → **Instances** → **Create instance**
2. Имя: `vacancy-bot`
3. **Image:** Ubuntu 22.04 (Canonical)
4. **Shape:** **Ampere** → `VM.Standard.A1.Flex`
   - OCPU: **1**
   - Memory: **6 GB** (можно меньше, 1 GB тоже хватит)
5. **Networking:** создайте VCN по умолчанию (Create new virtual cloud network)
6. **SSH keys:** **Generate a key pair for me** → скачайте `.pem` файл
7. **Create**

> Если ARM недоступен в регионе — попробуйте другой регион или shape AMD `VM.Standard.E2.1.Micro` (тоже Always Free, но слабее).

### 3. Открыть SSH (порт 22)
1. На странице instance → **Subnet** → **Default Security List**
2. **Add Ingress Rules:**
   - Source CIDR: `0.0.0.0/0` (или ваш IP для безопасности)
   - IP Protocol: TCP
   - Destination Port: **22**

### 4. Узнать публичный IP
На странице instance скопируйте **Public IP address**.

---

## Часть 2. Загрузка бота с Mac

```bash
cd "/Users/vladislavkotyrev/Desktop/тг бот парсер вакансий"
chmod +x deploy/oracle/upload-from-mac.sh
./deploy/oracle/upload-from-mac.sh ubuntu@ВАШ_IP ~/Downloads/ssh-key-XXXX.pem
```

Замените `ВАШ_IP` и путь к `.pem` файлу.

---

## Часть 3. Установка на сервере

```bash
ssh -i ~/Downloads/ssh-key-XXXX.pem ubuntu@ВАШ_IP
cd ~/vacancy-bot
chmod +x deploy/oracle/setup-server.sh
bash deploy/oracle/setup-server.sh
```

Проверка:
```bash
sudo systemctl status vacancy-bot
journalctl -u vacancy-bot -f
```

В Telegram: напишите боту `/start` — должен ответить.

---

## Часть 4. Остановить бота на Mac

Чтобы не было двух копий одновременно:

```bash
pkill -f "python -m bot.main"
```

---

## Обновление бота после изменений

```bash
# на Mac — снова загрузить файлы
./deploy/oracle/upload-from-mac.sh ubuntu@ВАШ_IP ~/Downloads/ssh-key-XXXX.pem

# на сервере
ssh -i ~/Downloads/ssh-key-XXXX.pem ubuntu@ВАШ_IP
cd ~/vacancy-bot
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart vacancy-bot
```

---

## Полезные команды

| Действие | Команда |
|----------|---------|
| Статус | `sudo systemctl status vacancy-bot` |
| Логи | `journalctl -u vacancy-bot -f` |
| Перезапуск | `sudo systemctl restart vacancy-bot` |
| Остановка | `sudo systemctl stop vacancy-bot` |

---

## Частые проблемы

**ARM shape недоступен** — смените регион или попробуйте позже (Oracle иногда ограничивает capacity).

**`chat not found`** — проверьте `TELEGRAM_CHAT_ID` в `.env` (для канала: `-100...`).

**HH.ru 403** — проверьте `HH_USER_AGENT` с реальным email в `.env`.

**Бот не отвечает** — `journalctl -u vacancy-bot -n 50` и убедитесь, что на Mac бот остановлен.
