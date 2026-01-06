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
from analytics import views as analytics_views

router = routers.DefaultRouter()
router.register(r'stations', data_views.StationViewSet)
router.register(r'trains', data_views.TrainViewSet)
router.register(r'routes', data_views.RouteViewSet)
router.register(r'route-stations', data_views.RouteStationViewSet)
router.register(r'passenger-flows', data_views.PassengerFlowViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # 数据管理API
    path('api/data/stats/', data_views.DataStatsView.as_view(), name='data-stats'),
    path('api/data/records/', data_views.DataRecordsView.as_view(), name='data-records'),
    path('api/data/export/', data_views.data_export, name='data-export'),
    path('api/data/upload/', data_views.DataUploadView.as_view(), name='data-upload'),

    # 客流分析API
    path('api/analytics/flow/', data_views.FlowAnalysisView.as_view(), name='flow-analysis'),
    path('api/analytics/kpi/', data_views.AnalyticsKpiView.as_view(), name='analytics-kpi'),
    path('api/analytics/heatmap/', data_views.AnalyticsHeatmapView.as_view(), name='analytics-heatmap'),
    path('api/analytics/trend/', data_views.AnalyticsTrendView.as_view(), name='analytics-trend'),
    path('api/analytics/time-periods/', data_views.AnalyticsTimePeriodsView.as_view(), name='analytics-time-periods'),
    path('api/analytics/time-distribution/', data_views.TimeDistributionView.as_view(), name='time-distribution'),
    path('api/analytics/line-loads/', data_views.AnalyticsLineLoadsView.as_view(), name='analytics-line-loads'),
    path('api/analytics/map/', data_views.AnalyticsMapView.as_view(), name='analytics-map'),
    path('api/analytics/trains/', data_views.AnalyticsTrainsView.as_view(), name='analytics-trains'),
    path('api/analytics/refresh/', data_views.AnalyticsRefreshView.as_view(), name='analytics-refresh'),
    path('api/analytics/export/', data_views.AnalyticsExportView.as_view(), name='analytics-export'),
    path('api/analytics/forecast/', data_views.AnalyticsForecastView.as_view(), name='analytics-forecast'),

    # 站点评估API
    path('api/analytics/stations/', data_views.StationAssessmentView.as_view(), name='station-assessment'),
    path('api/analytics/station-roles/', data_views.StationRoleAnalysisView.as_view(), name='station-role-analysis'),
    path('api/analytics/busy-ranking/', data_views.BusyRankingView.as_view(), name='busy-ranking'),
    # Route optimization APIs
    path('api/lines/', analytics_views.LineListView.as_view(), name='line-list'),
    path('api/lines/<str:line_id>/stations/', analytics_views.LineStationsView.as_view(), name='line-stations'),
    path('api/route-opt/kpi/', analytics_views.RouteOptKpiView.as_view(), name='route-opt-kpi'),
    path('api/route-opt/line-load/heatmap/', analytics_views.LineLoadHeatmapView.as_view(), name='route-opt-line-heatmap'),
    path('api/route-opt/line-load/trend/', analytics_views.LineLoadTrendView.as_view(), name='route-opt-line-trend'),
    path('api/route-opt/density/rank/', analytics_views.DensityRankView.as_view(), name='route-opt-density-rank'),
    path('api/route-opt/section-load/corridor/', analytics_views.SectionLoadCorridorView.as_view(), name='route-opt-section-corridor'),
    path('api/route-opt/trip-load/heatmap/', analytics_views.TripLoadHeatmapView.as_view(), name='route-opt-trip-heatmap'),
    path('api/route-opt/timetable/demand-scatter/', analytics_views.TimetableDemandScatterView.as_view(), name='route-opt-timetable-scatter'),
    path('api/route-opt/suggestions/list/', analytics_views.SuggestionListView.as_view(), name='route-opt-suggestions'),
    path('api/route-opt/suggestions/<str:suggestion_id>/', analytics_views.SuggestionDetailView.as_view(), name='route-opt-suggestion-detail'),
    path('api/route-opt/hubs/metrics/', analytics_views.HubMetricsView.as_view(), name='route-opt-hubs'),
]
