from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
from rest_framework.response import Response
from rest_framework.views import APIView

DATA_DIR = Path(__file__).resolve().parent.parent / "db"
SUMMARY_FILE = DATA_DIR / "train_passenger_summary.csv"
SEGMENT_FILE = DATA_DIR / "train_segment_detail.csv"
STATION_FILE = DATA_DIR / "train_station_detail.csv"
TRIP_FILE = DATA_DIR / "gaotie_clean_with_tripkey.parquet"
ROUTE_STATIONS_FILE = DATA_DIR / "route_stations.csv"


def _parse_date(value: Any) -> datetime.date | None:
    if pd.isna(value):
        return None
    text = str(int(value)) if isinstance(value, (int, float, np.integer, np.floating)) else str(value)
    try:
        return datetime.strptime(text, "%Y%m%d").date()
    except ValueError:
        try:
            return datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            return None


def _parse_trip_key(value: Any) -> str:
    if pd.isna(value):
        return "0000"
    text = str(int(value)) if isinstance(value, (int, float, np.integer, np.floating)) else str(value)
    return text.zfill(4)


def _trip_key_to_hour(trip_key: str) -> int:
    try:
        return int(trip_key[:2])
    except (TypeError, ValueError):
        return 0


def _normalize_direction(value: Any) -> str:
    if value is None or pd.isna(value):
        return "up"
    text = str(value).strip().lower()
    if text in {"up", "forward", "fwd", "upward", "上行"}:
        return "up"
    if text in {"down", "reverse", "backward", "downward", "下行"}:
        return "down"
    return "up"


def _p95(values: Iterable[float]) -> float:
    series = pd.Series(list(values)).dropna()
    if series.empty:
        return 0.0
    return float(np.percentile(series, 95))


@lru_cache(maxsize=1)
def load_summary() -> pd.DataFrame:
    df = pd.read_csv(SUMMARY_FILE)
    df = df.rename(
        columns={
            "yyxlbm": "line_id",
            "lcbm": "train_id",
            "yxrq": "date",
            "trip_key": "trip_key",
            "方向": "direction",
            "列车定员": "capacity",
            "平均上座率": "avg_load",
            "最大断面满载率": "p95_load",
            "峰值车上人数": "peak_onboard",
            "最拥挤区间": "crowded_segment",
            "平均断面客流": "avg_segment_flow",
            "人公里(PKM)": "pkm",
            "车公里(TKM)": "tkm",
        }
    )
    if "pkm" not in df.columns:
        for col in df.columns:
            if "PKM" in str(col):
                df["pkm"] = pd.to_numeric(df[col], errors="coerce")
                break
    if "tkm" not in df.columns:
        for col in df.columns:
            if "TKM" in str(col):
                df["tkm"] = pd.to_numeric(df[col], errors="coerce")
                break
    df["date"] = df["date"].apply(_parse_date)
    df["trip_key"] = df["trip_key"].apply(_parse_trip_key)
    df["hour"] = df["trip_key"].apply(_trip_key_to_hour)
    df["direction"] = df["direction"].apply(_normalize_direction)
    return df


@lru_cache(maxsize=1)
def load_segments() -> pd.DataFrame:
    df = pd.read_csv(SEGMENT_FILE)
    df = df.rename(
        columns={
            "from": "from_station_id",
            "to": "to_station_id",
            "区间距离": "segment_distance",
            "区间车上人数": "segment_load",
            "yyxlbm": "line_id",
            "lcbm": "train_id",
            "yxrq": "date",
            "trip_key": "trip_key",
            "区间人公里": "segment_pkm",
            "列车定员": "capacity",
            "断面满载率": "full_rate",
        }
    )
    df["date"] = df["date"].apply(_parse_date)
    df["trip_key"] = df["trip_key"].apply(_parse_trip_key)
    return df


@lru_cache(maxsize=1)
def load_route_stations() -> pd.DataFrame:
    df = pd.read_csv(ROUTE_STATIONS_FILE, skiprows=[1])
    df = df.rename(
        columns={
            "yyxlbm": "line_id",
            "yqzdjjl": "segment_distance",
            "ysjl": "cumulative_distance",
        }
    )
    df["segment_distance"] = pd.to_numeric(df.get("segment_distance"), errors="coerce")
    df["cumulative_distance"] = pd.to_numeric(df.get("cumulative_distance"), errors="coerce")
    return df


