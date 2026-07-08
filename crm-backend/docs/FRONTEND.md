# Frontend: Next.js + Tailwind

## Назначение

Новый frontend находится в `crm-frontend` и заменяет первичный статический интерфейс
backend-приложения. Интерфейс рассчитан на ежедневную работу менеджера и администратора:
таблица заявок, карточка, дашборд, CSV и админские экраны.

## Стек

- Next.js App Router.
- TypeScript.
- Tailwind CSS.
- Recharts для графиков.
- Lucide React для иконок.
- Client-side режим работы с API или моковыми данными.

## Запуск

```bash
cd crm-frontend
npm install
npm run dev
```

Адрес: http://localhost:3002.

Статическая сборка:

```bash
npm run build
npm run start
```

`npm run build` создает каталог `out/`. `npm run start` обслуживает `out/` через
`server-static.mjs` на порту `3002`.

## Конфигурация

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_USE_MOCKS=true
```

- `NEXT_PUBLIC_USE_MOCKS=true` — frontend использует локальные моковые данные.
- `NEXT_PUBLIC_USE_MOCKS=false` — frontend обращается к FastAPI backend.

## Структура

- `src/app` — Next entrypoints и глобальные стили.
- `src/components` — рабочие экраны и UI-компоненты.
- `src/lib/api.ts` — единая точка доступа к mock/API режимам.
- `src/lib/mock-data.ts` — моковые пользователи, заявки и справочники.
- `src/lib/analytics.ts` — расчет frontend-аналитики для mock-режима.
- `src/lib/csv.ts` — экспорт и предпросмотр CSV.
- `src/lib/permissions.ts` — UI-права для ролей.
- `public/sample-leads.csv` — пример файла импорта.

## Реализованные экраны

- `Дашборд` — KPI, funnel, line/bar/pie charts, таблица менеджеров.
- `Заявки` — фильтры, таблица, создание, редактирование, комментарии, архивирование.
- `CSV` — выгрузка и импорт с предпросмотром ошибок.
- `Администрирование` — создание пользователей, блокировка/активация, сброс пароля,
  создание и архивация справочников.

## Принципы UI

- Первый экран после входа — рабочее приложение, не landing page.
- Навигация и действия скрываются по роли.
- Таблица и панели рассчитаны на плотную CRM-работу.
- Просрочки визуально выделяются.
- Графики используют единый набор цветов и читаемые подписи.

## Ограничения текущей реализации

- Редактирование названий уже созданных справочников через UI пока не вынесено в
  отдельную inline-форму; API это поддерживает.
- CSV import в UI использует фиксированные имена колонок.
- В API-режиме frontend использует существующие REST endpoints, без SSR.
- Статический режим подходит для текущего client-side UI; при появлении server actions
  или SSR нужно вернуть полноценный `next start`.
