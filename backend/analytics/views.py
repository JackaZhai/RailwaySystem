"""Analytics API views."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
from django.utils.dateparse import parse_datetime
from rest_framework import status, views
from rest_framework.request import Request
from rest_framework.response import Response

from backend.data_management.models import PassengerRecord

from .forecasting import forecast_passenger_flow
from .services import passenger_flow_by_station, slice_by_timerange, spatial_distribution, temporal_trend


class PassengerFlowStatsView(views.APIView):
    """Aggregate passenger flow statistics per station/line."""

    def get(self, request: Request) -> Response:
        queryset = PassengerRecord.objects.all()
        start = parse_datetime(request.query_params.get("start")) if request.query_params.get("start") else None
        end = parse_datetime(request.query_params.get("end")) if request.query_params.get("end") else None
        queryset = slice_by_timerange(queryset, start, end)
        summaries = passenger_flow_by_station(queryset)
        data = [summary.__dict__ for summary in summaries]
        return Response(data)


class TemporalTrendView(views.APIView):
    """Passenger totals aggregated by a temporal frequency."""

    def get(self, request: Request) -> Response:
        freq = request.query_params.get("freq", "H")
        queryset = PassengerRecord.objects.all()
        start = parse_datetime(request.query_params.get("start")) if request.query_params.get("start") else None
        end = parse_datetime(request.query_params.get("end")) if request.query_params.get("end") else None
        queryset = slice_by_timerange(queryset, start, end)
        frame = temporal_trend(queryset, freq=freq)
        records = frame.to_dict(orient="records")
        for row in records:
            if row.get("timestamp") is not None:
                row["timestamp"] = pd.Timestamp(row["timestamp"]).isoformat()
        return Response(records)


class SpatialDistributionView(views.APIView):
    """Passenger totals grouped by station for mapping use cases."""

    def get(self, request: Request) -> Response:
        queryset = PassengerRecord.objects.all()
        start = parse_datetime(request.query_params.get("start")) if request.query_params.get("start") else None
        end = parse_datetime(request.query_params.get("end")) if request.query_params.get("end") else None
        queryset = slice_by_timerange(queryset, start, end)
        return Response(spatial_distribution(queryset))


class ForecastView(views.APIView):
    """Generate ARIMA forecasts for passenger flow."""

    def get(self, request: Request) -> Response:
        station = request.query_params.get("station")
        line = request.query_params.get("line")
        freq = request.query_params.get("freq", "H")
        steps = int(request.query_params.get("steps", 6))

        if not station or not line:
            return Response({"detail": "station and line parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

        records = PassengerRecord.objects.filter(station=station, line=line).order_by("timestamp")
        if not records.exists():
            return Response({"detail": "No records found"}, status=status.HTTP_404_NOT_FOUND)

        frame = pd.DataFrame(list(records.values("timestamp", "passengers_in")))
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        series = frame.set_index("timestamp").resample(freq).sum()["passengers_in"]
        series = series[series.notnull()]
        if len(series) < 5:
            return Response({"detail": "Insufficient data to train forecast"}, status=status.HTTP_400_BAD_REQUEST)

        result = forecast_passenger_flow(series, steps=steps)
        return Response(
            {
                "timestamps": [ts.isoformat() for ts in result.timestamps],
                "forecast": result.forecast,
                "confidence_lower": result.confidence_lower,
                "confidence_upper": result.confidence_upper,
            }
        )