@lru_cache(maxsize=1)
def load_trips() -> pd.DataFrame:
    df = pd.read_parquet(TRIP_FILE)
    df = df.rename(
        columns={
            "yyxlbm": "line_id",
            "lcbm": "train_id",
            "zdid": "station_id",
            "yxrq": "date",
            "ddsj": "arrive_time",
            "cfsj": "depart_time",
            "skl": "boarded",
            "xkl": "alighted",
            "start_station_name": "start_station_name",
            "end_station_name": "end_station_name",
            "start_id": "start_station_id",
            "dep_time": "dep_time",
            "trip_key": "trip_key",
        }
    )
    df["date"] = df["date"].apply(_parse_date)
    df["trip_key"] = df["trip_key"].apply(_parse_trip_key)
    return df


def _apply_common_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    time_range = filters.get("timeRange") or []
    if len(time_range) == 2:
        start = _parse_date(time_range[0])
        end = _parse_date(time_range[1])
        if start and end:
            df = df[(df["date"] >= start) & (df["date"] <= end)]

    line_ids = filters.get("lineIds") or []
    if line_ids:
        df = df[df["line_id"].astype(str).isin([str(line_id) for line_id in line_ids])]

    direction = filters.get("direction")
    if direction and direction != "all" and "direction" in df.columns:
        df = df[df["direction"] == direction]

    day_type = filters.get("dayType")
    if day_type in {"workday", "weekend"} and "date" in df.columns:
        df = df[df["date"].notna()].copy()
        df["weekday"] = df["date"].apply(lambda value: value.weekday())
        if day_type == "workday":
            df = df[df["weekday"] < 5]
        else:
            df = df[df["weekday"] >= 5]
        df = df.drop(columns=["weekday"])

    return df


def _build_station_sequence(df: pd.DataFrame) -> List[int]:
    edges: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
    in_degree: Dict[int, int] = defaultdict(int)
    out_degree: Dict[int, int] = defaultdict(int)

    for _, row in df.iterrows():
        src = int(row["from_station_id"])
        dst = int(row["to_station_id"])
        edges[src][dst] += 1
        out_degree[src] += 1
        in_degree[dst] += 1

    nodes = set(in_degree.keys()) | set(out_degree.keys())
    if not nodes:
        return []

    start_nodes = [node for node in nodes if in_degree[node] == 0]
    start = min(start_nodes) if start_nodes else min(nodes)

    sequence = [start]
    visited = {start}
    current = start
    while current in edges and edges[current]:
        next_candidates = sorted(edges[current].items(), key=lambda item: (-item[1], item[0]))
        next_node = None
        for candidate, _count in next_candidates:
            if candidate not in visited:
                next_node = candidate
                break
        if next_node is None:
            break
        sequence.append(next_node)
        visited.add(next_node)
        current = next_node

    for node in sorted(nodes):
        if node not in visited:
            sequence.append(node)
    return sequence


def _build_line_list(summary: pd.DataFrame) -> List[Dict[str, Any]]:
    lines = []
    for line_id, group in summary.groupby("line_id"):
        directions = sorted({direction for direction in group["direction"].dropna().unique()})
        if not directions:
            directions = ["up"]
        date_values = group["date"].dropna()
        min_date = date_values.min() if not date_values.empty else None
        max_date = date_values.max() if not date_values.empty else None
        lines.append(
            {
                "id": str(line_id),
                "name": f"Line {line_id}",
                "directions": directions,
                "dateRange": {
                    "minDate": min_date.strftime("%Y-%m-%d") if min_date else None,
                    "maxDate": max_date.strftime("%Y-%m-%d") if max_date else None,
                },
            }
        )
    return sorted(lines, key=lambda item: item["id"])


