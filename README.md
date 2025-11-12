# Railway System Platform

This repository provides a full-stack railway analytics platform composed of a Django backend and a React + Vite frontend.

## Backend (`backend/`)
- Django project with apps for data management, analytics, line optimization, and station evaluation.
- REST APIs under `/api/` for ingestion, passenger flow statistics, temporal/spatial analysis, line load evaluation, optimization recommendations, and station metrics.
- Data ingestion services support CSV/Excel uploads with cleaning, deduplication, and persistence.
- Forecasting utilities (ARIMA) available via `backend/analytics/forecasting.py`.
- Automated tests live in `backend/tests/`.

## Frontend (`frontend/`)
- React + Vite single-page app delivering dashboards, charts, maps, and interactive filters that consume the backend APIs.
- Configure the dev server proxy to point at the backend (`http://localhost:8000`).

## Database Migrations (`db/migrations/`)
- Store infrastructure SQL migrations alongside Django ORM migrations in app directories.

## Getting Started
Refer to `docs/configuration.md` for environment configuration, setup instructions, and validation steps.
