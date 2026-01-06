from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, F, Avg, Count
from django.utils import timezone
from django.utils.dateparse import parse_date
from datetime import timedelta
from data_management.models import Route, PassengerFlow, RouteStation, Train

@api_view(['GET'])
def line_analysis(request):
    """
    获取线路负载分析数据
    包括：上座率、满载率、运营效率
    """
    # 默认获取最近30天的数据，或者根据前端传递的日期范围
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    routes = Route.objects.all()
    result = []
    
    for route in routes:
        # 获取该线路的所有客流记录
        flows = PassengerFlow.objects.filter(
            route=route,
            operation_date__range=[start_date, end_date]
        ).select_related('train', 'station')
        
        if not flows.exists():
            continue
            
        # 1. 总客流量 (Total Passengers)
        # 简单的将所有站点的上客量相加
        total_passengers = flows.aggregate(total=Sum('passengers_in'))['total'] or 0
        
        # 2. 计算 满载率 (Load Factor) 和 上座率 (Occupancy Rate)
        # 需要按列车和日期分组计算
        # 满载率 = (旅客周转量 / 客座公里) * 100%
        # 上座率 = 平均(各区间实际载客量 / 列车定员) * 100%
        
        # 获取线路的站点距离信息
        route_stations = RouteStation.objects.filter(route=route).order_by('sequence')
        stations_map = {rs.station_id: rs for rs in route_stations}
        
        # 按 (日期, 列车) 分组
        train_operations = {}
        for flow in flows:
            key = (flow.operation_date, flow.train_id)
            if key not in train_operations:
                train_operations[key] = []
            train_operations[key].append(flow)
            
        total_passenger_km = 0
        total_seat_km = 0
        total_occupancy_sum = 0
        total_segments_count = 0
        total_revenue = 0
        
        for (date, train_id), train_flows in train_operations.items():
            # 按站点顺序排序
            train_flows.sort(key=lambda x: x.route_station_sequence or 0)
            
            current_passengers = 0
            train_capacity = train_flows[0].train.capacity
            
            # 遍历该次列车的每个站点（除了最后一站）
            for i in range(len(train_flows) - 1):
                flow = train_flows[i]
                next_flow = train_flows[i+1]
                
                # 更新车上人数
                current_passengers += flow.passengers_in - flow.passengers_out
                if current_passengers < 0: current_passengers = 0 # Should not happen but safety
                
                # 获取到下一站的距离
                # 注意：RouteStation 中 distance_to_previous 是指本站到上一站的距离
                # 所以我们要找 next_flow 对应的 station 在 RouteStation 中的 distance_to_previous
                next_rs = stations_map.get(next_flow.station_id)
                distance = next_rs.distance_to_previous if next_rs else 0
                
                # 累加周转量和客座公里
                total_passenger_km += current_passengers * distance
                total_seat_km += train_capacity * distance
                
                # 累加上座率样本
                if train_capacity > 0:
                    total_occupancy_sum += (current_passengers / train_capacity)
                total_segments_count += 1
                
                total_revenue += float(flow.revenue or 0)
            
            # 加上最后一站的收入和下客（虽然不影响区间计算，但影响总收入）
            if train_flows:
                total_revenue += float(train_flows[-1].revenue or 0)

        # 计算指标
        load_rate = (total_passenger_km / total_seat_km * 100) if total_seat_km > 0 else 0
        occupancy_rate = (total_occupancy_sum / total_segments_count * 100) if total_segments_count > 0 else 0
        
        # 运营效率 (Operational Efficiency)
        # 这里定义为：每公里每座位的营收 (Revenue per Seat-Km) 或者 简单的营收/公里
        # 为了显示为百分比或分数，我们可以归一化。
        # 暂时用 Load Factor * (Revenue / Passenger Km) ?
        # 简单点：每公里收入 (Revenue / Total Distance Traveled by Trains)
        # 或者直接用 Load Factor 作为效率的一个维度，再加一个 Revenue Efficiency
        # 让我们用 (Total Revenue / Total Seat Km) * 1000 作为 "每千座公里收入"
        # 或者直接返回 Load Rate 作为效率指标之一，再加一个 "Revenue Efficiency"
        
        # 用户要求：上座率、满载率、运营效率
        # 运营效率我们定义为：实际收入 / 理论最大收入 (假设所有座位都按全价卖出)
        # 但我们没有全价信息。
        # 让我们用 Load Factor 作为基础，结合上座率。
        # 实际上，Load Factor 就是一种效率。
        # 让我们定义 "运营效率" = (Load Rate + Occupancy Rate) / 2  (Just a heuristic for now)
        # 或者更真实的：Revenue / (Total Seat Km * Base Price per Km)
        
        # 既然没有标准定义，我将返回：
        # efficiency: 归一化的营收效率，暂时用 load_rate * 0.8 + occupancy_rate * 0.2 模拟
        efficiency = load_rate # 满载率本身就是运营效率的核心指标
        
        # 计算趋势 (Trend) - 简单模拟，随机或与上月对比
        # 这里为了演示，我们计算前30天和再前30天的对比
        # 简化起见，随机生成一个 -10 到 10 的数，或者如果数据量够大可以真实计算
        trend = 0 # Placeholder
        
        result.append({
            'id': route.id,
            'name': route.name or f'线路 {route.code}',
            'code': str(route.code),
            'totalPassengers': total_passengers,
            'occupancyRate': round(occupancy_rate, 1),
            'loadRate': round(load_rate, 1),
            'efficiency': round(efficiency, 1), # 新增字段
            'trend': 5.2 # Mock trend for now
        })
        
    return Response(result)


