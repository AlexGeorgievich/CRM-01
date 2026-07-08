# CRM-MiniSystem Backend

Backend MVP CRM-минисистемы для учета заявок учебного центра.

## Стек

- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.x async
- Alembic
- Redis
- Docker Compose

## Запуск разработки

1. Клонировать репозиторий
2. Скопировать `.env.example` в `.env` и заполнить значения для своего окружения
3. Запустить сервисы: `docker-compose up -d --build`
4. Новый Next.js интерфейс доступен по адресу: http://localhost:3002
5. API доступен по адресу: http://localhost:8001
6. Документация API: http://localhost:8001/docs
7. Проверка состояния: http://localhost:8001/health

При старте контейнера `app` автоматически применяются миграции Alembic.

## Команды

- Остановка: `docker-compose down`
- Просмотр логов: `docker-compose logs -f app`
- Просмотр логов frontend: `docker-compose logs -f frontend`
- Создание миграции: `docker-compose exec app alembic revision --autogenerate -m "message"`
- Применение миграций: `docker-compose exec app alembic upgrade head`
- Откат последней миграции: `docker-compose exec app alembic downgrade -1`
- Проверка API: `curl http://localhost:8001/health`
- Подключение к PostgreSQL с хоста: `localhost:5433`
- Запуск тестов локально: `..\venv\Scripts\pytest.exe -q`

Redis доступен только внутри Docker-сети как `redis:6379`; наружу он не публикуется,
чтобы не конфликтовать с локальными сервисами.

## Стартовый пользователь

При запуске после миграций создается администратор из переменных окружения:

- логин: `admin`
- пароль: `admin12345`

Для реального стенда пароль нужно изменить в `.env` до первого запуска.

## Веб-интерфейс

Откройте http://localhost:3002 и войдите под стартовым администратором.

Новый frontend находится в `../crm-frontend` и реализован на Next.js, TypeScript и Tailwind.
По умолчанию он работает на моковых данных; для подключения к API укажите
`NEXT_PUBLIC_USE_MOCKS=false`.

В текущей версии интерфейс позволяет:

- войти в CRM;
- переключаться между дашбордом, заявками, CSV и админским разделом по правам;
- просматривать список заявок;
- фильтровать заявки по статусу, курсу, источнику, ответственному менеджеру и просрочкам;
- искать заявку по имени клиента или контакту;
- создавать заявку;
- редактировать карточку заявки;
- удалять заявку из рабочего списка;
- добавлять комментарии;
- видеть системные комментарии по созданию, изменению и удалению;
- смотреть KPI, воронку, источники, курсы и нагрузку менеджеров;
- экспортировать и импортировать CSV.

## Документация

- [Инструкция установки](docs/INSTALL.md)
- [Руководство пользователя](docs/USER_GUIDE.md)
- [Frontend: Next.js + Tailwind](docs/FRONTEND.md)
- [API-расширения текущей итерации](docs/API_EXTENSIONS.md)
- [Чек-лист приемки MVP](docs/ACCEPTANCE_CHECKLIST.md)
- [Рекомендации по следующей версии](docs/NEXT_VERSION.md)

## Проверки

Тесты покрывают:

- доступность frontend и OpenAPI;
- защиту API без авторизации;
- хэширование паролей и JWT;
- полный жизненный цикл заявки;
- валидацию ссылок на справочники;
- запрет менеджеру создавать пользователей;
- разграничение доступа менеджера только к своим заявкам;
- CSV export и сводную аналитику.

## Основные API

- `POST /api/v1/auth/login` — вход, получение JWT
- `GET /api/v1/auth/me` — текущий пользователь
- `GET /api/v1/leads` — список заявок с фильтрами
- `POST /api/v1/leads` — создание заявки
- `GET /api/v1/leads/export.csv` — экспорт заявок в CSV
- `POST /api/v1/leads/import.csv` — импорт заявок из CSV, только администратор
- `GET /api/v1/leads/{lead_id}` — карточка заявки
- `PATCH /api/v1/leads/{lead_id}` — редактирование заявки
- `DELETE /api/v1/leads/{lead_id}` — мягкое удаление заявки
- `GET /api/v1/leads/{lead_id}/comments` — комментарии заявки
- `POST /api/v1/leads/{lead_id}/comments` — добавить комментарий
- `GET /api/v1/dictionaries/statuses` — статусы
- `GET /api/v1/dictionaries/courses` — курсы
- `GET /api/v1/dictionaries/sources` — источники
- `GET /api/v1/reports/summary` — KPI и базовая аналитика
- `GET /api/v1/users` — пользователи, только администратор

Для отладки SQL-запросов можно временно поставить `SQL_ECHO=True` в `.env`.

Фильтры заявок:

- `status_id`
- `course_id`
- `source_id`
- `assigned_manager_id`
- `overdue`
- `include_deleted`
- `search`
- `skip`
- `limit`

## Быстрая проверка API

1. Получить токен:

   `curl -X POST http://localhost:8001/api/v1/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=admin12345"`

2. В Swagger открыть `Authorize` и вставить токен без префикса `Bearer`.

3. Создать заявку через `POST /api/v1/leads`, используя существующие `status_id`, `course_id`, `source_id`.

## Текущая структура домена

- `users` — пользователи системы: администратор и менеджер
- `leads` — заявки клиентов
- `comments` — комментарии и системные заметки по заявке
- `statuses` — этапы воронки
- `courses` — справочник курсов
- `sources` — справочник источников заявок

## Что принято к исполнению из `addition.txt`

- Next.js + Tailwind frontend вместо слабого статического интерфейса.
- Моковые данные для проверки ролей, заявок, CSV, аналитики и админ-раздела.
- Дашборды: KPI, воронка, источники, курсы, менеджеры и просрочки.
- Роли `admin` и `manager` с ограничением данных менеджера на уровне API.
- CSV export/import.
- Поле `next_contact_date` и фильтр просрочек.

## Что принято к сведению для следующих этапов

- Полноценная матрица permissions вместо двух ролей.
- Аудит изменения ролей и всех бизнес-полей отдельной таблицей.
- Excel/PDF export отчетов.
- Drill-down из графиков в сохраненные выборки.
- Интеграции телефонии и почты.
