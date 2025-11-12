"""URL routing for analytics endpoints."""
from django.urls import path

from .views import ForecastView, PassengerFlowStatsView, SpatialDistributionView, TemporalTrendView

urlpatterns = [
    path("flow/", PassengerFlowStatsView.as_view(), name="passenger-flow"),
    path("temporal/", TemporalTrendView.as_view(), name="temporal-trend"),
    path("spatial/", SpatialDistributionView.as_view(), name="spatial-distribution"),
    path("forecast/", ForecastView.as_view(), name="forecast"),
]
