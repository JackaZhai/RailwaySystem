from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg, F, Q, Min, Max
from django.db.models.functions import Trunc
import pandas as pd
from datetime import datetime, timedelta

from .models import Station, Train, Route, RouteStation, PassengerFlow
from .serializers import (
    StationSerializer, TrainSerializer, RouteSerializer,
    RouteStationSerializer, PassengerFlowSerializer,
    PassengerFlowSummarySerializer, StationRankingSerializer,
    TimeDistributionSerializer, FlowAnalysisRequestSerializer
)


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
