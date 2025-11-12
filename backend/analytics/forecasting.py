"""Forecasting helpers leveraging classical statistical models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


@dataclass(slots=True)
class ForecastResult:
    """Container for forecasted values."""

    timestamps: list[pd.Timestamp]
    forecast: list[float]
    confidence_lower: list[float]
    confidence_upper: list[float]


def fit_arima(series: Sequence[float], order: tuple[int, int, int] = (2, 1, 2)) -> ARIMA:
    """Fit an ARIMA model to the supplied sequence."""
    array = np.asarray(series, dtype=float)
    if array.size < max(order) + 2:
        raise ValueError("Not enough data points to fit ARIMA model")
    return ARIMA(array, order=order).fit()


def forecast_passenger_flow(
    historical: pd.Series, steps: int = 6, order: tuple[int, int, int] = (1, 1, 1)
) -> ForecastResult:
    """Forecast passenger flow using ARIMA with confidence intervals."""
    model = ARIMA(historical.astype(float).values, order=order).fit()
    forecast_res = model.get_forecast(steps=steps)
    freq = historical.index.freq or pd.infer_freq(historical.index) or "H"
    forecast_index = pd.date_range(start=historical.index[-1], periods=steps + 1, freq=freq)[1:]
    conf_int = forecast_res.conf_int(alpha=0.05)
    return ForecastResult(
        timestamps=[pd.Timestamp(ts) for ts in forecast_index],
        forecast=list(forecast_res.predicted_mean),
        confidence_lower=list(conf_int.iloc[:, 0]),
        confidence_upper=list(conf_int.iloc[:, 1]),
    )
