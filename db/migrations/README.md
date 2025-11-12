# Database Migrations

This directory stores SQL migration scripts for infrastructure environments. The Django ORM
migrations for development live within the respective Django apps (for example
`backend/data_management/migrations/`). Operators can place vendor-specific migrations here to
support managed database services.
