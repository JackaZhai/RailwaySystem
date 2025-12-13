"""Tests for station evaluation services and views."""
from __future__ import annotations

from datetime import datetime, timezone

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from backend.data_management.models import PassengerRecord
from backend.station_evaluation.services import compute_station_metrics


class StationEvaluationServicesTests(TestCase):
    """Test station evaluation business logic."""

    def test_compute_station_metrics_with_empty_data(self) -> None:
        self.assertEqual(compute_station_metrics([]), [])

    def test_compute_station_metrics_with_records(self) -> None:
        records = [
            PassengerRecord(
                timestamp=datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc),
                station="Central",
                line="Red",
                passengers_in=100,
                passengers_out=80,
            ),
            PassengerRecord(
                timestamp=datetime(2024, 1, 1, 9, 5, tzinfo=timezone.utc),
                station="Central",
                line="Red",
                passengers_in=120,
                passengers_out=90,
            ),
        ]
        metrics = compute_station_metrics(records)
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0].station, "Central")
        self.assertEqual(metrics[0].total_passengers, 390)  # 100+80+120+90

    def test_compute_station_metrics_multiple_stations(self) -> None:
        records = [
            PassengerRecord(
                timestamp=datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc),
                station="StationA",
                line="Red",
                passengers_in=50,
                passengers_out=30,
            ),
            PassengerRecord(
                timestamp=datetime(2024, 1, 1, 8, 5, tzinfo=timezone.utc),
                station="StationB",
                line="Blue",
                passengers_in=70,
                passengers_out=40,
            ),
        ]
        metrics = compute_station_metrics(records)
        self.assertEqual(len(metrics), 2)
        stations = {m.station for m in metrics}
        self.assertSetEqual(stations, {"StationA", "StationB"})


class StationEvaluationViewsTests(TestCase):
    """Test station evaluation API endpoints."""

    def setUp(self) -> None:
        self.client = APIClient()
        PassengerRecord.objects.bulk_create(
            [
                PassengerRecord(
                    timestamp=datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc),
                    station="Central",
                    line="Red",
                    passengers_in=100,
                    passengers_out=80,
                ),
            ]
        )

    def test_station_metrics_endpoint(self) -> None:
        response = self.client.get(reverse("station-metrics"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("station", data[0])