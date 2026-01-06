from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg, F, Q, Min, Max, Value, FloatField, ExpressionWrapper, IntegerField, OuterRef, Exists, Case, When
from django.db.models.functions import Trunc, ExtractHour, Least, Coalesce
import pandas as pd
from datetime import datetime, timedelta

from .models import Station, Train, Route, RouteStation, PassengerFlow
from .serializers import (
    StationSerializer, TrainSerializer, RouteSerializer,
    RouteStationSerializer, PassengerFlowSerializer,
    PassengerFlowSummarySerializer, StationRankingSerializer,
    TimeDistributionSerializer, FlowAnalysisRequestSerializer
)

def _qp(request, *names):
    for name in names:
        value = request.query_params.get(name)
        if value not in (None, ''):
            return value
    return None


def _parse_ymd(value):
    if value in (None, ''):
        return None
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, 'year') and hasattr(value, 'month') and hasattr(value, 'day'):
        return value
    return datetime.strptime(str(value), '%Y-%m-%d').date()


DATE_RANGE_MAX_DAYS = 365


def _get_explicit_date_range(request, *, required, max_days=DATE_RANGE_MAX_DAYS):
    start_date = _qp(request, 'startDate', 'start_date')
    end_date = _qp(request, 'endDate', 'end_date')

    if not start_date and not end_date:
        if required:
            raise ValidationError({
                'startDate': '必须提供开始日期',
                'endDate': '必须提供结束日期',
            })
        return None, None

    if not start_date or not end_date:
        raise ValidationError({
            'startDate': '必须提供开始日期',
            'endDate': '必须提供结束日期',
        })

    try:
        start = _parse_ymd(start_date)
        end = _parse_ymd(end_date)
    except Exception:
        raise ValidationError({
            'startDate': '日期格式错误，必须为YYYY-MM-DD',
            'endDate': '日期格式错误，必须为YYYY-MM-DD',
        })

    if start > end:
        raise ValidationError('开始日期不能晚于结束日期')

    span_days = (end - start).days
    if span_days > max_days:
        raise ValidationError(f'日期范围不能超过{max_days}天')

    return start, end


def _resolve_date_range(request, default_range_type='month', require_explicit=False):
    raw_range_type = _qp(request, 'rangeType')
    range_type = raw_range_type or default_range_type

    start, end = _get_explicit_date_range(request, required=False)
    if start and end:
        if not raw_range_type:
            range_type = 'custom'
        return start, end, range_type

    if require_explicit:
        _get_explicit_date_range(request, required=True)

    latest_date = PassengerFlow.objects.aggregate(max_date=Max('operation_date'))['max_date']
    if not latest_date:
        return None, None, range_type

    if range_type == 'today':
        start = latest_date
        end = latest_date
    elif range_type == 'week':
        start = latest_date - timedelta(days=6)
        end = latest_date
    elif range_type == 'year':
        start = latest_date - timedelta(days=364)
        end = latest_date
    else:
        start = latest_date - timedelta(days=29)
        end = latest_date

    return start, end, range_type


