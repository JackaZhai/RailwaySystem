from django.db import models
from django.utils import timezone


class Station(models.Model):
    """站点表"""
    id = models.IntegerField(primary_key=True, verbose_name='站点ID')
    travel_area_id = models.IntegerField(null=True, blank=True, verbose_name='旅行区ID')
    name = models.CharField(max_length=100, verbose_name='站点名称')
    code = models.IntegerField(null=True, blank=True, verbose_name='站点代码')
    telecode = models.CharField(max_length=10, unique=True, verbose_name='站点电报码')
    shortname = models.CharField(max_length=20, null=True, blank=True, verbose_name='站点简称')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'station'
        verbose_name = '站点'
        verbose_name_plural = '站点'

    def __str__(self):
        return f'{self.name} ({self.telecode})'


class Train(models.Model):
    """列车表"""
    id = models.IntegerField(primary_key=True, verbose_name='列车编码')
    code = models.CharField(max_length=20, verbose_name='列车代码')
    capacity = models.IntegerField(verbose_name='列车运量')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'train'
        verbose_name = '列车'
        verbose_name_plural = '列车'

    def __str__(self):
        return f'{self.code} (容量: {self.capacity})'


class Route(models.Model):
    """运营线路表"""
    id = models.IntegerField(primary_key=True, verbose_name='运营线路编码')
    code = models.IntegerField(verbose_name='线路代码')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='线路名称')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'route'
        verbose_name = '运营线路'
        verbose_name_plural = '运营线路'

    def __str__(self):
        return f'线路 {self.code} ({self.name or "未命名"})'


class RouteStation(models.Model):
    """线路站点表"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stations', verbose_name='运营线路')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, verbose_name='站点')
    sequence = models.IntegerField(verbose_name='线路站点顺序')
    previous_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_stations',
        verbose_name='上一站'
    )
    next_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_stations',
        verbose_name='下一站'
    )
    distance_to_previous = models.IntegerField(default=0, verbose_name='与上一站距离(公里)')
    total_distance = models.IntegerField(default=0, verbose_name='累计运输距离(公里)')
    is_start = models.BooleanField(default=False, verbose_name='是否起始站点')
    is_end = models.BooleanField(default=False, verbose_name='是否终点站点')
    must_stop = models.BooleanField(default=True, verbose_name='是否必须停靠')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'route_station'
        verbose_name = '线路站点'
        verbose_name_plural = '线路站点'
        unique_together = ['route', 'station']
        ordering = ['route', 'sequence']

    def __str__(self):
        return f'{self.route.code}-{self.sequence}: {self.station.name}'


class PassengerFlow(models.Model):
    """客运记录表"""
    serial_number = models.IntegerField(null=True, blank=True, verbose_name='序号')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, verbose_name='运营线路')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, verbose_name='列车')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, verbose_name='站点')
    route_station_sequence = models.IntegerField(null=True, blank=True, verbose_name='线路站点顺序')
    operation_date = models.DateField(verbose_name='运行日期')
    arrival_time = models.TimeField(null=True, blank=True, verbose_name='到达时间')
    departure_time = models.TimeField(null=True, blank=True, verbose_name='出发时间')
    passengers_in = models.IntegerField(default=0, verbose_name='上客量')
    passengers_out = models.IntegerField(default=0, verbose_name='下客量')
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='车票价格')
    start_station_telecode = models.CharField(max_length=10, null=True, blank=True, verbose_name='起点站电报码')
    end_station_telecode = models.CharField(max_length=10, null=True, blank=True, verbose_name='终点站电报码')
    revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='收入')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'passenger_flow'
        verbose_name = '客运记录'
        verbose_name_plural = '客运记录'
        indexes = [
            models.Index(fields=['operation_date']),
            models.Index(fields=['route', 'operation_date']),
            models.Index(fields=['station', 'operation_date']),
            models.Index(fields=['train']),
        ]
        ordering = ['-operation_date', 'route', 'train', 'station']

    def __str__(self):
        return f'{self.operation_date} {self.train.code} @ {self.station.name}'

    @property
    def total_passengers(self):
        """总客流量"""
        return self.passengers_in + self.passengers_out
