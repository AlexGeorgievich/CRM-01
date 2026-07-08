# CRM Frontend

Next.js + TypeScript + Tailwind UI for the CRM backend.

## Run

```bash
npm install
npm run dev
```

Dev server uses http://localhost:3002.

For static preview:

```bash
npm run build
npm run start
```

By default the UI uses mock data:

```env
NEXT_PUBLIC_USE_MOCKS=true
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

Set `NEXT_PUBLIC_USE_MOCKS=false` to connect to the FastAPI backend.

## Demo accounts

- `admin / admin12345`
- `manager / manager12345`

## Implemented screens

- Dashboard with KPI, funnel, source/course charts and manager workload.
- Leads table with filters, create/edit form, overdue markers and comments.
- CSV export/import preview.
- Admin panel for users and dictionaries.
- Role-based navigation for `admin` and `manager`.

## CSV sample

Use `public/sample-leads.csv` to check import preview, validation and creation flow.
