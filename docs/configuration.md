# Deployment & Configuration Guide

## Environment Variables
- `DJANGO_SECRET_KEY`: Secret key for Django.
- `DJANGO_DEBUG`: Enable debug mode (`true`/`false`).
- `DJANGO_ALLOWED_HOSTS`: Comma-separated hostnames.
- `DJANGO_DB_ENGINE`, `DJANGO_DB_NAME`, `DJANGO_DB_USER`, `DJANGO_DB_PASSWORD`, `DJANGO_DB_HOST`, `DJANGO_DB_PORT`: Database connection configuration.

## Initial Setup
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. Apply migrations:
   ```bash
   python backend/manage.py migrate
   ```
3. Load seed data (optional):
   ```bash
   python backend/manage.py shell -c "from backend.data_management.services import load_sample_data; load_sample_data()"
   ```
4. Run the development server:
   ```bash
   python backend/manage.py runserver 0.0.0.0:8000
   ```

## Running Tests
```bash
python backend/manage.py test
```

## Integration Validation
1. Upload a CSV via `POST /api/data/records/ingest/`.
2. Verify analytics via `GET /api/analytics/flow/` and other endpoints.
3. Consume optimization and station metrics endpoints to confirm successful ingestion.

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The Vite dev server proxies API requests to `http://localhost:8000` by default.
