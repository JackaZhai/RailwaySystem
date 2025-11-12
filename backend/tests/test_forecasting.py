"""Tests for forecasting utilities."""
from __future__ import annotations

import pandas as pd
from django.test import SimpleTestCase

from backend.analytics.forecasting import forecast_passenger_flow


class ForecastingTests(SimpleTestCase):
    """Ensure ARIMA forecasting wrapper works."""

    def test_forecast_passenger_flow_returns_expected_length(self) -> None:
        index = pd.date_range("2024-01-01", periods=12, freq="H")
        series = pd.Series(range(12), index=index)
        result = forecast_passenger_flow(series, steps=3)
        self.assertEqual(len(result.forecast), 3)
        self.assertEqual(len(result.timestamps), 3)