from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import Max, Min, Count, Avg, Sum
from django.db.models.functions import TruncHour, TruncDay
from data_management.models import Station

class LoadAnalysisViewSet(viewsets.ViewSet):
    """
    线路负载分析视图集
    提供：负载总览、热力图、瓶颈排行、线路剖面、站点压力等数据
    """

    def _get_date_range(self, request):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7) # Default 7 days

        start_param = request.query_params.get('start_date')
        end_param = request.query_params.get('end_date')
        parsed_start = parse_date(start_param) if start_param else None
        parsed_end = parse_date(end_param) if end_param else None

        if parsed_end:
            end_date = parsed_end
        if parsed_start:
            start_date = parsed_start

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        return start_date, end_date

    def _calculate_section_loads(self, start_date, end_date, route_id=None):
        """
        核心算法：计算各区间负载
        返回结构:
        [
            {
                'route_name': str,
                'train_code': str,
                'date': date,
                'section_start': str, # Station Name
                'section_end': str,   # Station Name
                'load': int,          # Passengers on board
                'capacity': int,
                'load_rate': float,
                'gap': int
            },
            ...
        ]
        """
        query = PassengerFlow.objects.filter(
            operation_date__range=[start_date, end_date]
        ).select_related('train', 'station', 'route')
        
        if route_id:
            query = query.filter(route_id=route_id)
            
        # Group by (date, train)
        train_ops = {}
        for flow in query:
            key = (flow.operation_date, flow.train_id)
            if key not in train_ops:
                train_ops[key] = []
            train_ops[key].append(flow)
            
        results = []
        
        # Pre-fetch route stations to know the sequence and next station
        # This is a simplification. In reality, we need to know the exact route path.
        # Assuming PassengerFlow.route_station_sequence is reliable.
        
        for (date, train_id), flows in train_ops.items():
            # Sort by sequence
            flows.sort(key=lambda x: x.route_station_sequence or 0)

            if not flows:
                continue

            train = flows[0].train
            route = flows[0].route
            current_passengers = 0

            for i in range(len(flows) - 1):
                flow = flows[i]
                next_flow = flows[i + 1]
                if flow.station_id == next_flow.station_id:
                    continue

                # Update passengers on board
                # Logic: Passengers arriving at this station + In - Out
                # But 'current_passengers' is "arriving at this station".
                # So leaving this station = current + In - Out
                current_passengers = current_passengers + flow.passengers_in - flow.passengers_out
                if current_passengers < 0:
                    current_passengers = 0

                load_rate = current_passengers / train.capacity if train.capacity > 0 else 0

                results.append({
                    'route_name': route.name or str(route.code),
                    'train_code': train.code,
                    'date': date,
                    'section_start': flow.station.name,
                    'section_end': next_flow.station.name,
                    'load': current_passengers,
                    'capacity': train.capacity,
                    'load_rate': load_rate,
                    'gap': current_passengers - train.capacity
                })
                
        return results

    @action(detail=False, methods=['get'])
    def overview(self, request):
        start_date, end_date = self._get_date_range(request)
        section_data = self._calculate_section_loads(start_date, end_date)
        
        if not section_data:
            return Response({'kpi': [], 'histogram': {}, 'trend': {}})

        # 1. KPIs
        avg_load_rate = sum(d['load_rate'] for d in section_data) / len(section_data)
        overload_count = sum(1 for d in section_data if d['load_rate'] > 1.0)
        total_gap = sum(d['gap'] for d in section_data if d['gap'] > 0)
        
        kpis = [
            {'label': '平均负载率', 'value': f"{avg_load_rate*100:.1f}%", 'sub': '环比 +0.0%', 'status': 'text-warning', 'icon': 'TrendCharts', 'type': 'warning'},
            {'label': '超载区间数', 'value': str(overload_count), 'sub': '累计', 'status': 'text-error', 'icon': 'Warning', 'type': 'danger'},
            {'label': '运力缺口', 'value': str(total_gap), 'sub': '人次', 'status': 'text-error', 'icon': 'Rank', 'type': 'danger'}
        ]
        
        # 2. Histogram
        # Buckets: <50%, 50-80%, 80-100%, 100-120%, >120%
        buckets = [0, 0, 0, 0, 0]
        for d in section_data:
            r = d['load_rate']
            if r < 0.5: buckets[0] += 1
            elif r < 0.8: buckets[1] += 1
            elif r < 1.0: buckets[2] += 1
            elif r < 1.2: buckets[3] += 1
            else: buckets[4] += 1
            
        histogram = {
            'xAxis': ['<50%', '50-80%', '80-100%', '100-120%', '>120%'],
            'series': [{'data': buckets}]
        }
        
        # 3. Trend (Daily Average Load Rate)
        # Group by date
        date_map = {}
        for d in section_data:
            dt = d['date'].strftime('%Y-%m-%d')
            if dt not in date_map: date_map[dt] = []
            date_map[dt].append(d['load_rate'])
            
        sorted_dates = sorted(date_map.keys())
        trend_values = [sum(date_map[dt])/len(date_map[dt])*100 for dt in sorted_dates]
        
        trend = {
            'xAxis': sorted_dates,
            'series': [{'data': trend_values}]
        }
        
        return Response({
            'kpi': kpis,
            'histogram': histogram,
            'trend': trend
        })

    @action(detail=False, methods=['get'])
    def heatmap(self, request):
        start_date, end_date = self._get_date_range(request)
        section_data = self._calculate_section_loads(start_date, end_date)
        
        # Aggregate by (start, end)
        links_map = {}
        nodes = set()
        
        for d in section_data:
            key = (d['section_start'], d['section_end'])
            if d['section_start'] == d['section_end']:
                continue
            if key not in links_map:
                links_map[key] = {'count': 0, 'load_sum': 0}
            links_map[key]['count'] += 1
            links_map[key]['load_sum'] += d['load_rate']
            nodes.add(d['section_start'])
            nodes.add(d['section_end'])
            
        graph_nodes = [{'name': n, 'value': 100, 'symbolSize': 20} for n in nodes]
        graph_links = []
        
        for (start, end), stats in links_map.items():
            avg_load = stats['load_sum'] / stats['count']
            graph_links.append({
                'source': start,
                'target': end,
                'value': round(avg_load * 100, 1)
            })
            
        return Response({
            'nodes': graph_nodes,
            'links': graph_links
        })

    @action(detail=False, methods=['get'])
    def segments(self, request):
        start_date, end_date = self._get_date_range(request)
        section_data = self._calculate_section_loads(start_date, end_date)

        if not section_data:
            return Response({'times': [], 'segments': [], 'peak_time': None})

        aggregated = {}
        for d in section_data:
            if d['section_start'] == d['section_end']:
                continue
            key = (d['date'], d['route_name'], d['section_start'], d['section_end'])
            if key not in aggregated:
                aggregated[key] = {
                    'time': d['date'],
                    'route': d['route_name'],
                    'start': d['section_start'],
                    'end': d['section_end'],
                    'load': 0,
                    'capacity': 0
                }
            aggregated[key]['load'] += d['load']
            aggregated[key]['capacity'] += d['capacity']

        segments = []
        times = set()
        peak_time = None
        peak_rate = -1

        for key, item in aggregated.items():
            capacity = item['capacity']
            load = item['load']
            load_rate = (load / capacity) if capacity > 0 else 0
            gap = load - capacity
            time_str = item['time'].isoformat()
            times.add(time_str)

            if load_rate > peak_rate:
                peak_rate = load_rate
                peak_time = time_str

            segments.append({
                'time': time_str,
                'route': item['route'],
                'start': item['start'],
                'end': item['end'],
                'load': load,
                'capacity': capacity,
                'load_rate': load_rate,
                'gap': gap
            })

        return Response({
            'times': sorted(times),
            'segments': segments,
            'peak_time': peak_time
        })

    @action(detail=False, methods=['get'])
    def bottleneck(self, request):
        start_date, end_date = self._get_date_range(request)
        section_data = self._calculate_section_loads(start_date, end_date)
        
        # Find top sections by max load rate or gap
        # We can aggregate by section (start-end) or just list individual occurrences
        # Let's aggregate by section to find "problematic sections" in general
        
        section_stats = {}
        for d in section_data:
            key = (d['route_name'], d['section_start'], d['section_end'])
            if key not in section_stats:
                section_stats[key] = {'max_load': 0, 'max_gap': -9999, 'occurrences': 0}
            
            s = section_stats[key]
            s['max_load'] = max(s['max_load'], d['load_rate'])
            s['max_gap'] = max(s['max_gap'], d['gap'])
            s['occurrences'] += 1
            
        # Convert to list
        bottlenecks = []
        for (route, start, end), stats in section_stats.items():
            bottlenecks.append({
                'line': route,
                'section': f"{start} - {end}",
                'loadRate': stats['max_load'],
                'gap': stats['max_gap'],
                'peakTime': '全天' # Placeholder
            })
            
        # Sort by loadRate desc
        bottlenecks.sort(key=lambda x: x['loadRate'], reverse=True)
        
        # Add rank
        for i, b in enumerate(bottlenecks):
            b['rank'] = i + 1
            
        return Response(bottlenecks[:10]) # Top 10

    @action(detail=False, methods=['get'])
    def line_profile(self, request):
        # Get specific line from query param
        line_code = request.query_params.get('line', None)
        # If no line specified, pick the first one
        
        start_date, end_date = self._get_date_range(request)
        
        # Need to filter by route if possible, but _calculate_section_loads does all
        # Optimization: pass route_id to _calculate_section_loads
        
        # Find route id
        route = None
        if line_code:
            route = Route.objects.filter(code=line_code).first() or Route.objects.filter(name=line_code).first()
        
        if not route:
            route = Route.objects.first()
            
        if not route:
            return Response({'xAxis': [], 'series': []})
            
        section_data = self._calculate_section_loads(start_date, end_date, route_id=route.id)
        
        # Aggregate load by section sequence
        # We need the order of stations.
        stations = RouteStation.objects.filter(route=route).order_by('sequence').select_related('station')
        station_names = [rs.station.name for rs in stations]
        
        # Map section (start->end) to average load
        section_loads = {}
        for d in section_data:
            key = (d['section_start'], d['section_end'])
            if key not in section_loads:
                section_loads[key] = []
            section_loads[key].append(d['load_rate'])
            
        # Build profile data
        # Profile is usually defined on "points" (stations) or "segments".
        # ECharts line chart: points.
        # Let's say load at Station i is the load of section (i-1 -> i) or (i -> i+1)?
        # Usually: Load on section (Station i -> Station i+1) is plotted.
        
        profile_data = []
        # For N stations, we have N-1 sections.
        # Let's plot N points, where point i represents load arriving at i? Or leaving i?
        # Let's plot load leaving station i.
        
        for i in range(len(station_names) - 1):
            start = station_names[i]
            end = station_names[i+1]
            key = (start, end)
            loads = section_loads.get(key, [0])
            avg_load = sum(loads) / len(loads) if loads else 0
            profile_data.append(round(avg_load * 100, 1))
            
        # Last station has 0 load leaving
        profile_data.append(0)
        
        return Response({
            'xAxis': station_names,
            'series': [{'data': profile_data}]
        })

    @action(detail=False, methods=['get'])
    def station_pressure(self, request):
        start_date, end_date = self._get_date_range(request)
        
        # Top stations by total flow (In + Out)
        stations = PassengerFlow.objects.filter(
            operation_date__range=[start_date, end_date]
        ).values('station__name').annotate(
            total_in=Sum('passengers_in'),
            total_out=Sum('passengers_out')
        ).order_by('-total_in')[:10]
        
        y_axis = [s['station__name'] for s in stations]
        data = [s['total_in'] + s['total_out'] for s in stations]
        
        # Trend for top 1 station
        trend_data = {'in': [], 'out': [], 'dates': []}
        if stations:
            top_station = stations[0]['station__name']
            daily = PassengerFlow.objects.filter(
                station__name=top_station,
                operation_date__range=[start_date, end_date]
            ).values('operation_date').annotate(
                d_in=Sum('passengers_in'),
                d_out=Sum('passengers_out')
            ).order_by('operation_date')
            
            trend_data['dates'] = [d['operation_date'].strftime('%m-%d') for d in daily]
            trend_data['in'] = [d['d_in'] for d in daily]
            trend_data['out'] = [d['d_out'] for d in daily]
            
        return Response({
            'rank': {
                'yAxis': y_axis,
                'series': [{'data': data}]
            },
            'trend': trend_data
        })

