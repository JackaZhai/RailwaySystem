"""Tests for station evaluation services."""
from __future__ import annotations

from datetime import datetime, timezone

from django.test import TestCase

from backend.data_management.models import PassengerRecord
from backend.station_evaluation.services import compute_station_metrics


class StationEvaluationTests(TestCase):
    """Ensure station metrics calculations behave as expected."""

    def setUp(self) -> None:
        PassengerRecord.objects.bulk_create(
            [
                PassengerRecord(
                    timestamp=datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc),
                    station="Central",
                    line="Red",
                    passengers_in=50,
                    passengers_out=40,
                ),
                PassengerRecord(
                    timestamp=datetime(2024, 1, 1, 8, 10, tzinfo=timezone.utc),
                    station="Central",
                    line="Red",
                    passengers_in=60,
                    passengers_out=55,
                ),
            ]
        )

    def test_metrics_include_station_totals(self) -> None:
        metrics = compute_station_metrics(PassengerRecord.objects.all())
        self.assertEqual(metrics[0].station, "Central")
        self.assertGreater(metrics[0].total_passengers, 0)
