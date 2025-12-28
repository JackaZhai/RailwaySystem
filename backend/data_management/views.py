from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg, F, Q, Min, Max
from django.db.models.functions import (
    Trunc,
    TruncDay,
    TruncWeek,
    TruncMonth,
    TruncYear,
    ExtractHour,
    ExtractIsoWeekDay,
    ExtractQuarter,
    ExtractYear,
    Coalesce,
)
from django.http import HttpResponse
from django.utils import timezone
import json
import pandas as pd
import math
from datetime import datetime, timedelta, date

from .models import Station, Train, Route, RouteStation, PassengerFlow
from .serializers import (
    StationSerializer, TrainSerializer, RouteSerializer,
    RouteStationSerializer, PassengerFlowSerializer,
    PassengerFlowSummarySerializer, StationRankingSerializer,
    TimeDistributionSerializer, FlowAnalysisRequestSerializer
)


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    return None


def _get_date_range(request):
    data = request.query_params if request.method == 'GET' else request.data
    start_value = data.get('start_date') or data.get('startDate')
    end_value = data.get('end_date') or data.get('endDate')
    start_date = _parse_date(start_value)
    end_date = _parse_date(end_value)

    if not start_date or not end_date:
        # 尝试使用数据库中最新的数据日期
        last_record = PassengerFlow.objects.order_by('-operation_date').first()
        if last_record:
            end_date = last_record.operation_date
        else:
            end_date = timezone.localdate()

        range_type = data.get('range_type') or data.get('rangeType') or 'month'
        
        if range_type == 'today':
            start_date = end_date
        elif range_type == 'week':
            start_date = end_date - timedelta(days=6)
        elif range_type == 'month':
            start_date = end_date - timedelta(days=29)
        elif range_type == 'quarter':
            start_date = end_date - timedelta(days=89)
        elif range_type == 'year':
            start_date = end_date - timedelta(days=364)
        else:
            start_date = end_date - timedelta(days=29)
            
    # print(f"DEBUG: Date range calculated: {start_date} to {end_date}")

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    return start_date, end_date


def _normalize_int_list(value):
    if value is None:
        return []

    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed:
            return []
        if trimmed.startswith('[') and trimmed.endswith(']'):
            try:
                value = json.loads(trimmed)
            except json.JSONDecodeError:
                value = trimmed.strip('[]').split(',')
        else:
            value = trimmed.split(',')

    if not isinstance(value, (list, tuple)):
        value = [value]

    result = []
    for item in value:
        if item in (None, ''):
            continue
        try:
            result.append(int(item))
        except (TypeError, ValueError):
            continue
    return result


def _get_list_param(request, names):
    if request.method == 'GET':
        for name in names:
            values = request.query_params.getlist(name)
            if values:
                return _normalize_int_list(values)

    data = request.data
    for name in names:
        if name in data:
            return _normalize_int_list(data.get(name))
    return []


def _format_time_period(value, granularity):
    if value is None:
        return None
    if granularity == 'hour':
        return f'{int(value):02d}:00'
    if granularity == 'day':
        return value.strftime('%Y-%m-%d')
    if granularity == 'week':
        year, week, _ = value.isocalendar()
        return f'{year}-W{week:02d}'
    if granularity == 'month':
        return value.strftime('%Y-%m')
    if granularity == 'year':
        return value.strftime('%Y')
    return str(value)


def _apply_flow_filters(queryset, station_ids=None, route_ids=None, train_ids=None):
    if station_ids:
        queryset = queryset.filter(station_id__in=station_ids)
    if route_ids:
        queryset = queryset.filter(route_id__in=route_ids)
    if train_ids:
        queryset = queryset.filter(train_id__in=train_ids)
    return queryset


def _aggregate_flow_totals(queryset):
    totals = queryset.aggregate(
        total_passengers=Sum(F('passengers_in') + F('passengers_out')),
        total_revenue=Sum('revenue'),
        train_count=Count('train', distinct=True),
        station_count=Count('station', distinct=True)
    )

    return {
        'total_passengers': int(totals['total_passengers'] or 0),
        'total_revenue': float(totals['total_revenue'] or 0),
        'train_count': totals['train_count'] or 0,
        'station_count': totals['station_count'] or 0,
    }


def _calc_trend_value(current, previous):
    if not previous:
        return 0
    return round(((current - previous) / previous) * 100, 2)



