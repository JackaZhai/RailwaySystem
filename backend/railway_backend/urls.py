"""Root URL configuration for the RailwaySystem backend."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/data/", include("backend.data_management.urls")),
    path("api/analytics/", include("backend.analytics.urls")),
    path("api/lines/", include("backend.line_optimization.urls")),
    path("api/stations/", include("backend.station_evaluation.urls")),
]
