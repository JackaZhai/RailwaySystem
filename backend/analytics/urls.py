from django.urls import path
from . import views

urlpatterns = [
    path('lines/', views.line_analysis, name='line-analysis'),
]