def _build_line_station_response(line_id: str, direction: str) -> Dict[str, Any]:
    segments = load_segments()
    segments = segments[segments["line_id"].astype(str) == str(line_id)]
    sequence = _build_station_sequence(segments)
    if direction == "down":
        sequence = list(reversed(sequence))
    stations = [{"id": str(station_id), "name": f"Station {station_id}", "seq": idx + 1} for idx, station_id in enumerate(sequence)]
    return {
        "lineId": str(line_id),
        "direction": direction,
        "stations": stations,
    }


def _build_kpi(summary: pd.DataFrame, segments: pd.DataFrame, filters: Dict[str, Any]) -> Dict[str, Any]:
    threshold = filters.get("threshold") or {"overload": 1.0, "idle": 0.35}
    overload_threshold = float(threshold.get("overload", 1.0))
    idle_threshold = float(threshold.get("idle", 0.35))

    summary = summary.dropna(subset=["avg_load", "p95_load"])
    if summary.empty:
        return {
            "overloadLineCount": 0,
            "idleLineCount": 0,
            "topSection": None,
            "peakHours": [],
            "suggestionCount": {"addTrips": 0, "timetable": 0, "hub": 0},
        }

    line_stats = summary.groupby("line_id").agg(
        avg_load=("avg_load", "mean"),
        p95_load=("p95_load", _p95),
    )

    overload_line_count = int((line_stats["p95_load"] > overload_threshold).sum())
    idle_line_count = int((line_stats["avg_load"] < idle_threshold).sum())

    segment_stats = segments.groupby(["line_id", "from_station_id", "to_station_id"]).agg(
        p95_full_rate=("full_rate", _p95),
        avg_full_rate=("full_rate", "mean"),
    )
    top_section = None
    if not segment_stats.empty:
        top_row = segment_stats.sort_values("p95_full_rate", ascending=False).head(1).reset_index().iloc[0]
        top_section = {
            "lineId": str(top_row["line_id"]),
            "direction": filters.get("direction", "up"),
            "fromStationId": str(int(top_row["from_station_id"])),
            "toStationId": str(int(top_row["to_station_id"])),
            "p95FullRate": float(top_row["p95_full_rate"]),
        }

    peak_hour_stats = summary.groupby("hour")["p95_load"].mean().sort_values(ascending=False).head(3)
    peak_hours = [{"hour": int(hour), "value": float(value)} for hour, value in peak_hour_stats.items()]

    suggestions = build_suggestions(summary, segments, filters)
    suggestion_count = {
        "addTrips": sum(1 for item in suggestions if item["type"] == "addTrips"),
        "timetable": sum(1 for item in suggestions if item["type"] == "timetable"),
        "hub": sum(1 for item in suggestions if item["type"] == "hub"),
    }

    return {
        "overloadLineCount": overload_line_count,
        "idleLineCount": idle_line_count,
        "topSection": top_section,
        "peakHours": peak_hours,
        "suggestionCount": suggestion_count,
    }


def _build_line_heatmap(summary: pd.DataFrame, filters: Dict[str, Any]) -> Dict[str, Any]:
    threshold = filters.get("threshold") or {"overload": 1.0}
    overload_threshold = float(threshold.get("overload", 1.0))

    summary = summary.dropna(subset=["avg_load", "p95_load"])
    if summary.empty:
        return {"xAxis": [], "yAxis": [], "points": []}

    grouped = summary.groupby(["line_id", "hour"]).agg(
        avg_load=("avg_load", "mean"),
        p95_load=("p95_load", _p95),
        overload_count=("p95_load", lambda values: int((values > overload_threshold).sum())),
    )

    hours = sorted(summary["hour"].unique())
    lines = sorted(summary["line_id"].unique())
    y_axis = [{"lineId": str(line_id), "name": f"Line {line_id} ({filters.get('direction', 'up')})"} for line_id in lines]

    points = []
    for line_index, line_id in enumerate(lines):
        for hour_index, hour in enumerate(hours):
            if (line_id, hour) not in grouped.index:
                continue
            row = grouped.loc[(line_id, hour)]
            points.append(
                {
                    "x": hour_index,
                    "y": line_index,
                    "avgLoad": float(row["avg_load"]),
                    "p95Load": float(row["p95_load"]),
                    "overMinutes": int(row["overload_count"] * 5),
                }
            )

    x_axis = [f"{hour:02d}:00" for hour in hours]
    return {"xAxis": x_axis, "yAxis": y_axis, "points": points}


