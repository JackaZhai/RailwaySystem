from rest_framework import serializers
from .models import Station, Train, Route, RouteStation, PassengerFlow


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class RouteStationSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source='route.code', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    station_telecode = serializers.CharField(source='station.telecode', read_only=True)
    previous_station_name = serializers.CharField(source='previous_station.name', read_only=True, allow_null=True)
    next_station_name = serializers.CharField(source='next_station.name', read_only=True, allow_null=True)

    class Meta:
        model = RouteStation
        fields = '__all__'
        extra_fields = ['route_name', 'station_name', 'station_telecode', 'previous_station_name', 'next_station_name']


class PassengerFlowSerializer(serializers.ModelSerializer):
    route_code = serializers.IntegerField(source='route.code', read_only=True)
    train_code = serializers.CharField(source='train.code', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    station_telecode = serializers.CharField(source='station.telecode', read_only=True)
    total_passengers = serializers.IntegerField(read_only=True)

    class Meta:
        model = PassengerFlow
        fields = '__all__'
        extra_fields = ['route_code', 'train_code', 'station_name', 'station_telecode', 'total_passengers']


class PassengerFlowSummarySerializer(serializers.Serializer):
    """客运记录汇总序列化器"""
    date = serializers.DateField()
    total_passengers = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_passengers_per_train = serializers.FloatField()
    station_count = serializers.IntegerField()


class StationRankingSerializer(serializers.Serializer):
    """站点排名序列化器"""
    station_id = serializers.IntegerField()
    station_name = serializers.CharField()
    station_telecode = serializers.CharField()
    total_passengers = serializers.IntegerField()
    passengers_in = serializers.IntegerField()
    passengers_out = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    ranking = serializers.IntegerField()


class TimeDistributionSerializer(serializers.Serializer):
    """时间分布序列化器"""
    hour = serializers.IntegerField()
    total_passengers = serializers.IntegerField()
    passengers_in = serializers.IntegerField()
    passengers_out = serializers.IntegerField()
    avg_passengers = serializers.FloatField()
    percentage = serializers.FloatField()


class FlowAnalysisRequestSerializer(serializers.Serializer):
    """客流分析请求序列化器"""
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    station_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    route_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    train_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    time_granularity = serializers.ChoiceField(
        choices=['hour', 'day', 'week', 'month', 'quarter', 'year'],
        default='day'
    )