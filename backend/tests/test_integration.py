"""End-to-end smoke test covering ingestion and analytics endpoints."""
from __future__ import annotations

import io

import pandas as pd
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class EndToEndTests(TestCase):
    """Ensure a CSV ingest enables downstream analytics APIs."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_ingest_then_fetch_flow_stats(self) -> None:
        dataframe = pd.DataFrame(
            [
                {
                    "timestamp": "2024-01-01T08:00:00Z",
                    "station": "Central",
                    "line": "Red",
                    "passengers_in": 90,
                    "passengers_out": 70,
                }
            ]
        )
        buffer = io.BytesIO()
        dataframe.to_csv(buffer, index=False)
        buffer.seek(0)
        buffer.name = "ingest.csv"

        response = self.client.post(
            reverse("passenger-record-ingest"),
            {"file": buffer},
            format="multipart",
        )
        self.assertEqual(response.status_code, 200)

        stats_response = self.client.get(reverse("passenger-flow"))
        self.assertEqual(stats_response.status_code, 200)
        self.assertEqual(stats_response.json()[0]["station"], "Central")