def _build_line_trend(summary: pd.DataFrame) -> Dict[str, Any]:
    if summary.empty:
        return {"series": []}

    summary = summary.dropna(subset=["avg_load", "p95_load"])
    grouped = summary.groupby(["line_id", "date"]).agg(
        avg_load=("avg_load", "mean"),
        p95_load=("p95_load", _p95),
    )
    series = []
    for line_id, line_group in grouped.groupby(level=0):
        line_group = line_group.reset_index().sort_values("date")
        points = [
            {
                "t": row["date"].strftime("%Y-%m-%d"),
                "avgLoad": float(row["avg_load"]),
                "p95Load": float(row["p95_load"]),
            }
            for _, row in line_group.iterrows()
        ]
        series.append({"lineId": str(line_id), "direction": "up", "points": points})
    return {"series": series}


def _build_density_rank(segments: pd.DataFrame) -> Dict[str, Any]:
    if segments.empty or "segment_pkm" not in segments.columns or "segment_distance" not in segments.columns:
        return {"items": []}

    segments = segments.copy()
    segments["segment_pkm"] = pd.to_numeric(segments["segment_pkm"], errors="coerce")
    segments["segment_distance"] = pd.to_numeric(segments["segment_distance"], errors="coerce")
    segments = segments.dropna(subset=["segment_pkm", "segment_distance"])
    segments = segments[segments["segment_distance"] > 0]

    grouped = segments.groupby(["from_station_id", "to_station_id"]).agg(
        total_pkm=("segment_pkm", "sum"),
        total_distance=("segment_distance", "sum"),
        line_id=("line_id", "first"),
    )

    items = []
    for (from_station_id, to_station_id), row in grouped.iterrows():
        total_distance = float(row["total_distance"])
        if total_distance <= 0:
            continue
        total_pkm = float(row["total_pkm"])
        density = total_pkm / total_distance
        items.append(
            {
                "fromStationId": str(int(from_station_id)),
                "toStationId": str(int(to_station_id)),
                "lineId": str(row["line_id"]) if pd.notna(row["line_id"]) else "",
                "totalPkm": total_pkm,
                "segmentDistance": total_distance,
                "density": density,
            }
        )

    items = sorted(items, key=lambda item: item["density"], reverse=True)
    return {"items": items}


def _build_section_corridor(summary: pd.DataFrame, segments: pd.DataFrame, filters: Dict[str, Any]) -> Dict[str, Any]:
    if segments.empty:
        return {"lineId": filters.get("lineId"), "direction": filters.get("direction", "up"), "segments": []}

    summary_key = summary[["line_id", "train_id", "date", "trip_key", "hour"]].dropna()
    merged = segments.merge(summary_key, on=["line_id", "train_id", "date", "trip_key"], how="left")

    grouped = merged.groupby(["from_station_id", "to_station_id"]).agg(
        avg_full_rate=("full_rate", "mean"),
        p95_full_rate=("full_rate", _p95),
        flow=("segment_load", "mean"),
        peak_hour=("hour", lambda values: int(pd.Series(values).dropna().mode().iloc[0]) if pd.Series(values).dropna().any() else 0),
    )

    segments_payload = []
    for _, row in grouped.reset_index().iterrows():
        segments_payload.append(
            {
                "fromStationId": str(int(row["from_station_id"])),
                "toStationId": str(int(row["to_station_id"])),
                "avgFullRate": float(row["avg_full_rate"]),
                "p95FullRate": float(row["p95_full_rate"]),
                "peakHour": int(row["peak_hour"]),
                "flow": float(row["flow"]),
                "topOD": [
                    {
                        "oStationId": str(int(row["from_station_id"])),
                        "dStationId": str(int(row["to_station_id"])),
                        "flow": float(row["flow"]),
                    }
                ],
            }
        )

    return {
        "lineId": str(filters.get("lineId")),
        "direction": filters.get("direction", "up"),
        "segments": sorted(segments_payload, key=lambda item: item["p95FullRate"], reverse=True),
    }


