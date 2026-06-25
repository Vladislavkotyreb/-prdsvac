# Handoff: состояние проекта и история изменений

Этот файл — инструкция для следующего агента. Описывает текущее состояние
бота, что было сделано, известные баги и что ещё не готово.

---

## Текущее состояние (на 26.06.2026)

### Где запущен

Бот развёрнут на хостинге **reg.ru** (ISPmanager) у пользователя `u3452280`:

```
/var/www/u3452280/data/vacancy-bot/
```

Cron запускает публикацию **каждый день в 12:00 МСК**:
```
0 12 * * *   cd /var/www/u3452280/data/vacancy-bot && .venv/bin/python -m bot.run_once fetch
```

Python на сервере — **3.8.6**. Бот совместим через `backports.zoneinfo`.

### GitHub Actions

Расписание в `.github/workflows/daily-vacancies.yml` **отключено** — оставлен
только `workflow_dispatch` для ручного запуска. Это сделано намеренно, чтобы
GitHub и сервер не постили параллельно (у них разные SQLite базы).

### HH.ru API

Токен приложения получен и прописан в `.env` на сервере и локально.
Источник: dev.hh.ru, grant_type=client_credentials.
Токен не имеет срока истечения в ответе. Если вдруг снова появится 403 —
перевыпустить командой:

```bash
curl -s -X POST "https://hh.ru/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: ProductDesignerVacancyBot/1.0 (kotvlad2016@gmail.com)" \
  -d "grant_type=client_credentials&client_id=CLIENT_ID&client_secret=CLIENT_SECRET"
```

Client ID и Client Secret хранятся в личном кабинете dev.hh.ru.

---

## Архитектура

```
bot/
  run_once.py      — точка входа для cron/GitHub Actions
  main.py          — точка входа для long-polling режима (не используется на хостинге)
  service.py       — оркестрация: collect → filter_new → filter_fresh → dedupe → send → save
  database.py      — SQLite: таблицы vacancies + run_log
  dates.py         — утилиты дат, is_fresh(), dedupe_key(), parse_russian_date()
  config.py        — Settings.from_env(), список регионов HH и поисковых запросов
  filters.py       — фильтр «продуктовый дизайнер» по ключевым словам
  formatters.py    — форматирование HTML-сообщений для Telegram
  parsers/
    hh.py          — HH.ru REST API (Bearer token, date_from/date_to)
    habr.py        — Habr Career (scraping)
    geekjob.py     — GeekJob JSON API
    getmatch.py    — GetMatch API
    remotejob.py   — Remote-job.ru (scraping)
    base.py        — BaseParser
data/
  vacancies.db     — SQLite база (на сервере живёт постоянно)
```

### Логика одного прогона (run_once.py → service.py)

1. `should_run_scheduled_fetch` — при запуске по расписанию проверяет:
   - дата не в `SCHEDULE_SKIP_DATES`
   - успешной публикации сегодня ещё не было (`has_successful_post_today`)
   - текущий час ≥ 12 по `TIMEZONE` (верхней границы нет — GitHub часто запаздывает)
2. `collect_all` — параллельный обход всех 5 парсеров
3. `filter_new` — отсекает `uid` уже в базе + дубли по `dedupe_key(title+company)`
4. `filter_fresh` — отсекает вакансии без даты или старше `MAX_VACANCY_AGE_HOURS` (72 ч)
5. `dedupe_by_title_company` — финальная дедупликация внутри текущей выборки
6. `_send_combined` — форматирует и отправляет 1..N сообщений в Telegram
7. Сохраняет в базу **только опубликованные** вакансии (не все собранные!)

**Важно: п.7 — намеренное ограничение.** Если сохранять все собранные (включая
без даты), вакансии remote-job.ru без `published_at` навсегда блокировались бы
дедупом когда позже получали дату. База = «уже в канале», не «всё виденное».

---

## Исправленные баги (история)

### 1. Вечная блокировка вакансий без даты (регрессия)
**Файл:** `bot/service.py`  
**Баг:** Ранее сохранялись все собранные вакансии, включая без даты. Новый
дедуп по `title+company` навсегда блокировал их, когда позже появлялась дата.  
**Фикс:** Сохранять только `to_post` (опубликованные), не весь `vacancies`.

### 2. Хрупкий разбор даты в GetMatch
**Файл:** `bot/parsers/getmatch.py`  
**Баг:** `datetime.fromisoformat()` бросал исключение на нестандартном формате →
весь источник падал с потерей всех вакансий.  
**Фикс:** Заменить на `parse_iso_datetime()` из `bot/dates.py` (возвращает `None`).

### 3. Неэкранированный URL в HTML-сообщении
**Файл:** `bot/formatters.py`  
**Баг:** `<a href="{url}">` — `&` в URL ломал Telegram HTML-парсер → сообщение
не отправлялось → прогон падал с ошибкой → вакансии не сохранялись → репост.  
**Фикс:** `escape_html(vacancy.url)` в атрибуте href.

### 4. GitHub Actions пропускал публикацию из-за задержки cron
**Файл:** `bot/run_once.py`, `.github/workflows/daily-vacancies.yml`  
**Баг:** GitHub запускал cron с задержкой до нескольких часов. Код проверял
`hour > 14` → «окно закрыто» → пост терялся.  
**Фикс:** Убрана верхняя граница окна. Добавлен почасовой фолбэк в расписании.
Затем GitHub Actions полностью переведён на ручной запуск после переезда на хостинг.

### 5. TelegramNetworkError не ретраился
**Файл:** `bot/service.py`, метод `_safe_send`  
**Баг:** Ловился только `TelegramRetryAfter`. Таймаут сети падал без повтора.  
**Фикс:** Добавлен retry до 3 раз с паузами 10/20/30 сек на `TelegramNetworkError`.

### 6. Python 3.8 несовместимость
**Файл:** `requirements.txt`, `bot/database.py`, `bot/main.py`, `bot/run_once.py`  
**Баг:** `from zoneinfo import ZoneInfo` — только Python 3.9+. Сервер на 3.8.6.  
**Фикс:** `try/except ImportError` с `backports.zoneinfo`. Добавлен
`backports.zoneinfo; python_version < "3.9"` в requirements.txt.

---

## Известные ограничения

### Remote-job.ru: большинство вакансий без даты
~80 вакансий с remote-job.ru обычно не имеют `published_at` → все отсекаются
фильтром `is_fresh`. Это ожидаемое поведение. Если хочется включать их —
нужно доработать парсер `bot/parsers/remotejob.py` для более точного извлечения
дат из HTML, либо считать вакансии без даты «свежими» (рискованно — можно
получить старьё). Пока не реализовано.

### HH.ru: токен требует периодического обновления
Токен типа `client_credentials` теоретически бессрочный, но HH может его
инвалидировать. При появлении `403` в логах — перевыпустить (см. выше).

---

## Обновление бота на сервере

```bash
cd /var/www/u3452280/data/vacancy-bot
git pull
.venv/bin/pip install -r requirements.txt  # только если менялся requirements.txt
```

## Ручной тестовый запуск на сервере

```bash
cd /var/www/u3452280/data/vacancy-bot && PYTHONIOENCODING=utf-8 .venv/bin/python -m bot.run_once fetch
```

## Проверить состояние базы

```bash
cd /var/www/u3452280/data/vacancy-bot && PYTHONIOENCODING=utf-8 .venv/bin/python -m bot.run_once status
```