class StationViewSet(viewsets.ModelViewSet):
    """站点视图集"""
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['travel_area_id', 'code']
    search_fields = ['name', 'telecode', 'shortname']
    ordering_fields = ['id', 'name', 'code']
    ordering = ['id']

    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索站点"""
        query = request.query_params.get('q', '')
        if query:
            stations = Station.objects.filter(
                Q(name__icontains=query) |
                Q(telecode__icontains=query) |
                Q(shortname__icontains=query)
            )[:50]
            serializer = self.get_serializer(stations, many=True)
            return Response(serializer.data)
        return Response([])


class TrainViewSet(viewsets.ModelViewSet):
    """列车视图集"""
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['capacity']
    search_fields = ['code']
    ordering_fields = ['id', 'code', 'capacity']
    ordering = ['id']


class RouteViewSet(viewsets.ModelViewSet):
    """线路视图集"""
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name']
    ordering_fields = ['id', 'code']
    ordering = ['id']

    @action(detail=True, methods=['get'])
    def stations(self, request, pk=None):
        """获取线路的所有站点"""
        route = self.get_object()
        route_stations = RouteStation.objects.filter(route=route).order_by('sequence')
        serializer = RouteStationSerializer(route_stations, many=True)
        return Response(serializer.data)


class RouteStationViewSet(viewsets.ModelViewSet):
    """线路站点视图集"""
    queryset = RouteStation.objects.all()
    serializer_class = RouteStationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['route', 'station', 'is_start', 'is_end', 'must_stop']
    ordering_fields = ['route', 'sequence']
    ordering = ['route', 'sequence']


class PassengerFlowViewSet(viewsets.ModelViewSet):
    """客运记录视图集"""
    queryset = PassengerFlow.objects.all()
    serializer_class = PassengerFlowSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['route', 'train', 'station', 'operation_date']
    ordering_fields = ['operation_date', 'route', 'train', 'station']
    ordering = ['-operation_date', 'route', 'train', 'station']

    def get_queryset(self):
        """根据查询参数过滤查询集"""
        queryset = super().get_queryset()

        # 日期范围过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                operation_date__range=[start_date, end_date]
            )

        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取客运记录汇总"""
        queryset = self.filter_queryset(self.get_queryset())

        # 按日期分组汇总
        summary_data = queryset.values('operation_date').annotate(
            total_passengers=Sum(F('passengers_in') + F('passengers_out')),
            total_revenue=Sum('revenue'),
            train_count=Count('train', distinct=True),
            station_count=Count('station', distinct=True)
        ).annotate(
            avg_passengers_per_train=F('total_passengers') / F('train_count')
        ).order_by('operation_date')

        serializer = PassengerFlowSummarySerializer(summary_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def station_ranking(self, request):
        """获取站点客流排名"""
        queryset = self.filter_queryset(self.get_queryset())

        # 按站点分组汇总
        station_stats = queryset.values(
            'station__id', 'station__name', 'station__telecode'
        ).annotate(
            total_passengers=Sum(F('passengers_in') + F('passengers_out')),
            passengers_in=Sum('passengers_in'),
            passengers_out=Sum('passengers_out'),
            total_revenue=Sum('revenue')
        ).order_by('-total_passengers')

        # 添加排名
        ranked_data = []
        for i, stat in enumerate(station_stats, 1):
            ranked_data.append({
                'station_id': stat['station__id'],
                'station_name': stat['station__name'],
                'station_telecode': stat['station__telecode'],
                'total_passengers': stat['total_passengers'] or 0,
                'passengers_in': stat['passengers_in'] or 0,
                'passengers_out': stat['passengers_out'] or 0,
                'total_revenue': stat['total_revenue'] or 0,
                'ranking': i
            })

        serializer = StationRankingSerializer(ranked_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def time_distribution(self, request):
        """获取时间分布（按小时）"""
        queryset = self.filter_queryset(self.get_queryset())

        # 按小时分组
        hourly_stats = []
        for hour in range(24):
            hour_queryset = queryset.filter(
                arrival_time__hour=hour
            ).aggregate(
                total_passengers=Sum(F('passengers_in') + F('passengers_out')),
                passengers_in=Sum('passengers_in'),
                passengers_out=Sum('passengers_out'),
                record_count=Count('id')
            )

            total_passengers = hour_queryset['total_passengers'] or 0
            avg_passengers = total_passengers / (hour_queryset['record_count'] or 1)

            hourly_stats.append({
                'hour': hour,
                'total_passengers': total_passengers,
                'passengers_in': hour_queryset['passengers_in'] or 0,
                'passengers_out': hour_queryset['passengers_out'] or 0,
                'avg_passengers': avg_passengers,
                'percentage': 0  # 将在后面计算
            })

        # 计算百分比
        total = sum(stat['total_passengers'] for stat in hourly_stats)
        if total > 0:
            for stat in hourly_stats:
                stat['percentage'] = (stat['total_passengers'] / total) * 100

        serializer = TimeDistributionSerializer(hourly_stats, many=True)
        return Response(serializer.data)


class FlowAnalysisView(APIView):
    """客流分析视图"""

    def get(self, request):
        """获取客流流向数据"""
        start_date, end_date = _get_date_range(request)
        station_ids = _get_list_param(request, ['station_ids', 'stationIds', 'stationIds[]'])
        route_ids = _get_list_param(request, ['route_ids', 'routeIds', 'line_ids', 'lineIds', 'lineIds[]'])
        train_ids = _get_list_param(request, ['train_ids', 'trainIds', 'trainIds[]'])

        queryset = PassengerFlow.objects.filter(
            operation_date__range=[start_date, end_date]
        )
        queryset = _apply_flow_filters(queryset, station_ids, route_ids, train_ids)

        flow_pairs = queryset.exclude(
            start_station_telecode__isnull=True
        ).exclude(
            end_station_telecode__isnull=True
        ).values(
            'start_station_telecode', 'end_station_telecode'
        ).annotate(
            total_passengers=Sum(F('passengers_in') + F('passengers_out'))
        ).order_by('-total_passengers')[:500]

        telecodes = set()
        for pair in flow_pairs:
            telecodes.add(pair['start_station_telecode'])
            telecodes.add(pair['end_station_telecode'])

        stations = Station.objects.filter(telecode__in=telecodes)
        station_id_by_telecode = {
            station.telecode: station.id
            for station in stations
        }
        station_name_by_telecode = {
            station.telecode: station.name
            for station in stations
        }

        max_total = max([pair['total_passengers'] or 0 for pair in flow_pairs], default=0)

        def intensity_label(value):
            if max_total <= 0:
                return 'low'
            ratio = value / max_total
            if ratio >= 0.66:
                return 'high'
            if ratio >= 0.33:
                return 'medium'
            return 'low'

        flows = []
        for pair in flow_pairs:
            from_telecode = pair['start_station_telecode']
            to_telecode = pair['end_station_telecode']
            from_id = station_id_by_telecode.get(from_telecode)
            to_id = station_id_by_telecode.get(to_telecode)
            if not from_id or not to_id:
                continue
            passenger_count = pair['total_passengers'] or 0
            flows.append({
                'fromStationId': from_id,
                'toStationId': to_id,
                'fromStationName': station_name_by_telecode.get(from_telecode),
                'toStationName': station_name_by_telecode.get(to_telecode),
                'passengerCount': passenger_count,
                'intensity': intensity_label(passenger_count)
            })

        return Response(flows)

    def post(self, request):
        """执行客流分析"""
        start_date, end_date = _get_date_range(request)
        station_ids = _get_list_param(request, ['station_ids', 'stationIds', 'stationIds[]'])
        route_ids = _get_list_param(request, ['route_ids', 'routeIds', 'line_ids', 'lineIds', 'lineIds[]'])
        train_ids = _get_list_param(request, ['train_ids', 'trainIds', 'trainIds[]'])
        time_granularity = (
            request.data.get('time_granularity')
            or request.data.get('timeGranularity')
            or 'day'
        )

        serializer = FlowAnalysisRequestSerializer(data={
            'start_date': start_date,
            'end_date': end_date,
            'station_ids': station_ids,
            'route_ids': route_ids,
            'train_ids': train_ids,
            'time_granularity': time_granularity
        })
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        start_date = data['start_date']
        end_date = data['end_date']
        station_ids = data.get('station_ids', [])
        route_ids = data.get('route_ids', [])
        train_ids = data.get('train_ids', [])
        time_granularity = data['time_granularity']

        # 构建查询
        queryset = PassengerFlow.objects.filter(
            operation_date__range=[start_date, end_date]
        )

        queryset = _apply_flow_filters(queryset, station_ids, route_ids, train_ids)

        # 根据时间粒度分组
        if time_granularity == 'hour':
            # 按小时分组
            queryset = queryset.annotate(
                time_period=ExtractHour(Coalesce('arrival_time', 'departure_time'))
            ).exclude(time_period__isnull=True)
            group_fields = ['time_period']
        elif time_granularity == 'day':
            queryset = queryset.annotate(
                time_period=TruncDay('operation_date')
            )
            group_fields = ['time_period']
        elif time_granularity == 'week':
            queryset = queryset.annotate(
                time_period=TruncWeek('operation_date')
            )
            group_fields = ['time_period']
        elif time_granularity == 'month':
            queryset = queryset.annotate(
                time_period=TruncMonth('operation_date')
            )
            group_fields = ['time_period']
        elif time_granularity == 'quarter':
            queryset = queryset.annotate(
                year=ExtractYear('operation_date'),
                quarter=ExtractQuarter('operation_date')
            )
            group_fields = ['year', 'quarter']
        else:  # year
            queryset = queryset.annotate(
                time_period=TruncYear('operation_date')
            )
            group_fields = ['time_period']

        # 执行聚合
        results = queryset.values(*group_fields).annotate(
            total_passengers=Sum(F('passengers_in') + F('passengers_out')),
            passengers_in=Sum('passengers_in'),
            passengers_out=Sum('passengers_out'),
            total_revenue=Sum('revenue'),
            train_count=Count('train', distinct=True),
            station_count=Count('station', distinct=True)
        )

        if time_granularity == 'quarter':
            results = results.order_by('year', 'quarter')
        else:
            results = results.order_by('time_period')

        # 格式化结果
        formatted_results = []
        for result in results:
            if time_granularity == 'quarter':
                time_period = f"{result['year']}-Q{result['quarter']}"
            else:
                time_period = _format_time_period(result.get('time_period'), time_granularity)

            formatted_results.append({
                'time_period': time_period,
                'total_passengers': result['total_passengers'] or 0,
                'passengers_in': result['passengers_in'] or 0,
                'passengers_out': result['passengers_out'] or 0,
                'total_revenue': float(result['total_revenue'] or 0),
                'train_count': result['train_count'],
                'station_count': result['station_count'],
                'avg_passengers_per_train': (result['total_passengers'] or 0) / (result['train_count'] or 1)
            })

        return Response({
            'success': True,
            'data': formatted_results,
            'summary': {
                'total_records': queryset.count(),
                'time_periods': len(formatted_results),
                'time_granularity': time_granularity
            }
        })


class AnalyticsKpiView(APIView):
    """客流分析KPI视图"""

    def get(self, request):
        start_date, end_date = _get_date_range(request)
        station_ids = _get_list_param(request, ['station_ids', 'stationIds', 'stationIds[]'])
        route_ids = _get_list_param(request, ['route_ids', 'routeIds', 'line_ids', 'lineIds', 'lineIds[]'])
        train_ids = _get_list_param(request, ['train_ids', 'trainIds', 'trainIds[]'])

        queryset = PassengerFlow.objects.filter(operation_date__range=[start_date, end_date])
        queryset = _apply_flow_filters(queryset, station_ids, route_ids, train_ids)
        current = _aggregate_flow_totals(queryset)

        delta_days = (end_date - start_date).days + 1
        prev_start = start_date - timedelta(days=delta_days)
        prev_end = start_date - timedelta(days=1)
        prev_queryset = PassengerFlow.objects.filter(operation_date__range=[prev_start, prev_end])
        prev_queryset = _apply_flow_filters(prev_queryset, station_ids, route_ids, train_ids)
        previous = _aggregate_flow_totals(prev_queryset)

        return Response({
            'totalPassengers': current['total_passengers'],
            'totalTrains': current['train_count'],
            'busyStations': current['station_count'],
            'totalRevenue': current['total_revenue'],
            'trends': {
                'totalPassengers': _calc_trend_value(current['total_passengers'], previous['total_passengers']),
                'totalTrains': _calc_trend_value(current['train_count'], previous['train_count']),
                'busyStations': _calc_trend_value(current['station_count'], previous['station_count']),
                'totalRevenue': _calc_trend_value(current['total_revenue'], previous['total_revenue'])
            }
        })


def _build_trend_data(queryset, frequency):
    if frequency == 'hourly':
        results = queryset.annotate(
            hour=ExtractHour(Coalesce('arrival_time', 'departure_time'))
        ).exclude(
            hour__isnull=True
        ).values(
            'hour'
        ).annotate(
            total=Sum(F('passengers_in') + F('passengers_out')),
            inbound=Sum('passengers_in'),
            outbound=Sum('passengers_out')
        ).order_by('hour')

        data = []
        for row in results:
            data.append({
                'time': f"{int(row['hour']):02d}:00",
                'total': row['total'] or 0,
                'inbound': row['inbound'] or 0,
                'outbound': row['outbound'] or 0
            })
        return data

    if frequency == 'weekly':
        trunc_func = TruncWeek
        time_format = 'week'
    elif frequency == 'monthly':
        trunc_func = TruncMonth
        time_format = 'month'
    else:
        trunc_func = TruncDay
        time_format = 'day'

    results = queryset.annotate(
        period=trunc_func('operation_date')
    ).values(
        'period'
    ).annotate(
        total=Sum(F('passengers_in') + F('passengers_out')),
        inbound=Sum('passengers_in'),
        outbound=Sum('passengers_out')
    ).order_by('period')

    data = []
    for row in results:
        data.append({
            'time': _format_time_period(row['period'], time_format),
            'total': row['total'] or 0,
            'inbound': row['inbound'] or 0,
            'outbound': row['outbound'] or 0
        })
    return data


class AnalyticsTrendView(APIView):
    """客流趋势数据视图"""

    def get(self, request):
        start_date, end_date = _get_date_range(request)
        frequency = request.query_params.get('frequency', 'daily')

        station_ids = _get_list_param(request, ['station_ids', 'stationIds', 'stationIds[]'])
        route_ids = _get_list_param(request, ['route_ids', 'routeIds', 'line_ids', 'lineIds', 'lineIds[]'])
        train_ids = _get_list_param(request, ['train_ids', 'trainIds', 'trainIds[]'])

        queryset = PassengerFlow.objects.filter(operation_date__range=[start_date, end_date])
        queryset = _apply_flow_filters(queryset, station_ids, route_ids, train_ids)

        return Response(_build_trend_data(queryset, frequency))


class AnalyticsHeatmapView(APIView):
    """客流热力图数据视图"""

    def get(self, request):
        start_date, end_date = _get_date_range(request)
        station_ids = _get_list_param(request, ['station_ids', 'stationIds', 'stationIds[]'])
        route_ids = _get_list_param(request, ['route_ids', 'routeIds', 'line_ids', 'lineIds', 'lineIds[]'])
        train_ids = _get_list_param(request, ['train_ids', 'trainIds', 'trainIds[]'])

        queryset = PassengerFlow.objects.filter(operation_date__range=[start_date, end_date])
        queryset = _apply_flow_filters(queryset, station_ids, route_ids, train_ids)

        station_totals = queryset.values('station_id').annotate(
            total=Sum(F('passengers_in') + F('passengers_out'))
        ).order_by('-total')[:10]

        top_station_ids = [item['station_id'] for item in station_totals]
        stations = Station.objects.filter(id__in=top_station_ids)
        station_map = {station.id: station.name for station in stations}

        times = [f'{hour:02d}:00' for hour in range(24)]
        data_matrix = [[0 for _ in times] for _ in top_station_ids]

        hourly = queryset.filter(
            station_id__in=top_station_ids
        ).annotate(
            hour=ExtractHour(Coalesce('arrival_time', 'departure_time'))
        ).exclude(
            hour__isnull=True
        ).values(
            'station_id', 'hour'
        ).annotate(
            total=Sum(F('passengers_in') + F('passengers_out'))
        )

        data_map = {}
        for item in hourly:
            data_map[(item['station_id'], item['hour'])] = item['total'] or 0

        for row_index, station_id in enumerate(top_station_ids):
            for hour in range(24):
                data_matrix[row_index][hour] = data_map.get((station_id, hour), 0)

        return Response({
            'stations': [station_map.get(station_id, str(station_id)) for station_id in top_station_ids],
            'times': times,
            'data': data_matrix
        })


class AnalyticsTimePeriodsView(APIView):
    """时段分析数据视图"""

    def get(self, request):
        start_date, end_date = _get_date_range(request)
        station_ids = _get_list_param(request, ['station_ids', 'stationIds', 'stationIds[]'])
        route_ids = _get_list_param(request, ['route_ids', 'routeIds', 'line_ids', 'lineIds', 'lineIds[]'])
        train_ids = _get_list_param(request, ['train_ids', 'trainIds', 'trainIds[]'])
        granularity = (request.query_params.get('granularity') or request.query_params.get('type') or 'period').lower()

        queryset = PassengerFlow.objects.filter(operation_date__range=[start_date, end_date])
        queryset = _apply_flow_filters(queryset, station_ids, route_ids, train_ids)

        if granularity in ('hour', 'hourly'):
            hourly = queryset.annotate(
                hour=ExtractHour(Coalesce('arrival_time', 'departure_time'))
            ).exclude(
                hour__isnull=True
            ).values(
                'hour'
            ).annotate(
                total=Sum(F('passengers_in') + F('passengers_out')),
                trains=Count('train', distinct=True)
            )

            hourly_map = {item['hour']: item for item in hourly}
            total_passengers = sum(item['total'] or 0 for item in hourly) or 1

            result = []
            for hour in range(24):
                stats = hourly_map.get(hour, {})
                passengers = stats.get('total') or 0
                trains = stats.get('trains') or 0
                result.append({
                    'id': hour + 1,
                    'name': f'{hour:02d}时',
                    'time': f'{hour:02d}:00-{hour:02d}:59',
                    'passengers': passengers,
                    'percentage': round((passengers / total_passengers) * 100, 2),
                    'trains': trains
                })

            return Response(result)

        if granularity in ('day', 'daily'):
            weekday_stats = queryset.values(
                weekday=ExtractIsoWeekDay('operation_date')
            ).annotate(
                total=Sum(F('passengers_in') + F('passengers_out')),
                trains=Count('train', distinct=True)
            )

            weekday_map = {item['weekday']: item for item in weekday_stats}
            total_passengers = sum(item['total'] or 0 for item in weekday_stats) or 1
            weekday_labels = {
                1: '周一',
                2: '周二',
                3: '周三',
                4: '周四',
                5: '周五',
                6: '周六',
                7: '周日'
            }

            result = []
            for weekday in range(1, 8):
                stats = weekday_map.get(weekday, {})
                passengers = stats.get('total') or 0
                trains = stats.get('trains') or 0
                label = weekday_labels[weekday]
                result.append({
                    'id': weekday,
                    'name': label,
                    'time': '',
                    'passengers': passengers,
                    'percentage': round((passengers / total_passengers) * 100, 2),
                    'trains': trains
                })

            return Response(result)

        if granularity in ('week', 'weekly'):
            weekly = queryset.annotate(
                period=TruncWeek('operation_date')
            ).values(
                'period'
            ).annotate(
                total=Sum(F('passengers_in') + F('passengers_out')),
                trains=Count('train', distinct=True)
            ).order_by('period')

            total_passengers = sum(item['total'] or 0 for item in weekly) or 1
            result = []
            for index, item in enumerate(weekly, 1):
                period_start = item['period']
                if isinstance(period_start, datetime):
                    period_start = period_start.date()
                period_end = period_start + timedelta(days=6) if period_start else None
                if period_end and period_end > end_date:
                    period_end = end_date
                time_label = ''
                if period_start and period_end:
                    time_label = f'{period_start:%Y-%m-%d} 至 {period_end:%Y-%m-%d}'

                passengers = item['total'] or 0
                trains = item['trains'] or 0
                result.append({
                    'id': index,
                    'name': f'第{index}周',
                    'time': time_label,
                    'passengers': passengers,
                    'percentage': round((passengers / total_passengers) * 100, 2),
                    'trains': trains
                })

            return Response(result)

        hourly = queryset.annotate(
            hour=ExtractHour(Coalesce('arrival_time', 'departure_time'))
        ).exclude(
            hour__isnull=True
        ).values(
            'hour'
        ).annotate(
            total=Sum(F('passengers_in') + F('passengers_out'))
        )

        hourly_map = {item['hour']: item['total'] or 0 for item in hourly}
        total_passengers = sum(hourly_map.values()) or 1

        periods = [
            {'id': 1, 'name': '凌晨', 'start': 0, 'end': 6, 'label': '00:00-06:00'},
            {'id': 2, 'name': '上午', 'start': 6, 'end': 12, 'label': '06:00-12:00'},
            {'id': 3, 'name': '下午', 'start': 12, 'end': 18, 'label': '12:00-18:00'},
            {'id': 4, 'name': '晚上', 'start': 18, 'end': 24, 'label': '18:00-24:00'},
        ]

        result = []
        for period in periods:
            period_passengers = sum(
                hourly_map.get(hour, 0) for hour in range(period['start'], period['end'])
            )
            period_trains = queryset.annotate(
                hour=ExtractHour(Coalesce('arrival_time', 'departure_time'))
            ).filter(
                hour__gte=period['start'],
                hour__lt=period['end']
            ).values('train').distinct().count()

            result.append({
                'id': period['id'],
                'name': period['name'],
                'time': period['label'],
                'passengers': period_passengers,
                'percentage': round((period_passengers / total_passengers) * 100, 2),
                'trains': period_trains
            })

        return Response(result)


class AnalyticsLineLoadsView(APIView):
    """线路负载分析数据视图"""

    def get(self, request):
        start_date, end_date = _get_date_range(request)
        station_ids = _get_list_param(request, ['station_ids', 'stationIds', 'stationIds[]'])
        route_ids = _get_list_param(request, ['route_ids', 'routeIds', 'line_ids', 'lineIds', 'lineIds[]'])
        train_ids = _get_list_param(request, ['train_ids', 'trainIds', 'trainIds[]'])

        queryset = PassengerFlow.objects.filter(operation_date__range=[start_date, end_date])
        queryset = _apply_flow_filters(queryset, station_ids, route_ids, train_ids)

        route_totals = list(queryset.values(
            'route_id',
            'route__name',
            'route__code'
        ).annotate(
            total_passengers=Sum(F('passengers_in') + F('passengers_out')),
            stations=Count('station', distinct=True)
        ).order_by('-total_passengers'))

        if not route_totals:
            return Response([])

        route_ids = [row['route_id'] for row in route_totals]

        # Optimize capacity calculation
        # Instead of fetching all rows, we can aggregate in DB if possible, or optimize the fetch
        # Fetch only necessary fields
        trip_rows = queryset.values(
            'route_id', 'train_id', 'operation_date', 'train__capacity'
        ).distinct()
        
        # Use a more efficient way to sum
        capacity_by_route = {}
        # Pre-calculate to avoid repeated dict lookups
        for row in trip_rows:
            r_id = row['route_id']
            cap = row['train__capacity'] or 0
            if r_id in capacity_by_route:
                capacity_by_route[r_id] += cap
            else:
                capacity_by_route[r_id] = cap

        station_counts = RouteStation.objects.filter(
            route_id__in=route_ids
        ).values('route_id').annotate(
            count=Count('station', distinct=True)
        )
        station_count_map = {row['route_id']: row['count'] for row in station_counts}

        results = []
        for row in route_totals:
            total_passengers = int(row['total_passengers'] or 0)
            capacity = int(capacity_by_route.get(row['route_id'], 0) or 0)
            stations = int(station_count_map.get(row['route_id'], row['stations'] or 0) or 0)
            avg_per_station = total_passengers / (stations or 1)
            load_rate = total_passengers / capacity if capacity else 0

            line_code = row['route__code']
            results.append({
                'lineId': row['route_id'],
                'lineName': row['route__name'] or (f'线路 {line_code}' if line_code is not None else '线路'),
                'lineCode': str(line_code) if line_code is not None else '',
                'totalPassengers': total_passengers,
                'capacity': capacity,
                'loadRate': round(load_rate, 4),
                'stations': stations,
                'avgPassengersPerStation': round(avg_per_station, 2)
            })

        return Response(results)


class AnalyticsTrainsView(APIView):
    """实时列车数据视图"""

    def get(self, request):
        start_date, end_date = _get_date_range(request)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        queryset = PassengerFlow.objects.filter(operation_date__range=[start_date, end_date])
        train_stats = queryset.values('train_id').annotate(
            last_date=Max('operation_date')
        ).order_by('-last_date')

        total = train_stats.count()
        offset = (page - 1) * page_size
        page_train_ids = [item['train_id'] for item in train_stats[offset:offset + page_size]]

        trains = {train.id: train for train in Train.objects.filter(id__in=page_train_ids)}
        data = []

        for train_id in page_train_ids:
            train = trains.get(train_id)
            if not train:
                continue

            train_flows = PassengerFlow.objects.filter(
                train_id=train_id,
                operation_date__range=[start_date, end_date]
            ).order_by('operation_date', 'arrival_time', 'departure_time', 'id')

            start_flow = train_flows.first()
            end_flow = train_flows.last()

            total_passengers = train_flows.aggregate(
                total=Sum(F('passengers_in') + F('passengers_out'))
            )['total'] or 0

            record_count = train_flows.count() or 1
            capacity = train.capacity or 1
            occupancy = total_passengers / (capacity * record_count)
            occupancy = max(0, min(1, occupancy))

            departure_station = start_flow.station.name if start_flow else '未知'
            arrival_station = end_flow.station.name if end_flow else '未知'
            departure_time = None
            if start_flow:
                departure_time = start_flow.departure_time or start_flow.arrival_time
            arrival_time = None
            if end_flow:
                arrival_time = end_flow.arrival_time or end_flow.departure_time

            status = 'running'
            status_text = '运行中'

            data.append({
                'id': train.id,
                'code': train.code,
                'type': train.code[:1] if train.code else 'T',
                'departureStation': departure_station,
                'arrivalStation': arrival_station,
                'departureTime': departure_time.isoformat() if departure_time else None,
                'arrivalTime': arrival_time.isoformat() if arrival_time else None,
                'occupancy': round(occupancy, 3),
                'status': status,
                'statusText': status_text
            })

        total_pages = (total + page_size - 1) // page_size
        return Response({
            'data': data,
            'total': total,
            'page': page,
            'pageSize': page_size,
            'totalPages': total_pages
        })


class AnalyticsRefreshView(APIView):
    """数据刷新视图"""

    def post(self, _request):
        return Response({'success': True, 'message': '数据已刷新'})


class AnalyticsExportView(APIView):
    """数据导出视图"""

    def get(self, request):
        start_date, end_date = _get_date_range(request)
        export_format = request.query_params.get('format', 'json')

        queryset = PassengerFlow.objects.filter(operation_date__range=[start_date, end_date])
        trend_data = _build_trend_data(queryset, 'daily')

        if export_format == 'json':
            content = json.dumps(trend_data, ensure_ascii=False)
            response = HttpResponse(content, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="analytics.json"'
            return response

        output = []
        header = ['time', 'total', 'inbound', 'outbound']
        output.append(','.join(header))
        for item in trend_data:
            output.append(f"{item['time']},{item['total']},{item['inbound']},{item['outbound']}")

        content = '\n'.join(output)
        content_type = 'text/csv' if export_format == 'csv' else 'application/vnd.ms-excel'
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="analytics.csv"'
        return response


class AnalyticsForecastView(APIView):
    """客流预测视图"""

    def get(self, request):
        start_date, end_date = _get_date_range(request)
        days = int(request.query_params.get('days', 7))
        forecast_days = max(1, min(days, 90))

        station_ids = _get_list_param(request, ['station_ids', 'stationIds', 'stationIds[]'])
        route_ids = _get_list_param(request, ['route_ids', 'routeIds', 'line_ids', 'lineIds', 'lineIds[]'])
        train_ids = _get_list_param(request, ['train_ids', 'trainIds', 'trainIds[]'])

        forecast_end = end_date + timedelta(days=forecast_days)
        queryset = PassengerFlow.objects.filter(operation_date__range=[start_date, forecast_end])
        queryset = _apply_flow_filters(queryset, station_ids, route_ids, train_ids)
        daily = queryset.annotate(
            period=TruncDay('operation_date')
        ).values(
            'period'
        ).annotate(
            total=Sum(F('passengers_in') + F('passengers_out'))
        ).order_by('period')

        history = []
        future_actuals = {}
        for item in daily:
            period = item['period']
            if isinstance(period, datetime):
                period = period.date()
            if not isinstance(period, date):
                continue
            total = float(item['total'] or 0)
            if period <= end_date:
                history.append((period, total))
            else:
                future_actuals[period] = total

        if not history:
            return Response([])

        history.sort(key=lambda row: row[0])
        totals = [value for _, value in history]

        window = min(14, len(totals))
        recent_totals = totals[-window:]
        mean = sum(recent_totals) / window if window else 0

        variance = 0
        if window > 1:
            variance = sum((value - mean) ** 2 for value in recent_totals) / window
        stdev = math.sqrt(variance) if variance > 0 else 0
        coefficient = (stdev / mean) if mean else 0
        confidence = max(0.65, min(0.95, 0.9 - coefficient * 0.5))

        slope = 0
        if window > 1:
            x_values = list(range(window))
            x_mean = sum(x_values) / window
            y_mean = mean
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, recent_totals))
            denominator = sum((x - x_mean) ** 2 for x in x_values) or 1
            slope = numerator / denominator

        weekday_totals = {}
        for period, total in history:
            weekday = period.weekday()
            weekday_totals.setdefault(weekday, []).append(total)

        weekday_avg = {
            weekday: sum(values) / len(values) for weekday, values in weekday_totals.items()
        }

        forecasts = []
        for i in range(1, forecast_days + 1):
            target_date = end_date + timedelta(days=i)
            base = weekday_avg.get(target_date.weekday(), mean)
            forecast = max(0, base + slope * i)
            lower = max(0, forecast - 1.64 * stdev)
            upper = max(lower, forecast + 1.64 * stdev)
            actual_value = future_actuals.get(target_date)

            forecasts.append({
                'timestamp': target_date.strftime('%Y-%m-%d'),
                'forecast': round(forecast, 2),
                'lowerBound': round(lower, 2),
                'upperBound': round(upper, 2),
                'confidence': round(confidence, 2),
                'actual': round(actual_value, 2) if actual_value is not None else None
            })

        return Response(forecasts)


# 数据管理API
class DataStatsView(APIView):
    """数据统计视图"""

    def get(self, request):
        """获取数据统计"""
        try:
            # 获取各实体的数量
            total_records = PassengerFlow.objects.count()
            stations_count = Station.objects.count()
            trains_count = Train.objects.count()
            routes_count = Route.objects.count()

            # 获取客运记录的日期范围
            date_range = PassengerFlow.objects.aggregate(
                min_date=Min('operation_date'),
                max_date=Max('operation_date')
            )

            # 获取最近上传（这里简化处理，返回空数组）
            recent_uploads = []

            return Response({
                'totalRecords': total_records,
                'stations': stations_count,
                'trains': trains_count,
                'lines': routes_count,
                'dateRange': {
                    'minDate': date_range['min_date'].strftime('%Y-%m-%d') if date_range['min_date'] else None,
                    'maxDate': date_range['max_date'].strftime('%Y-%m-%d') if date_range['max_date'] else None
                },
                'lastUpdated': datetime.now().isoformat(),
                'recentUploads': recent_uploads
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataRecordsView(APIView):
    """数据记录查询视图"""

    def get(self, request):
        """查询数据记录"""
        try:
            # 获取查询参数
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('pageSize', 20))
            start_date = request.query_params.get('startDate')
            end_date = request.query_params.get('endDate')
            station_ids = request.query_params.getlist('stationIds[]')
            line_ids = request.query_params.getlist('lineIds[]')
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sortBy', 'id')
            sort_order = request.query_params.get('sortOrder', 'asc')

            # 构建查询
            queryset = PassengerFlow.objects.all()

            # 应用日期过滤
            if start_date and end_date:
                queryset = queryset.filter(operation_date__range=[start_date, end_date])

            # 应用站点过滤
            if station_ids:
                queryset = queryset.filter(station_id__in=station_ids)

            # 应用线路过滤（route_id）
            if line_ids:
                queryset = queryset.filter(route_id__in=line_ids)

            # 应用搜索（这里简化处理，实际可以根据需要实现）

            # 应用排序
            if sort_order == 'desc':
                sort_by = f'-{sort_by}'
            queryset = queryset.order_by(sort_by)

            # 分页
            total = queryset.count()
            total_pages = (total + page_size - 1) // page_size
            offset = (page - 1) * page_size
            records = queryset[offset:offset + page_size]

            # 格式化响应数据
            data = []
            for record in records:
                # 获取关联的站点和线路信息
                station = Station.objects.filter(id=record.station_id).first()
                route = Route.objects.filter(id=record.route_id).first()
                train = Train.objects.filter(id=record.train_id).first()

                data.append({
                    'id': record.id,
                    'timestamp': record.arrival_time.isoformat() if record.arrival_time else record.operation_date.isoformat(),
                    'stationId': record.station_id,
                    'stationName': station.name if station else f'站点{record.station_id}',
                    'lineId': record.route_id,
                    'lineName': route.name if route else f'线路{record.route_id}',
                    'passengersIn': record.passengers_in,
                    'passengersOut': record.passengers_out,
                    'direction': 'both',  # 简化处理
                    'createdAt': record.created_at.isoformat() if record.created_at else None,
                    'updatedAt': record.updated_at.isoformat() if record.updated_at else None
                })

            return Response({
                'data': data,
                'total': total,
                'page': page,
                'pageSize': page_size,
                'totalPages': total_pages,
                'filters': {
                    'page': page,
                    'pageSize': page_size,
                    'startDate': start_date,
                    'endDate': end_date,
                    'stationIds': station_ids,
                    'lineIds': line_ids,
                    'search': search,
                    'sortBy': sort_by.lstrip('-'),
                    'sortOrder': sort_order
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
