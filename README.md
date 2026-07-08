# CRM-MiniSystem

CRM-MiniSystem — учебно-практический CRM-проект для учета заявок образовательного центра NexusCode. Система помогает менеджерам вести лиды, фиксировать комментарии, контролировать следующие контакты и просрочки, а администратору — управлять пользователями, справочниками, импортом, экспортом и аналитикой.

Проект состоит из двух частей:

- `crm-backend` — FastAPI backend с PostgreSQL, Redis, SQLAlchemy, Alembic, JWT-авторизацией и REST API.
- `crm-frontend` — Next.js + TypeScript + Tailwind frontend с рабочими экранами CRM, моковыми данными, дашбордом и CSV-инструментами.

## Возможности

- Авторизация пользователей и роли `admin` / `manager`.
- CRUD заявок, фильтры, поиск, комментарии и мягкая архивация.
- Ограничение менеджера только своими заявками на уровне API.
- Управление пользователями и справочниками статусов, курсов и источников.
- `next_contact_date`, контроль просроченных заявок и фильтр просрочек.
- Дашборд с KPI, воронкой, источниками, курсами и нагрузкой менеджеров.
- CSV export/import с проверкой данных.
- Mock-режим frontend для быстрой демонстрации без подключения к backend.
- Docker Compose окружение для backend, PostgreSQL, Redis и frontend.

## Быстрый запуск

```bash
cd crm-backend
docker compose up -d --build
```

После запуска:

- Frontend: http://localhost:3002
- Backend API: http://localhost:8001
- Swagger/OpenAPI: http://localhost:8001/docs
- Healthcheck: http://localhost:8001/health

Стартовый пользователь локального стенда:

- логин: `admin`
- пароль: `admin12345`

Для production или демонстрационного стенда пароль и `SECRET_KEY` нужно изменить в `crm-backend/.env` до первого запуска.

## Документация

- [Backend README](crm-backend/README.md) — запуск backend, основные команды, API и структура домена.
- [Frontend README](crm-frontend/README.md) — запуск Next.js frontend, mock/API режимы и экраны интерфейса.
- [Инструкция установки](crm-backend/docs/INSTALL.md) — требования, Docker-запуск, локальный frontend и проверка работоспособности.
- [Руководство пользователя](crm-backend/docs/USER_GUIDE.md) — вход, заявки, комментарии, дашборд, CSV и роли.
- [Frontend: Next.js + Tailwind](crm-backend/docs/FRONTEND.md) — архитектура frontend, структура файлов и ограничения текущей реализации.
- [API-расширения](crm-backend/docs/API_EXTENSIONS.md) — RBAC, просрочки, CSV endpoints, reports API и миграции.
- [Чек-лист приемки](crm-backend/docs/ACCEPTANCE_CHECKLIST.md) — сценарии проверки MVP.
- [Рекомендации по развитию](crm-backend/docs/NEXT_VERSION.md) — что уже реализовано и что вынесено в следующие версии.
- [Расширенные требования](crm-backend/addition.txt) — исходный backlog требований и приоритетов.

## Проверки

Backend:

```bash
cd crm-backend
..\venv\Scripts\python.exe -m pytest
```

Frontend:

```bash
cd crm-frontend
npm install
npm run build
```

Если Next.js build на Windows падает с out-of-memory, используйте:

```powershell
$env:NODE_OPTIONS='--max-old-space-size=4096'; npm run build
```

## Репозиторий

GitHub: https://github.com/AlexGeorgievich/CRM-01
