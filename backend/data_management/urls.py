"""URL routing for data management."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PassengerRecordViewSet

router = DefaultRouter()
router.register("records", PassengerRecordViewSet, basename="passenger-record")

urlpatterns = [path("", include(router.urls))]
