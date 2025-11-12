"""Line optimization heuristics and analytics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from backend.data_management.models import PassengerRecord


@dataclass(slots=True)
class LineLoad:
    line: str
    average_load: float
    peak_load: int
    offpeak_load: int


@dataclass(slots=True)
class OptimizationRecommendation:
    line: str
    recommendation: str
    rationale: str


def evaluate_line_loads(records: Iterable[PassengerRecord]) -> list[LineLoad]:
    frame = pd.DataFrame(
        [
            {
                "line": record.line,
                "timestamp": record.timestamp,
                "load": record.passengers_in + record.passengers_out,
            }
            for record in records
        ]
    )
    if frame.empty:
        return []

    frame["hour"] = frame["timestamp"].dt.hour
    peak_hours = frame[frame["hour"].between(7, 9) | frame["hour"].between(16, 19)]
    offpeak_hours = frame.drop(peak_hours.index)

    results: list[LineLoad] = []
    for line, group in frame.groupby("line"):
        peak_load = int(peak_hours[peak_hours["line"] == line]["load"].mean() if not peak_hours.empty else 0)
        offpeak_load = int(offpeak_hours[offpeak_hours["line"] == line]["load"].mean() if not offpeak_hours.empty else 0)
        results.append(
            LineLoad(
                line=line,
                average_load=float(group["load"].mean()),
                peak_load=peak_load,
                offpeak_load=offpeak_load,
            )
        )
    return results


def build_recommendations(loads: list[LineLoad]) -> list[OptimizationRecommendation]:
    recommendations: list[OptimizationRecommendation] = []
    for load in loads:
        if load.peak_load > load.offpeak_load * 1.5:
            recommendation = "Increase train frequency during peak hours"
            rationale = (
                "Peak load exceeds off-peak load by more than 50%. Increase peak service frequency to reduce congestion."
            )
        elif load.average_load < 50:
            recommendation = "Evaluate potential service consolidation"
            rationale = "Low average load suggests opportunities to redeploy rolling stock."
        else:
            recommendation = "Maintain current schedule"
            rationale = "Load distribution is balanced across peak and off-peak periods."

        recommendations.append(
            OptimizationRecommendation(line=load.line, recommendation=recommendation, rationale=rationale)
        )
    return recommendations
