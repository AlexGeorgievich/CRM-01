# Установка и запуск CRM-MiniSystem

## Требования

- Docker Desktop и Docker Compose.
- Node.js 22+ и npm 11+ для локальной разработки frontend.
- Python virtualenv проекта для локальных backend-тестов.
- Свободные порты:
  - `8001` — FastAPI backend;
  - `3002` — Next/static frontend;
  - `5433` — PostgreSQL с хоста.

## Быстрый запуск через Docker

1. Перейдите в каталог backend:

   `cd crm-backend`

2. Проверьте `.env`.

   Для локального стенда можно использовать значения по умолчанию. Для демонстрации
   измените `SECRET_KEY` и `INITIAL_ADMIN_PASSWORD` до первого запуска.

3. Запустите сервисы:

   `docker compose up -d --build`

4. Откройте интерфейс:

   http://localhost:3002

5. Проверьте backend:

   - API: http://localhost:8001
   - Swagger: http://localhost:8001/docs
   - Healthcheck: http://localhost:8001/health

При старте контейнера `app` автоматически применяются миграции Alembic и создаются
начальные справочники.

## Локальный запуск frontend

Frontend находится в `../crm-frontend`.

```bash
cd crm-frontend
npm install
npm run dev
```

Адрес dev-сервера: http://localhost:3002.

Для статического preview:

```bash
npm run build
npm run start
```

Если Next build падает с out-of-memory на Windows, запустите сборку с увеличенным heap:

```powershell
$env:NODE_OPTIONS='--max-old-space-size=4096'; npm run build
```

## Режимы frontend

По умолчанию frontend работает с моковыми данными:

```env
NEXT_PUBLIC_USE_MOCKS=true
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

Для подключения к реальному backend задайте:

```env
NEXT_PUBLIC_USE_MOCKS=false
```

## Стартовый пользователь

Администратор создается из `.env`:

- логин: `admin`
- пароль: значение `INITIAL_ADMIN_PASSWORD`

Для mock-режима также доступны:

- `admin / admin12345`
- `manager / manager12345`

## Проверка работоспособности

- Backend healthcheck: `curl http://localhost:8001/health`
- OpenAPI: http://localhost:8001/docs
- Frontend: http://localhost:3002
- Логи backend: `docker compose logs -f app`
- Логи frontend Docker-сервиса: `docker compose logs -f frontend`

## Остановка

```bash
docker compose down
```

## Сброс данных локального стенда

Команда ниже удалит контейнеры и volumes с данными PostgreSQL/Redis:

```bash
docker compose down -v
```

После повторного запуска миграции и стартовые данные будут созданы заново.
