"""Tests for data ingestion services."""
from __future__ import annotations

import pandas as pd
from django.test import TestCase

from backend.data_management.models import PassengerRecord
from backend.data_management.services import DataIngestionService


class DataIngestionServiceTests(TestCase):
    """Validate ingestion logic for CSV/Excel files."""

    def test_import_dataframe_normalizes_and_persists(self) -> None:
        dataframe = pd.DataFrame(
            [
                {
                    "Timestamp": "2024-01-01T08:00:00Z",
                    "Station": "Central ",
                    "Line": "Red",
                    "Passengers_In": 100,
                    "Passengers_Out": 75,
                },
                {
                    "Timestamp": "2024-01-01T08:00:00Z",
                    "Station": "Central",
                    "Line": "Red",
                    "Passengers_In": 100,
                    "Passengers_Out": 75,
                },
            ]
        )

        service = DataIngestionService(chunk_size=100)
        report = service._import_dataframe(dataframe)

        self.assertEqual(report.total_rows, 1)
        self.assertEqual(PassengerRecord.objects.count(), 1)

    def test_missing_columns_raise_error(self) -> None:
        dataframe = pd.DataFrame([{"station": "Central"}])
        service = DataIngestionService()
        with self.assertRaises(ValueError):
            service._import_dataframe(dataframe)
