# API-расширения текущей итерации

## RBAC

Backend использует две роли:

- `admin` — полный доступ.
- `manager` — доступ только к заявкам, назначенным на текущего пользователя.

Ограничения применяются в endpoints заявок:

- список заявок;
- карточка заявки;
- обновление заявки;
- комментарии;
- CSV export;
- сводная аналитика.

Менеджер при создании заявки автоматически назначает ее на себя и не может назначить
заявку другому менеджеру.

## Управление пользователями

Пользовательские административные операции доступны только роли `admin`.

```http
GET /api/v1/users
POST /api/v1/users
PATCH /api/v1/users/{user_id}
POST /api/v1/users/{user_id}/reset-password
```

`PATCH /api/v1/users/{user_id}` поддерживает изменение:

- `full_name`
- `email`
- `role`
- `is_active`

`POST /api/v1/users/{user_id}/reset-password` принимает:

```json
{
  "password": "new-password"
}
```

Заблокированный пользователь не проходит авторизацию.

## Управление справочниками

Создание и изменение справочников доступны только роли `admin`.

```http
POST /api/v1/dictionaries/statuses
PATCH /api/v1/dictionaries/statuses/{status_id}
POST /api/v1/dictionaries/courses
PATCH /api/v1/dictionaries/courses/{course_id}
POST /api/v1/dictionaries/sources
PATCH /api/v1/dictionaries/sources/{source_id}
```

Для архивации используется `is_active=false`. Архивные записи не показываются в рабочих
списках по умолчанию.

## Заявки и просрочки

В модель `Lead` добавлены поля:

```text
next_contact_date: date | null
email: string | null
```

E-mail нормализуется в нижний регистр, проверяется при создании и редактировании и
участвует в общем поиске заявок.

Просрочка считается так:

- `next_contact_date` заполнено;
- дата меньше текущего дня;
- статус заявки не финальный.

Фильтр списка:

```http
GET /api/v1/leads?overdue=true
```

Архивные заявки по умолчанию скрыты. Для включения используется:

```http
GET /api/v1/leads?include_deleted=true
```

## CSV export

```http
GET /api/v1/leads/export.csv
```

Поддерживает те же фильтры, что и список заявок:

- `status_id`
- `course_id`
- `source_id`
- `assigned_manager_id`
- `search`
- `overdue`
- `include_deleted`

Экспорт учитывает роль пользователя. Менеджер выгружает только свои заявки.

## CSV import

```http
POST /api/v1/leads/import.csv
Content-Type: multipart/form-data
```

Поле файла: `file`.

Импорт доступен только администратору.

Поддерживаемые колонки:

- `customer_name`
- `contact`
- `email`
- `status_id`
- `course_id`
- `source_id`
- `assigned_manager_id`
- `notes`
- `next_contact_date`

Ответ содержит количество созданных строк и ошибки по строкам:

```json
{
  "created": 2,
  "errors": [
    {
      "row": 4,
      "errors": {
        "status_id": "Status does not exist or is inactive"
      }
    }
  ]
}
```

## Сводная аналитика

```http
GET /api/v1/reports/summary
```

Возвращает:

- `updated_at`
- `kpi.total`
- `kpi.won`
- `kpi.overdue`
- `kpi.conversion`
- `by_status`
- `by_source`
- `by_course`
- `by_manager`

Endpoint поддерживает общие фильтры заявок и учитывает роль пользователя.

## Миграция

Добавлены ревизии:

```text
20260708_0002_add_next_contact_date.py
20260709_0003_add_lead_email.py
```

Они добавляют колонки `leads.next_contact_date`, `leads.email` и соответствующие
индексы `ix_leads_next_contact_date`, `ix_leads_email`.
