"""Station evaluation KPIs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from backend.data_management.models import PassengerRecord


@dataclass(slots=True)
class StationMetric:
    station: str
    total_passengers: int
    average_headway: float
    peak_hour: int | None


def compute_station_metrics(records: Iterable[PassengerRecord]) -> list[StationMetric]:
    frame = pd.DataFrame(
        [
            {
                "station": record.station,
                "timestamp": record.timestamp,
                "passengers": record.passengers_in + record.passengers_out,
            }
            for record in records
        ]
    )
    if frame.empty:
        return []

    frame.sort_values("timestamp", inplace=True)
    results: list[StationMetric] = []
    for station, group in frame.groupby("station"):
        total = int(group["passengers"].sum())
        diffs = group["timestamp"].sort_values().diff().dt.total_seconds().dropna()
        average_headway = float(diffs.mean() / 60.0) if not diffs.empty else 0.0
        hourly = group.copy()
        hourly["hour"] = hourly["timestamp"].dt.hour
        peak_hour = int(hourly.groupby("hour")["passengers"].sum().idxmax()) if not hourly.empty else None
        results.append(
            StationMetric(
                station=station,
                total_passengers=total,
                average_headway=average_headway,
                peak_hour=peak_hour,
            )
        )
    return results
