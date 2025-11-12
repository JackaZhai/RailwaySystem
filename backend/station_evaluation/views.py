"""Station evaluation API views."""
from __future__ import annotations

from rest_framework import views
from rest_framework.request import Request
from rest_framework.response import Response

from backend.data_management.models import PassengerRecord

from .services import compute_station_metrics


class StationMetricsView(views.APIView):
    """Return KPI metrics per station."""

    def get(self, request: Request) -> Response:
        records = PassengerRecord.objects.all()
        metrics = compute_station_metrics(records)
        return Response([metric.__dict__ for metric in metrics])
