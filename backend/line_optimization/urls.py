"""URL routing for line optimization endpoints."""
from django.urls import path

from .views import LineLoadView, OptimizationRecommendationView

urlpatterns = [
    path("loads/", LineLoadView.as_view(), name="line-loads"),
    path("recommendations/", OptimizationRecommendationView.as_view(), name="line-recommendations"),
]
