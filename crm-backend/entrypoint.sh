#!/bin/sh
set -e

# Ожидание PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL started"

# Применение миграций
echo "Running migrations..."
alembic upgrade head

echo "Seeding initial data..."
python -m app.initial_data

# Запуск приложения
echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