def _build_trip_heatmap(summary: pd.DataFrame, segments: pd.DataFrame, filters: Dict[str, Any]) -> Dict[str, Any]:
    if segments.empty or summary.empty:
        return {"trips": [], "segments": [], "cells": []}

    summary_key = summary[["line_id", "train_id", "date", "trip_key"]].dropna()
    merged = segments.merge(summary_key, on=["line_id", "train_id", "date", "trip_key"], how="inner")

    segment_sequence = _build_station_sequence(segments)
    if len(segment_sequence) < 2:
        return {"trips": [], "segments": [], "cells": []}
    segment_index = {(segment_sequence[idx], segment_sequence[idx + 1]): idx for idx in range(len(segment_sequence) - 1)}

    trip_order = summary.drop_duplicates(subset=["trip_key", "train_id"])
    trip_order = trip_order.sort_values("trip_key")

    trips = [
        {
            "tripId": f"{row['line_id']}-{row['train_id']}-{row['trip_key']}",
            "lineId": str(row["line_id"]),
            "trainId": str(row["train_id"]),
            "departTime": row["trip_key"][:2] + ":" + row["trip_key"][2:],
        }
        for _, row in trip_order.iterrows()
    ]

    segments_payload = [
        {"fromStationId": str(segment_sequence[idx]), "toStationId": str(segment_sequence[idx + 1])}
        for idx in range(len(segment_sequence) - 1)
    ]

    cells = []
    for _, row in merged.iterrows():
        key = (int(row["from_station_id"]), int(row["to_station_id"]))
        if key not in segment_index:
            continue
        cells.append(
            {
                "tripId": f"{row['line_id']}-{row['train_id']}-{row['trip_key']}",
                "segIndex": int(segment_index[key]),
                "load": float(row["full_rate"]),
                "flow": float(row["segment_load"]),
            }
        )

    return {"trips": trips, "segments": segments_payload, "cells": cells}


def _build_timetable_scatter(summary: pd.DataFrame) -> Dict[str, Any]:
    if summary.empty:
        return {"points": []}

    grouped = summary.groupby("trip_key").agg(
        avg_load=("avg_load", "mean"),
        p95_load=("p95_load", _p95),
        sample_trips=("trip_key", "count"),
    )
    grouped = grouped.fillna(0)
    points = []
    for _, row in grouped.reset_index().iterrows():
        trip_key = str(row["trip_key"]).zfill(4)
        points.append(
            {
                "departTime": trip_key[:2] + ":" + trip_key[2:],
                "avgLoad": float(row["avg_load"]),
                "p95Load": float(row["p95_load"]),
                "sampleTrips": int(row["sample_trips"]),
            }
        )
    return {"points": sorted(points, key=lambda item: item["departTime"])}


