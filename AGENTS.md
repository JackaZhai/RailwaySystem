# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: Django REST backend. Core apps include `analytics/` and `data_management/`, with project settings in `railway_backend/` and entrypoint at `manage.py`.
- `frontend/`: Vue 3 + Vite app. Source lives in `frontend/src/`, static assets in `frontend/public/`, build output in `frontend/dist/`.
- `db/`: CSV data files used by the system.
- `docs/`: Project documentation.
- Root scripts: `start_dev.py`, `check_data_distribution.py`, and `check_ranking_api.py` for local workflows and validation.

## Build, Test, and Development Commands
Backend (from repo root):
```bash
python -m venv .venv
pip install -r backend/requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver 0.0.0.0:8080
```
Frontend:
```bash
cd frontend
npm install
npm run dev
```
Both (single command):
```bash
python start_dev.py
```
Quality and build:
```bash
cd frontend
npm run lint       # auto-fix lint
npm run lint:check # check only
npm run type-check
npm run build
npm run preview
```

## Coding Style & Naming Conventions
- Python: 4-space indentation, `snake_case` for modules/functions/vars, `PascalCase` for classes (Django conventions).
- Vue/TypeScript: follow Prettier config (2-space indentation, single quotes, semicolons). Components are `PascalCase.vue` in `frontend/src/components/`.
- Keep API routes under `backend/*/urls.py` and views in `backend/*/views.py`.

## Testing Guidelines
- Backend tests use Django’s test runner and live in each app’s `tests.py`.
```bash
python backend/manage.py test
```
- No dedicated frontend test framework is configured; use `npm run lint:check` and `npm run type-check` for baseline coverage.

## Commit & Pull Request Guidelines
- Commit messages are short and descriptive. History shows Conventional Commit-style prefixes (e.g., `feat:`) and plain summaries; pick one style and keep it consistent.
- PRs should include: a concise description, steps to run/verify, and screenshots for UI changes. Note any data/schema changes clearly.

## Configuration & Secrets
- Frontend envs: copy `frontend/.env.example` to `frontend/.env.development` and set `VITE_*` values (API base URL and map keys).
- Do not commit secrets. The backend defaults to SQLite; keep local DB files under `backend/db/` or your local workspace only.
