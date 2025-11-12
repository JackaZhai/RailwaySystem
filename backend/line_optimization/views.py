"""Line optimization API endpoints."""
from __future__ import annotations

from rest_framework import views
from rest_framework.request import Request
from rest_framework.response import Response

from backend.data_management.models import PassengerRecord

from .services import build_recommendations, evaluate_line_loads


class LineLoadView(views.APIView):
    """Return load metrics per line."""

    def get(self, request: Request) -> Response:
        records = PassengerRecord.objects.all()
        loads = evaluate_line_loads(records)
        return Response([load.__dict__ for load in loads])


class OptimizationRecommendationView(views.APIView):
    """Return optimization recommendations for lines."""

    def get(self, request: Request) -> Response:
        records = PassengerRecord.objects.all()
        loads = evaluate_line_loads(records)
        recommendations = build_recommendations(loads)
        return Response([rec.__dict__ for rec in recommendations])
