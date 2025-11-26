"""Pytest configuration for initializing Django environment."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import django

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_configure() -> None:
    """Ensure Django settings are available before test collection."""
    os.environ.setdefault("DJANGO_DB_NAME", ":memory:")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "railway_backend.settings")
    django.setup()
    from django.core.management import call_command

    call_command("migrate", verbosity=0, run_syncdb=True)