def build_suggestions(summary: pd.DataFrame, segments: pd.DataFrame, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    threshold = filters.get("threshold") or {"overload": 1.0, "idle": 0.35}
    overload_threshold = float(threshold.get("overload", 1.0))
    idle_threshold = float(threshold.get("idle", 0.35))
    suggestions: List[Dict[str, Any]] = []

    if not segments.empty:
        grouped = segments.groupby(["line_id", "from_station_id", "to_station_id"]).agg(
            p95_full_rate=("full_rate", _p95),
        )
        for _, row in grouped.reset_index().iterrows():
            if row["p95_full_rate"] <= overload_threshold:
                continue
            line_id = row["line_id"]
            from_station = row["from_station_id"]
            to_station = row["to_station_id"]
            suggestion_id = f"SG-{line_id}-{from_station}-{to_station}"
            suggestions.append(
                {
                    "id": suggestion_id,
                    "type": "addTrips",
                    "title": f"Line {line_id} {from_station}-{to_station} add trips",
                    "lineId": str(line_id),
                    "direction": filters.get("direction", "up"),
                    "timeWindow": "07:30-08:30",
                    "segment": {"fromStationId": str(int(from_station)), "toStationId": str(int(to_station))},
                    "reason": f"p95 load {row['p95_full_rate']:.2f} over {overload_threshold}",
                    "confidence": "high",
                    "impact": {
                        "p95Before": float(row["p95_full_rate"]),
                        "p95After": max(0.85, float(row["p95_full_rate"]) - 0.15),
                        "overMinutesDropPct": 0.35,
                    },
                    "cost": {"extraTrips": 2, "opCostIndex": 1.1},
                    "status": "pending",
                }
            )

    if not summary.empty:
        low_load = summary.groupby("line_id")["avg_load"].mean().reset_index()
        for _, row in low_load.iterrows():
            if row["avg_load"] >= idle_threshold:
                continue
            suggestion_id = f"SG-{row['line_id']}-TT"
            suggestions.append(
                {
                    "id": suggestion_id,
                    "type": "timetable",
                    "title": f"Line {row['line_id']} adjust timetable",
                    "lineId": str(row["line_id"]),
                    "direction": filters.get("direction", "up"),
                    "timeWindow": "10:00-16:00",
                    "segment": None,
                    "reason": f"avg load {row['avg_load']:.2f} below {idle_threshold}",
                    "confidence": "medium",
                    "impact": {"p95Before": float(row["avg_load"]), "p95After": float(row["avg_load"]) + 0.1, "overMinutesDropPct": 0.1},
                    "cost": {"extraTrips": 0, "opCostIndex": 0.9},
                    "status": "pending",
                }
            )

    hub_ids = _build_hub_ids()
    for station_id in hub_ids[:2]:
        suggestions.append(
            {
                "id": f"SG-HUB-{station_id}",
                "type": "hub",
                "title": f"Station {station_id} hub reinforcement",
                "lineId": "",
                "direction": "all",
                "timeWindow": "all-day",
                "segment": None,
                "reason": "High transfer pressure",
                "confidence": "medium",
                "impact": {"p95Before": 1.05, "p95After": 0.95, "overMinutesDropPct": 0.2},
                "cost": {"extraTrips": 0, "opCostIndex": 1.3},
                "status": "pending",
            }
        )

    return suggestions


def _build_hub_ids() -> List[int]:
    segments = load_segments()
    if segments.empty:
        return []
    counts = segments.groupby("from_station_id").size() + segments.groupby("to_station_id").size()
    counts = counts.fillna(0).sort_values(ascending=False)
    return [int(station_id) for station_id in counts.index[:10]]


def _build_hub_metrics(filters: Dict[str, Any]) -> Dict[str, Any]:
    segments = load_segments()
    trips = load_trips()
    segments = _apply_common_filters(segments, filters)
    trips = _apply_common_filters(trips, filters)

    degree = segments.groupby("from_station_id").size().add(
        segments.groupby("to_station_id").size(), fill_value=0
    )
    flow = trips.groupby("station_id")[["boarded", "alighted"]].sum()
    flow["in_out_flow"] = flow["boarded"].fillna(0) + flow["alighted"].fillna(0)

    nodes = []
    for station_id, deg_value in degree.sort_values(ascending=False).head(30).items():
        station_flow = flow["in_out_flow"].get(station_id, 0.0)
        betweenness = float(deg_value) / float(degree.max() or 1)
        closeness = min(1.0, 0.2 + betweenness)
        nodes.append(
            {
                "stationId": str(int(station_id)),
                "name": f"Station {int(station_id)}",
                "degree": int(deg_value),
                "betweenness": round(betweenness, 4),
                "closeness": round(closeness, 4),
                "inOutFlow": float(station_flow),
                "transferFlow": float(station_flow) * 0.35,
            }
        )

    edges = []
    if not segments.empty:
        edge_stats = segments.groupby(["from_station_id", "to_station_id"])["full_rate"].mean().reset_index()
        max_rate = edge_stats["full_rate"].max() or 1
        for _, row in edge_stats.head(80).iterrows():
            edges.append(
                {
                    "fromStationId": str(int(row["from_station_id"])),
                    "toStationId": str(int(row["to_station_id"])),
                    "weight": float(row["full_rate"]) / max_rate,
                }
            )

    return {"nodes": nodes, "edges": edges}


class LineListView(APIView):
    def get(self, _request):
        summary = load_summary()
        return Response(_build_line_list(summary))


class LineStationsView(APIView):
    def get(self, request, line_id: str):
        direction = request.query_params.get("direction", "up")
        return Response(_build_line_station_response(line_id, direction))


class RouteOptKpiView(APIView):
    def post(self, request):
        filters = request.data or {}
        summary = _apply_common_filters(load_summary(), filters)
        segments = _apply_common_filters(load_segments(), filters)
        return Response(_build_kpi(summary, segments, filters))


class LineLoadHeatmapView(APIView):
    def post(self, request):
        filters = request.data or {}
        summary = _apply_common_filters(load_summary(), filters)
        return Response(_build_line_heatmap(summary, filters))


class LineLoadTrendView(APIView):
    def post(self, request):
        filters = request.data or {}
        summary = _apply_common_filters(load_summary(), filters)
        return Response(_build_line_trend(summary))


class DensityRankView(APIView):
    def post(self, request):
        filters = request.data or {}
        segments = _apply_common_filters(load_segments(), filters)
        return Response(_build_density_rank(segments))


class SectionLoadCorridorView(APIView):
    def post(self, request):
        filters = request.data or {}
        summary = _apply_common_filters(load_summary(), filters)
        segments = _apply_common_filters(load_segments(), filters)
        line_id = filters.get("lineId")
        if line_id:
            segments = segments[segments["line_id"].astype(str) == str(line_id)]
            summary = summary[summary["line_id"].astype(str) == str(line_id)]
        return Response(_build_section_corridor(summary, segments, filters))


class TripLoadHeatmapView(APIView):
    def post(self, request):
        filters = request.data or {}
        summary = _apply_common_filters(load_summary(), filters)
        segments = _apply_common_filters(load_segments(), filters)
        line_id = filters.get("lineId")
        if line_id:
            segments = segments[segments["line_id"].astype(str) == str(line_id)]
            summary = summary[summary["line_id"].astype(str) == str(line_id)]
        return Response(_build_trip_heatmap(summary, segments, filters))


class TimetableDemandScatterView(APIView):
    def post(self, request):
        filters = request.data or {}
        summary = _apply_common_filters(load_summary(), filters)
        line_id = filters.get("lineId")
        if line_id:
            summary = summary[summary["line_id"].astype(str) == str(line_id)]
        return Response(_build_timetable_scatter(summary))


class SuggestionListView(APIView):
    def post(self, request):
        filters = request.data.get("filters") if isinstance(request.data, dict) else {}
        summary = _apply_common_filters(load_summary(), filters or {})
        segments = _apply_common_filters(load_segments(), filters or {})
        items = build_suggestions(summary, segments, filters or {})
        return Response({"total": len(items), "items": items})


class SuggestionDetailView(APIView):
    def get(self, _request, suggestion_id: str):
        summary = load_summary()
        segments = load_segments()
        suggestions = build_suggestions(summary, segments, {})
        for suggestion in suggestions:
            if suggestion["id"] == suggestion_id:
                return Response(
                    {
                        "id": suggestion_id,
                        "evidence": {
                            "lineHeatmapRef": {"lineId": suggestion.get("lineId"), "peakHours": [8]},
                            "corridorTopSegments": suggestion.get("segment") and [
                                {
                                    "fromStationId": suggestion["segment"]["fromStationId"],
                                    "toStationId": suggestion["segment"]["toStationId"],
                                    "p95FullRate": suggestion["impact"]["p95Before"],
                                }
                            ],
                            "topTrips": [],
                        },
                        "action": {
                            "addTrips": {"count": 2, "headwayFromMin": 10, "headwayToMin": 7}
                            if suggestion["type"] == "addTrips"
                            else None,
                            "timetableAdjust": [],
                        },
                        "simulationAssumption": {
                            "splitRule": "even",
                            "note": "assume evenly split demand for new trips",
                        },
                    }
                )
        return Response({"detail": "Not found"}, status=404)


class HubMetricsView(APIView):
    def post(self, request):
        filters = request.data or {}
        return Response(_build_hub_metrics(filters))
