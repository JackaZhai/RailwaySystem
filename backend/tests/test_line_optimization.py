"""Tests for line optimization services."""
from __future__ import annotations

from datetime import datetime, timezone

from django.test import TestCase

from backend.data_management.models import PassengerRecord
from backend.line_optimization.services import build_recommendations, evaluate_line_loads


class LineOptimizationTests(TestCase):
    """Validate load evaluation and recommendations."""

    def setUp(self) -> None:
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
                    timestamp=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
                    station="Central",
                    line="Red",
                    passengers_in=40,
                    passengers_out=35,
                ),
            ]
        )

    def test_load_evaluation(self) -> None:
        loads = evaluate_line_loads(PassengerRecord.objects.all())
        self.assertEqual(loads[0].line, "Red")

    def test_recommendations(self) -> None:
        loads = evaluate_line_loads(PassengerRecord.objects.all())
        recommendations = build_recommendations(loads)
        self.assertEqual(recommendations[0].line, "Red")
        self.assertTrue(len(recommendations[0].recommendation) > 0)
