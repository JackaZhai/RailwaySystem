"""URL routing for station evaluation endpoints."""
from django.urls import path

from .views import StationMetricsView

urlpatterns = [path("metrics/", StationMetricsView.as_view(), name="station-metrics")]
