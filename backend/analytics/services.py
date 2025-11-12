"""Analytical utilities for passenger flow insights."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from django.db.models import QuerySet, Sum

from backend.data_management.models import PassengerRecord


@dataclass(slots=True)
class PassengerFlowSummary:
    station: str
    line: str
    total_in: int
    total_out: int


def passenger_flow_by_station(records: QuerySet[PassengerRecord]) -> list[PassengerFlowSummary]:
    aggregates = (
        records.values("station", "line")
        .annotate(total_in=Sum("passengers_in"), total_out=Sum("passengers_out"))
        .order_by("station", "line")
    )
    return [PassengerFlowSummary(**aggregate) for aggregate in aggregates]


def temporal_trend(records: QuerySet[PassengerRecord], freq: str = "H") -> pd.DataFrame:
    data = pd.DataFrame(list(records.values("timestamp", "passengers_in", "passengers_out")))
    if data.empty:
        return pd.DataFrame(columns=["timestamp", "passengers_in", "passengers_out"])
    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True)
    grouped = data.set_index("timestamp").resample(freq).sum().reset_index()
    return grouped


def spatial_distribution(records: QuerySet[PassengerRecord]) -> list[dict[str, object]]:
    aggregates = (
        records.values("station")
        .annotate(total_in=Sum("passengers_in"), total_out=Sum("passengers_out"))
        .order_by("station")
    )
    return [dict(item) for item in aggregates]


def slice_by_timerange(records: QuerySet[PassengerRecord], start: datetime | None, end: datetime | None) -> QuerySet[PassengerRecord]:
    if start:
        records = records.filter(timestamp__gte=start)
    if end:
        records = records.filter(timestamp__lte=end)
    return records