class KpiView(APIView):
    """KPI指标视图"""

    def get(self, request):
        try:
            start, end, _range_type = _resolve_date_range(request, default_range_type='month', require_explicit=True)
            pf_qs = PassengerFlow.objects.all()
            if start and end:
                pf_qs = pf_qs.filter(operation_date__range=[start, end])

            # 统计总数
            total_passengers = pf_qs.aggregate(
                total=Sum(F('passengers_in') + F('passengers_out'))
            )['total'] or 0

            total_trains = Train.objects.count()
            
            # 繁忙站点（客流前10%）
            station_count = pf_qs.values('station_id').distinct().count()
            busy_stations_count = max(int(station_count * 0.1), 1) if station_count else 0

            total_revenue = pf_qs.aggregate(
                total=Sum('revenue')
            )['total'] or 0

            return Response({
                'totalPassengers': total_passengers,
                'totalTrains': total_trains,
                'busyStations': busy_stations_count,
                'totalRevenue': float(total_revenue),
                'trends': {
                    'totalPassengers': 5.2,
                    'totalTrains': 0,
                    'busyStations': 0,
                    'totalRevenue': 4.8
                }
            })
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            msg = str(e)
            return Response({'error': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HeatMapView(APIView):
    """热力图视图"""

    def get(self, request):
        try:
            start, end, _range_type = _resolve_date_range(request, default_range_type='month', require_explicit=True)

            pf_qs = PassengerFlow.objects.all()
            if start and end:
                pf_qs = pf_qs.filter(operation_date__range=[start, end])

            station_ids = pf_qs.values_list('station_id', flat=True).distinct()
            stations = Station.objects.filter(id__in=station_ids).order_by('id')
            times = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']

            data = []
            for station in stations:
                row = []
                for time_str in times:
                    hour = int(time_str.split(':')[0])
                    
                    # 查询该站点在附近的客流
                    flow = pf_qs.filter(
                        station=station,
                        arrival_time__hour__gte=hour,
                        arrival_time__hour__lt=hour+4
                    ).aggregate(total=Sum(F('passengers_in') + F('passengers_out')))['total'] or 0
                    
                    row.append({
                        'value': int(flow),
                        'time': time_str,
                        'label': station.name
                    })
                data.append(row)

            return Response(data)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            msg = str(e)
            return Response({'error': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        start, end = _get_explicit_date_range(self.request, required=False)
        if start and end:
            queryset = queryset.filter(operation_date__range=[start, end])

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

        station_id = request.query_params.get('station_id')
        start, end = _get_explicit_date_range(request, required=False)
        if start and end:
            queryset = queryset.filter(operation_date__range=[start, end])

        if station_id:
            try:
                queryset = queryset.filter(station_id=int(station_id))
            except (TypeError, ValueError):
                pass

        queryset = queryset.filter(Q(arrival_time__isnull=False) | Q(departure_time__isnull=False))

        hourly_data = queryset.annotate(
            hour=ExtractHour(Coalesce('arrival_time', 'departure_time'))
        ).values('hour').annotate(
            total_passengers=Sum(F('passengers_in') + F('passengers_out')),
            passengers_in=Sum('passengers_in'),
            passengers_out=Sum('passengers_out'),
            record_count=Count('id')
        ).order_by('hour')

        stats_map = {item['hour']: item for item in hourly_data if item['hour'] is not None}

        hourly_stats = []
        for hour in range(24):
            data = stats_map.get(hour, {})
            
            total_passengers = data.get('total_passengers', 0) or 0
            record_count = data.get('record_count', 0) or 1
            avg_passengers = total_passengers / record_count if record_count > 0 else 0
            passengers_in = data.get('passengers_in', 0) or 0
            passengers_out = data.get('passengers_out', 0) or 0

            hourly_stats.append({
                'hour': hour,
                'total_passengers': total_passengers,
                'passengers_in': passengers_in,
                'passengers_out': passengers_out,
                'avg_passengers': avg_passengers,
                'percentage': 0
            })

        total = sum(stat['total_passengers'] for stat in hourly_stats)
        if total > 0:
            for stat in hourly_stats:
                stat['percentage'] = (stat['total_passengers'] / total) * 100

        serializer = TimeDistributionSerializer(hourly_stats, many=True)
        return Response(serializer.data)


class FlowAnalysisView(APIView):
    """客流分析视图"""

    def post(self, request):
        """执行客流分析"""
        serializer = FlowAnalysisRequestSerializer(data=request.data)
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

        if station_ids:
            queryset = queryset.filter(station_id__in=station_ids)
        if route_ids:
            queryset = queryset.filter(route_id__in=route_ids)
        if train_ids:
            queryset = queryset.filter(train_id__in=train_ids)

        # 根据时间粒度分组
        if time_granularity == 'hour':
            # 按小时分组
            queryset = queryset.annotate(
                time_period=Trunc('arrival_time', 'hour')
            )
        elif time_granularity == 'day':
            queryset = queryset.annotate(
                time_period=Trunc('operation_date', 'day')
            )
        elif time_granularity == 'week':
            queryset = queryset.annotate(
                time_period=Trunc('operation_date', 'week')
            )
        elif time_granularity == 'month':
            queryset = queryset.annotate(
                time_period=Trunc('operation_date', 'month')
            )
        elif time_granularity == 'quarter':
            queryset = queryset.annotate(
                time_period=Trunc('operation_date', 'quarter')
            )
        else:  # year
            queryset = queryset.annotate(
                time_period=Trunc('operation_date', 'year')
            )

        # 执行聚合
        results = queryset.values('time_period').annotate(
            total_passengers=Sum(F('passengers_in') + F('passengers_out')),
            passengers_in=Sum('passengers_in'),
            passengers_out=Sum('passengers_out'),
            total_revenue=Sum('revenue'),
            train_count=Count('train', distinct=True),
            station_count=Count('station', distinct=True)
        ).order_by('time_period')

        # 格式化结果
        formatted_results = []
        for result in results:
            formatted_results.append({
                'time_period': result['time_period'],
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
            raw_start_date = request.query_params.get('startDate')
            raw_end_date = request.query_params.get('endDate')
            station_ids = request.query_params.getlist('stationIds[]')
            line_ids = request.query_params.getlist('lineIds[]')
            search = request.query_params.get('search', '')
            sort_by = request.query_params.get('sortBy', 'id')
            sort_order = request.query_params.get('sortOrder', 'asc')

            # 构建查询
            queryset = PassengerFlow.objects.all()

            # 应用日期过滤
            start, end = _get_explicit_date_range(request, required=False)
            if start and end:
                queryset = queryset.filter(operation_date__range=[start, end])

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
                    'startDate': raw_start_date,
                    'endDate': raw_end_date,
                    'stationIds': station_ids,
                    'lineIds': line_ids,
                    'search': search,
                    'sortBy': sort_by.lstrip('-'),
                    'sortOrder': sort_order
                }
            })
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StationAssessmentView(APIView):
    """站点评估数据视图 - 多维度评估"""

    def get(self, request):
        try:
            start, end, _range_type = _resolve_date_range(request, default_range_type='month', require_explicit=True)
            pf_qs = PassengerFlow.objects.all()
            if start and end:
                pf_qs = pf_qs.filter(operation_date__range=[start, end])

            stations = Station.objects.all()
            
            route_stats = RouteStation.objects.values('station_id').annotate(
                route_count=Count('route', distinct=True),
                start_count=Count('route', filter=Q(is_start=True)),
                end_count=Count('route', filter=Q(is_end=True))
            )
            route_map = {item['station_id']: item for item in route_stats}

            flow_stats = pf_qs.values('station_id').annotate(
                total_in=Sum('passengers_in'),
                total_out=Sum('passengers_out'),
            )
            flow_map = {item['station_id']: item for item in flow_stats}

            peak_hours_map = {}
            peak_flows_map = {}
            hourly_flows = (
                pf_qs.filter(Q(arrival_time__isnull=False) | Q(departure_time__isnull=False))
                .annotate(hour=ExtractHour(Coalesce('arrival_time', 'departure_time')))
                .values('station_id', 'hour')
                .annotate(flow=Sum(F('passengers_in') + F('passengers_out')))
                .order_by('station_id', '-flow')
            )
            
            processed_stations = set()
            for hf in hourly_flows:
                s_id = hf['station_id']
                if s_id not in processed_stations and hf.get('hour') is not None:
                    peak_hours_map[s_id] = hf['hour']
                    peak_flows_map[s_id] = hf.get('flow') or 0
                    processed_stations.add(s_id)

            assessment_data = []
            
            for station in stations:
                f_stat = flow_map.get(station.id, {'total_in': 0, 'total_out': 0})
                r_stat = route_map.get(station.id, {'route_count': 0, 'start_count': 0, 'end_count': 0})
                
                total_flow = (f_stat['total_in'] or 0) + (f_stat['total_out'] or 0)
                passengers_in = f_stat['total_in'] or 0
                passengers_out = f_stat['total_out'] or 0
                route_count = r_stat['route_count']
                
                peak_hour = peak_hours_map.get(station.id, None)
                peak_hour_str = f"{peak_hour}:00 - {peak_hour+1}:00" if peak_hour is not None else "暂无数据"

                peak_flow = peak_flows_map.get(station.id, 0) or 0

                inbound_ratio = 0
                if total_flow > 0:
                    inbound_ratio = passengers_in / total_flow
                outbound_ratio = 1 - inbound_ratio

                role_type = 'through'
                role_name = '通过站'
                
                is_hub = route_count >= 2 and total_flow > 5000
                
                if is_hub:
                    role_type = 'hub'
                    role_name = '枢纽/中转站'
                elif r_stat['start_count'] > 0 or inbound_ratio > 0.65:
                    role_type = 'origin'
                    role_name = '始发站'
                elif r_stat['end_count'] > 0 or outbound_ratio > 0.65:
                    role_type = 'destination'
                    role_name = '终到站'

                design_capacity = station.platform_count * 1000 # 假设每个站台设计容量 1000人/小时
                
                saturation = 0
                if design_capacity > 0:
                    saturation = peak_flow / design_capacity

                assessment_data.append({
                    'id': station.id,
                    'name': station.name,
                    'totalFlow': total_flow,
                    'peakFlow': peak_flow,
                    'peakHour': peak_hour_str,
                    'inboundRatio': inbound_ratio,
                    'outboundRatio': outbound_ratio,
                    'routeCount': route_count,
                    'roleType': role_type,
                    'roleName': role_name,
                    'platformCount': station.platform_count,
                    'designCapacity': design_capacity,
                    'saturation': saturation,
                    'transferPotential': 'High' if is_hub else 'Low' # 简化的中转潜力
                })
            
            assessment_data.sort(key=lambda x: x['totalFlow'], reverse=True)

            return Response(assessment_data)

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            msg = str(e)
            return Response({'error': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StationRoleAnalysisView(APIView):
    def get(self, request):
        try:
            start, end, range_type = _resolve_date_range(request, default_range_type='month', require_explicit=True)
            q = request.query_params.get('q', '').strip()

            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            page = max(page, 1)
            page_size = min(max(page_size, 1), 200)

            pf_qs = PassengerFlow.objects.all()
            if start and end:
                pf_qs = pf_qs.filter(operation_date__range=[start, end])

            if q:
                station_ids = Station.objects.filter(
                    Q(name__icontains=q) | Q(telecode__icontains=q)
                ).values_list('id', flat=True)
                pf_qs = pf_qs.filter(station_id__in=station_ids)

            start_rs = RouteStation.objects.filter(
                route_id=OuterRef('route_id'),
                station_id=OuterRef('station_id'),
                is_start=True,
            )
            end_rs = RouteStation.objects.filter(
                route_id=OuterRef('route_id'),
                station_id=OuterRef('station_id'),
                is_end=True,
            )

            pf_qs = pf_qs.annotate(
                is_start=Exists(start_rs),
                is_end=Exists(end_rs),
            )

            station_rows = list(
                pf_qs.values('station_id', 'station__name', 'station__telecode')
                .annotate(
                    total_in=Coalesce(Sum('passengers_in'), 0),
                    total_out=Coalesce(Sum('passengers_out'), 0),
                    route_count=Count('route_id', distinct=True),
                    endpoint_out=Coalesce(
                        Sum(
                            Case(
                                When(is_start=True, then=F('passengers_out')),
                                default=Value(0),
                                output_field=IntegerField(),
                            )
                        ),
                        0,
                    ),
                    endpoint_in=Coalesce(
                        Sum(
                            Case(
                                When(is_end=True, then=F('passengers_in')),
                                default=Value(0),
                                output_field=IntegerField(),
                            )
                        ),
                        0,
                    ),
                )
            )

            route_end_stats = RouteStation.objects.values('station_id').annotate(
                start_route_count=Count('route', filter=Q(is_start=True), distinct=True),
                end_route_count=Count('route', filter=Q(is_end=True), distinct=True),
            )
            route_end_map = {item['station_id']: item for item in route_end_stats}

            def calc_percentile(values, p):
                clean = sorted([v for v in values if isinstance(v, (int, float)) and v > 0])
                if not clean:
                    return None
                idx = int(round((len(clean) - 1) * p))
                idx = max(0, min(idx, len(clean) - 1))
                return clean[idx]

            items = []
            for row in station_rows:
                station_id = row['station_id']
                total_in = int(row.get('total_in') or 0)
                total_out = int(row.get('total_out') or 0)
                total_flow = total_in + total_out
                transfer = min(total_in, total_out)
                route_count = int(row.get('route_count') or 0)

                endpoint_out = int(row.get('endpoint_out') or 0)
                endpoint_in = int(row.get('endpoint_in') or 0)
                endpoint_total = endpoint_out + endpoint_in

                inbound_ratio = (total_in / total_flow) if total_flow > 0 else 0.0
                outbound_ratio = (total_out / total_flow) if total_flow > 0 else 0.0
                endpoint_in_ratio = (endpoint_in / endpoint_total) if endpoint_total > 0 else 0.0
                endpoint_out_ratio = (endpoint_out / endpoint_total) if endpoint_total > 0 else 0.0

                re_stat = route_end_map.get(station_id, {})
                start_route_count = int(re_stat.get('start_route_count') or 0)
                end_route_count = int(re_stat.get('end_route_count') or 0)

                items.append({
                    'id': int(station_id),
                    'name': row.get('station__name') or '',
                    'telecode': row.get('station__telecode'),
                    'totalFlow': total_flow,
                    'totalIn': total_in,
                    'totalOut': total_out,
                    'transfer': transfer,
                    'routeCount': route_count,
                    'startRouteCount': start_route_count,
                    'endRouteCount': end_route_count,
                    'endpointOut': endpoint_out,
                    'endpointIn': endpoint_in,
                    'endpointTotal': endpoint_total,
                    'inboundRatio': inbound_ratio,
                    'outboundRatio': outbound_ratio,
                    'endpointInboundRatio': endpoint_in_ratio,
                    'endpointOutboundRatio': endpoint_out_ratio,
                })

            hub_candidates = [it['transfer'] for it in items if it['routeCount'] >= 3 and it['transfer'] > 0]
            hub_threshold = calc_percentile(hub_candidates, 0.9)
            if hub_threshold is None:
                hub_threshold = 0

            for it in items:
                role_type = 'through'
                role_name = '通过站'

                if it['routeCount'] >= 3 and it['transfer'] > 0 and it['transfer'] >= hub_threshold:
                    role_type = 'hub'
                    role_name = '枢纽/中转站'
                else:
                    if it['endpointTotal'] > 0:
                        if it['endpointOutboundRatio'] >= 0.65 or (it['startRouteCount'] > 0 and it['endpointOutboundRatio'] >= 0.6):
                            role_type = 'origin'
                            role_name = '始发站'
                        elif it['endpointInboundRatio'] >= 0.65 or (it['endRouteCount'] > 0 and it['endpointInboundRatio'] >= 0.6):
                            role_type = 'destination'
                            role_name = '终到站'
                    else:
                        if it['startRouteCount'] > 0 and it['outboundRatio'] >= 0.65:
                            role_type = 'origin'
                            role_name = '始发站'
                        elif it['endRouteCount'] > 0 and it['inboundRatio'] >= 0.65:
                            role_type = 'destination'
                            role_name = '终到站'

                it['roleType'] = role_type
                it['roleName'] = role_name

            distribution_map = {}
            for it in items:
                key = it['roleType']
                if key not in distribution_map:
                    distribution_map[key] = {'roleType': it['roleType'], 'roleName': it['roleName'], 'count': 0}
                distribution_map[key]['count'] += 1

            total_stations = len(items)
            distribution = []
            for d in distribution_map.values():
                count = d['count']
                distribution.append({
                    'roleType': d['roleType'],
                    'roleName': d['roleName'],
                    'count': count,
                    'percent': (count / total_stations) if total_stations > 0 else 0.0,
                })
            distribution.sort(key=lambda x: x['count'], reverse=True)

            items.sort(key=lambda x: x['totalFlow'], reverse=True)
            offset = (page - 1) * page_size
            paged = items[offset:offset + page_size]

            return Response({
                'summary': {
                    'rangeType': range_type,
                    'startDate': str(start) if start else None,
                    'endDate': str(end) if end else None,
                    'totalStations': total_stations,
                },
                'distribution': distribution,
                'count': total_stations,
                'page': page,
                'pageSize': page_size,
                'results': paged,
            })
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            msg = str(e)
            return Response({'error': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BusyRankingView(APIView):
    def get(self, request):
        try:
            start, end, range_type = _resolve_date_range(request, default_range_type='month', require_explicit=True)
            q = request.query_params.get('q', '').strip()

            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 50))
            page = max(page, 1)
            page_size = min(max(page_size, 1), 200)

            w_send = float(request.query_params.get('wSend', 0.4))
            w_arrive = float(request.query_params.get('wArrive', 0.4))
            w_transfer = float(request.query_params.get('wTransfer', 0.2))

            w_send = max(w_send, 0.0)
            w_arrive = max(w_arrive, 0.0)
            w_transfer = max(w_transfer, 0.0)
            w_sum = w_send + w_arrive + w_transfer
            if w_sum <= 0:
                w_send, w_arrive, w_transfer = 0.4, 0.4, 0.2
            else:
                w_send /= w_sum
                w_arrive /= w_sum
                w_transfer /= w_sum

            pf_qs = PassengerFlow.objects.all()
            if start and end:
                pf_qs = pf_qs.filter(operation_date__range=[start, end])

            if q:
                station_ids = Station.objects.filter(
                    Q(name__icontains=q) | Q(telecode__icontains=q)
                ).values_list('id', flat=True)
                pf_qs = pf_qs.filter(station_id__in=station_ids)

            station_stats = pf_qs.values('station_id', 'station__name', 'station__telecode').annotate(
                send=Coalesce(Sum('passengers_out'), 0),
                arrive=Coalesce(Sum('passengers_in'), 0),
            ).annotate(
                transfer=Least(F('send'), F('arrive')),
            ).annotate(
                busy_index=ExpressionWrapper(
                    Value(w_send) * F('send') + Value(w_arrive) * F('arrive') + Value(w_transfer) * F('transfer'),
                    output_field=FloatField()
                )
            ).order_by('-busy_index')

            total = station_stats.count()
            max_page = max(((total - 1) // page_size) + 1, 1)
            page = min(page, max_page)
            offset = (page - 1) * page_size
            rows = list(station_stats[offset:offset + page_size])

            station_id_list = [row['station_id'] for row in rows]

            hourly_rows = pf_qs.filter(
                station_id__in=station_id_list,
                arrival_time__isnull=False,
            ).annotate(
                hour=ExtractHour('arrival_time')
            ).values('station_id', 'hour').annotate(
                flow=Sum(F('passengers_in') + F('passengers_out'))
            ).order_by('station_id', '-flow')

            peak_map = {}
            peak_list_map = {}
            for hr in hourly_rows:
                s_id = hr['station_id']
                hour = hr['hour']
                if hour is None:
                    continue
                if s_id not in peak_list_map:
                    peak_list_map[s_id] = []
                if len(peak_list_map[s_id]) < 3:
                    peak_list_map[s_id].append(int(hour))
                if s_id not in peak_map:
                    peak_map[s_id] = int(hour)

            results = []
            for idx, row in enumerate(rows):
                s_id = row['station_id']
                peak_hour = peak_map.get(s_id)
                peak_hours = peak_list_map.get(s_id, [])
                results.append({
                    'rank': offset + idx + 1,
                    'stationId': s_id,
                    'stationName': row['station__name'],
                    'stationTelecode': row.get('station__telecode'),
                    'send': int(row['send'] or 0),
                    'arrive': int(row['arrive'] or 0),
                    'transfer': int(row['transfer'] or 0),
                    'busyIndex': float(row['busy_index'] or 0),
                    'peakHour': f'{peak_hour}:00 - {peak_hour + 1}:00' if peak_hour is not None else None,
                    'peakHours': [f'{h}:00 - {h + 1}:00' for h in peak_hours],
                })

            return Response({
                'count': total,
                'page': page,
                'pageSize': page_size,
                'results': results,
            })
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            msg = str(e)
            return Response({'error': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

