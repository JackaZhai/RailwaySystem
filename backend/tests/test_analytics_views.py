"""Tests for analytics API endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from backend.data_management.models import PassengerRecord


class AnalyticsViewsTests(TestCase):
    """Ensure analytics endpoints return expected payloads."""

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
                PassengerRecord(
                    timestamp=datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc),
                    station="Central",
                    line="Red",
                    passengers_in=120,
                    passengers_out=90,
                ),
            ]
        )

    def test_passenger_flow_endpoint(self) -> None:
        response = self.client.get(reverse("passenger-flow"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["station"], "Central")

    def test_temporal_trend_endpoint(self) -> None:
        response = self.client.get(reverse("temporal-trend"), {"freq": "H"})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_spatial_distribution_endpoint(self) -> None:
        response = self.client.get(reverse("spatial-distribution"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["station"], "Central")
