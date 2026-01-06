"""
URL configuration for railway_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from data_management import views as data_views

router = routers.DefaultRouter()
router.register(r'stations', data_views.StationViewSet)
router.register(r'trains', data_views.TrainViewSet)
router.register(r'routes', data_views.RouteViewSet)
router.register(r'route-stations', data_views.RouteStationViewSet)
router.register(r'passenger-flows', data_views.PassengerFlowViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/analytics/flow/', data_views.FlowAnalysisView.as_view(), name='flow-analysis'),
    path('api/analytics/heatmap/', data_views.HeatMapView.as_view(), name='heatmap'),
    path('api/analytics/kpi/', data_views.KpiView.as_view(), name='kpi'),
    path('api/analytics/stations/', data_views.StationAssessmentView.as_view(), name='station-assessment'),
    path('api/analytics/station-roles/', data_views.StationRoleAnalysisView.as_view(), name='station-role-analysis'),
    path('api/analytics/busy-ranking/', data_views.BusyRankingView.as_view(), name='busy-ranking'),
    # 数据管理API
    path('api/data/stats/', data_views.DataStatsView.as_view(), name='data-stats'),
    path('api/data/records/', data_views.DataRecordsView.as_view(), name='data-records'),
]
