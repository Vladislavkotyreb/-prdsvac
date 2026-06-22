# Деплой через GitHub Actions (без карты)

Бесплатно. Карта **не нужна**.

---

## Как управлять ботом

Бот **не online** в Telegram — управление через **GitHub** (сайт или приложение).

### Панель управления

Репозиторий → вкладка **Actions** → **Daily Vacancies** → **Run workflow**

| Режим | Что делает | Аналог |
|-------|------------|--------|
| **fetch** | Парсит площадки, постит новые в канал | `/fetch` |
| **test** | Тестовое сообщение с 3 вакансиями в канал | `/test` |
| **status** | Отчёт о последнем прогоне | `/status` |

Выберите режим → **Run workflow** → через 1–2 минуты результат.

### Автоматически

Каждый день с **12:00 МСК** (если GitHub задержал — догоняет при ближайшем часовом запуске, но **не чаще одного раза в день**).

### Уведомления в Telegram (опционально)

Добавьте секрет `TELEGRAM_ADMIN_ID` — ваш личный Telegram ID (узнать у [@userinfobot](https://t.me/userinfobot)).

После каждого ручного/авто прогона бот пришлёт вам в личку:
- «Найдено X, опубликовано Y»
- или «Новых вакансий нет»

Режим **status** тоже придёт в личку, если задан `TELEGRAM_ADMIN_ID`.

### Логи

**Actions** → клик на run → **Run bot** → полный вывод (ошибки парсеров, HH 403 и т.д.).

### С телефона

Установите **GitHub** ([iOS](https://apps.apple.com/app/github/id1477376905) / [Android](https://play.google.com/store/apps/details?id=com.github.android)) → ваш репозиторий → **Actions** → **Run workflow**.

---

## Что работает / не работает

| ✅ Работает | ❌ Не работает |
|------------|----------------|
| Автопостинг в 12:00 | `/fetch` прямо в Telegram |
| Ручной запуск из GitHub | `/start` в Telegram |
| Тест и статус через GitHub | Бот не отвечает мгновенно на команды |
| Дедупликация (кэш базы) | |

---

## Установка

### 1. Репозиторий на GitHub

```bash
cd "/Users/vladislavkotyrev/Desktop/тг бот парсер вакансий"
git init
git add bot requirements.txt .github deploy README.md .env.example .gitignore
git commit -m "Vacancy bot with GitHub Actions"
```

Создайте репо на [github.com/new](https://github.com/new) → push:

```bash
git remote add origin https://github.com/ВАШ_ЛОГИН/vacancy-bot.git
git branch -M main
git push -u origin main
```

### 2. Секреты

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret | Обязательно | Значение |
|--------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | ✅ | токен от @BotFather |
| `TELEGRAM_CHAT_ID` | ✅ | `-1004396616905` |
| `HH_USER_AGENT` | ✅ | `ProductDesignerVacancyBot/1.0 (kotvlad2016@gmail.com)` |
| `TELEGRAM_ADMIN_ID` | ⬜ | ваш ID от @userinfobot (уведомления в личку) |

### 3. Первый запуск

**Actions** → **Daily Vacancies** → **Run workflow** → mode: **fetch**

### 4. Остановить бота на Mac

```bash
pkill -f "python -m bot.main"
```

---

## База вакансий

Хранится в **GitHub Actions cache** между запусками. Если cache сбросится — часть вакансий может повторно уйти в канал как «новые» (редко).

Перед миграцией с Mac: один раз `/fetch` локально, чтобы база была актуальной — затем первый run в Actions сохранит cache.

---

## Схема

```
Вы → GitHub Actions (Run workflow)
         ↓
    парсинг HH, Habr, GeekJob, GetMatch
         ↓
    новые вакансии → Telegram-канал
         ↓
    (опционально) отчёт → ваш Telegram
```
