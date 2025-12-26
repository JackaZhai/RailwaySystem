import calendar
import uuid
from datetime import date, timedelta
from typing import Optional

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse

from data_management.models import PassengerFlow, RouteStation, Station
from .models import OptimizationPlan, OptimizationScenario, OptimizationInsight


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _get_date_range(range_type: str, start_date: Optional[str], end_date: Optional[str]) -> tuple[date, date]:
    today = timezone.localdate()
    if range_type == 'today':
        return today, today
    if range_type == 'month':
        start = today.replace(day=1)
        end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        return start, end
    if range_type == 'custom':
        start = _parse_date(start_date) or today - timedelta(days=6)
        end = _parse_date(end_date) or today
        return start, end
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def _apply_day_type(qs, day_type: str):
    if day_type == 'weekday':
        return qs.filter(operation_date__week_day__in=[2, 3, 4, 5, 6])
    if day_type in {'weekend', 'holiday'}:
        return qs.filter(operation_date__week_day__in=[1, 7])
    return qs


def _ensure_defaults():
    scenarios = [
        {'code': 'base', 'name': '基线方案', 'status': 'ready', 'owner': '优化中心', 'tags': ['默认']},
        {'code': 'peak', 'name': '早高峰强化', 'status': 'draft', 'owner': '线路组', 'tags': ['早高峰', '增开']},
        {'code': 'green', 'name': '节能降耗', 'status': 'running', 'owner': '调度组', 'tags': ['平峰', '降耗']},
    ]
    for item in scenarios:
        OptimizationScenario.objects.get_or_create(code=item['code'], defaults=item)

    insights = [
        {'title': '早高峰瓶颈', 'detail': '中央站-东港连续三周高负载', 'tag': '瓶颈', 'impact': '预计提升 6%'},
        {'title': '平峰冗余', 'detail': '10:00-15:00 运力利用率偏低', 'tag': '节能', 'impact': '预计节约 5%'},
        {'title': '换乘拥堵', 'detail': '中央站换乘通道流速下降', 'tag': '枢纽', 'impact': '预计提升 3%'},
    ]
    if not OptimizationInsight.objects.exists():
        OptimizationInsight.objects.bulk_create([OptimizationInsight(**item) for item in insights])


def _format_ratio(value: float) -> int:
    return max(0, min(100, int(round(value * 100))))


def _build_overview(filters: dict) -> dict:
    _ensure_defaults()
    start, end = _get_date_range(filters.get('rangeType', 'week'), filters.get('startDate'), filters.get('endDate'))
    day_type = filters.get('dayType', 'weekday')

    qs = PassengerFlow.objects.select_related('route', 'train', 'station').filter(operation_date__range=(start, end))
    qs = _apply_day_type(qs, day_type)
    # lineGroup 暂不做过滤，后续可按线路标签扩展

    flows = list(qs)
    if not flows:
        return {
            'updatedAt': timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M'),
            'snapshot': {
                'efficiencyScore': 0,
                'loadMatch': 0,
                'peakAbsorb': 0,
                'capacityElastic': 0,
                'overloadedRatio': 0,
                'focusLine': '',
            },
            'kpis': {
                'averageOccupancy': 0,
                'maxSectionLoad': 0,
                'overloadedCount': 0,
                'idleCount': 0,
            },
            'lines': [],
            'odAlerts': [],
            'odMatrix': {'pairs': []},
            'density': {'trains': [], 'matrix': []},
            'timetable': [],
            'hubs': [],
            'recommendations': [],
            'scenarios': _list_scenarios(),
            'insights': _list_insights(),
        }

    route_stats = {}
    station_stats = {}
    station_names = {}
    segment_stats = {}
    od_stats = {}
    route_train_stats = {}
    train_totals = {}
    train_names = {}
    timetable_stats = {key: {'sum_ratio': 0.0, 'count': 0} for key in ['06-08', '08-10', '10-16', '16-19', '19-22']}
    latest_date = max(flow.operation_date for flow in flows)
    split_date = latest_date - timedelta(days=6)

    route_ids = {flow.route_id for flow in flows}
    segment_map = _get_route_segment_map(route_ids)
    segment_pair_map = _get_route_segment_pair_map(route_ids)
    od_station_map = _get_od_station_map(flows)

    for flow in flows:
        total_pass = flow.passengers_in + flow.passengers_out
        capacity = max(flow.train.capacity or 0, 1)
        ratio = total_pass / capacity

        route = flow.route
        route_stat = route_stats.setdefault(route.id, {
            'id': route.id,
            'name': route.name or f'线路 {route.code}',
            'code': f'L{route.code}',
            'ratio_sum': 0.0,
            'count': 0,
            'max_ratio': 0.0,
            'total_pass': 0,
            'recent_pass': 0,
            'prev_pass': 0,
        })
        route_stat['ratio_sum'] += ratio
        route_stat['count'] += 1
        route_stat['max_ratio'] = max(route_stat['max_ratio'], ratio)
        route_stat['total_pass'] += total_pass

        if flow.operation_date >= split_date:
            route_stat['recent_pass'] += total_pass
        else:
            route_stat['prev_pass'] += total_pass

        station_stats[flow.station_id] = station_stats.get(flow.station_id, 0) + total_pass
        station_names[flow.station_id] = flow.station.name

        train_key = flow.train_id
        train_totals[train_key] = train_totals.get(train_key, 0) + total_pass
        train_names[train_key] = flow.train.code

        route_train_key = (route.id, flow.train_id)
        entry = route_train_stats.setdefault(route_train_key, {'ratio_sum': 0.0, 'count': 0, 'train_code': flow.train.code})
        entry['ratio_sum'] += ratio
        entry['count'] += 1

        bucket = _time_bucket(flow.departure_time or flow.arrival_time)
        if bucket:
            timetable_stats[bucket]['sum_ratio'] += ratio
            timetable_stats[bucket]['count'] += 1

        if flow.route_station_sequence is not None:
            segment_key = (route.id, flow.route_station_sequence)
            segment_name = segment_map.get(segment_key)
            if segment_name:
                segment = segment_stats.setdefault(segment_key, {
                    'segment': segment_name,
                    'ratio_sum': 0.0,
                    'count': 0,
                    'high_days': set(),
                })
                segment['ratio_sum'] += ratio
                segment['count'] += 1
                if ratio >= 0.9:
                    segment['high_days'].add(flow.operation_date)

        od_pair = _get_od_pair(flow, od_station_map, segment_pair_map)
        if od_pair:
            od_entry = od_stats.setdefault(od_pair, {
                'from': od_pair[0],
                'to': od_pair[1],
                'total': 0,
                'days': set(),
            })
            od_entry['total'] += total_pass
            od_entry['days'].add(flow.operation_date)

    line_rows = []
    max_section_load = 0
    overloaded_count = 0
    idle_count = 0
    focus_line = ''
    focus_load = 0
    occupancy_acc = 0.0
    occupancy_count = 0

    for route_id, stat in route_stats.items():
        avg_ratio = stat['ratio_sum'] / max(stat['count'], 1)
        max_ratio = stat['max_ratio']
        trend = _calc_trend(stat['recent_pass'], stat['prev_pass'])
        occupancy = _format_ratio(avg_ratio)
        section_load = _format_ratio(max_ratio)
        peak_segment = _peak_segment(route_id, segment_stats, segment_map)

        line_rows.append({
            'id': stat['id'],
            'name': stat['name'],
            'code': stat['code'],
            'occupancy': occupancy,
            'sectionLoad': section_load,
            'trend': trend,
            'peakSegment': peak_segment,
        })

        max_section_load = max(max_section_load, section_load)
        occupancy_acc += occupancy
        occupancy_count += 1
        if section_load >= 90:
            overloaded_count += 1
        if occupancy < 55:
            idle_count += 1
        if section_load > focus_load:
            focus_load = section_load
            focus_line = stat['name']

    average_occupancy = int(round(occupancy_acc / max(occupancy_count, 1)))
    overloaded_ratio = int(round((overloaded_count / max(len(line_rows), 1)) * 100))

    snapshot = {
        'efficiencyScore': _calc_efficiency_score(average_occupancy, overloaded_ratio, idle_count, len(line_rows)),
        'loadMatch': average_occupancy,
        'peakAbsorb': max_section_load,
        'capacityElastic': max(0, 100 - int(round((idle_count / max(len(line_rows), 1)) * 100))),
        'overloadedRatio': overloaded_ratio,
        'focusLine': focus_line,
    }

    density = _build_density(route_stats, route_train_stats, train_totals, train_names)
    timetable = _build_timetable(timetable_stats)
    hubs = _build_hubs(station_stats, station_names)
    recommendations = _build_recommendations(line_rows, hubs)

    return {
        'updatedAt': timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M'),
        'snapshot': snapshot,
        'kpis': {
            'averageOccupancy': average_occupancy,
            'maxSectionLoad': max_section_load,
            'overloadedCount': overloaded_count,
            'idleCount': idle_count,
        },
        'lines': sorted(line_rows, key=lambda item: item['sectionLoad'], reverse=True),
        'odAlerts': _build_od_alerts_from_od(od_stats),
        'odMatrix': _build_od_matrix(od_stats),
        'density': density,
        'timetable': timetable,
        'hubs': hubs,
        'recommendations': recommendations,
        'scenarios': _list_scenarios(),
        'insights': _list_insights(),
    }


def _calc_trend(recent: int, previous: int) -> int:
    if previous <= 0:
        return 0
    return int(round(((recent - previous) / previous) * 100))


def _calc_efficiency_score(avg_occ: int, overloaded_ratio: int, idle_count: int, total_lines: int) -> int:
    idle_ratio = int(round((idle_count / max(total_lines, 1)) * 100))
    score = 100 - overloaded_ratio - idle_ratio + int(round(avg_occ * 0.2))
    return max(0, min(100, score))


def _time_bucket(value):
    if not value:
        return None
    hour = value.hour
    if 6 <= hour < 8:
        return '06-08'
    if 8 <= hour < 10:
        return '08-10'
    if 10 <= hour < 16:
        return '10-16'
    if 16 <= hour < 19:
        return '16-19'
    if 19 <= hour < 22:
        return '19-22'
    return None


def _build_timetable(stats: dict):
    windows = [
        ('06:00-08:00', '06-08'),
        ('08:00-10:00', '08-10'),
        ('10:00-16:00', '10-16'),
        ('16:00-19:00', '16-19'),
        ('19:00-22:00', '19-22'),
    ]
    results = []
    for label, key in windows:
        entry = stats[key]
        avg_ratio = entry['sum_ratio'] / max(entry['count'], 1)
        load = round(avg_ratio, 2)
        suggestion = '保持现有频次'
        if load >= 0.9:
            suggestion = '加密发车至 3-4 分钟'
        elif load <= 0.55:
            suggestion = '合并班次，节约运力'
        results.append({'time': label, 'load': load, 'suggestion': suggestion})
    return results


def _get_route_segment_map(route_ids):
    segment_map = {}
    rows = RouteStation.objects.filter(
        route_id__in=route_ids,
        next_station__isnull=False,
    ).select_related('station', 'next_station').order_by('route_id', 'sequence')
    for row in rows:
        segment_map[(row.route_id, row.sequence)] = f'{row.station.name} - {row.next_station.name}'
    return segment_map


def _get_route_segment_pair_map(route_ids):
    pair_map = {}
    rows = RouteStation.objects.filter(
        route_id__in=route_ids,
        next_station__isnull=False,
    ).select_related('station', 'next_station').order_by('route_id', 'sequence')
    for row in rows:
        pair_map[(row.route_id, row.sequence)] = {
            'from': row.station.name,
            'to': row.next_station.name,
        }
    return pair_map


def _peak_segment(route_id, segment_stats, segment_map):
    segments = {key: value for key, value in segment_stats.items() if key[0] == route_id}
    if not segments:
        return '暂无数据'
    top_key = max(segments.keys(), key=lambda key: segments[key]['ratio_sum'] / max(segments[key]['count'], 1))
    return segment_map.get(top_key, segments[top_key]['segment'])


def _get_od_station_map(flows):
    telecodes = set()
    for flow in flows:
        if flow.start_station_telecode:
            telecodes.add(flow.start_station_telecode)
        if flow.end_station_telecode:
            telecodes.add(flow.end_station_telecode)
    if not telecodes:
        return {}
    stations = Station.objects.filter(telecode__in=telecodes).values('name', 'telecode')
    return {item['telecode']: item['name'] for item in stations}


def _get_od_pair(flow, od_station_map, segment_pair_map):
    start_code = flow.start_station_telecode
    end_code = flow.end_station_telecode
    if not start_code or not end_code:
        if flow.route_station_sequence is None:
            return None
        fallback = segment_pair_map.get((flow.route_id, flow.route_station_sequence))
        if not fallback:
            return None
        return fallback['from'], fallback['to']
    if start_code == end_code:
        return None
    if start_code not in od_station_map or end_code not in od_station_map:
        return None
    return od_station_map[start_code], od_station_map[end_code]


def _build_od_alerts_from_od(od_stats):
    if not od_stats:
        return []
    sorted_pairs = sorted(od_stats.values(), key=lambda item: item['total'], reverse=True)
    max_total = max(item['total'] for item in od_stats.values()) or 1
    alerts = []
    for pair in sorted_pairs[:3]:
        load = min(1.2, pair['total'] / max_total)
        days = len(pair['days'])
        suggestion = '建议加密班次' if load >= 0.8 else '建议优化发车间隔'
        alerts.append({
            'segment': f"{pair['from']} → {pair['to']}",
            'load': round(load, 2),
            'duration': f'连续 {max(days, 1)} 天高负载',
            'suggestion': suggestion,
        })
    return alerts


def _build_od_matrix(od_stats):
    pairs = sorted(od_stats.values(), key=lambda item: item['total'], reverse=True)[:10]
    return {
        'pairs': [
            {
                'from': pair['from'],
                'to': pair['to'],
                'total': pair['total'],
                'days': len(pair['days']),
            }
            for pair in pairs
        ]
    }


def _build_density(route_stats, route_train_stats, train_totals, train_names):
    top_routes = sorted(route_stats.values(), key=lambda item: item['total_pass'], reverse=True)[:4]
    top_trains = sorted(train_totals.items(), key=lambda item: item[1], reverse=True)[:5]
    train_codes = [train_names.get(train_id, f'T{train_id}') for train_id, _ in top_trains]
    matrix = []
    for route in top_routes:
        row = {'line': route['name'], 'trains': []}
        for train_id, _ in top_trains:
            entry = route_train_stats.get((route['id'], train_id))
            ratio = 0.0
            if entry:
                ratio = entry['ratio_sum'] / max(entry['count'], 1)
            row['trains'].append({'name': train_names.get(train_id, f'T{train_id}'), 'density': round(ratio, 2)})
        matrix.append(row)
    return {'trains': train_codes, 'matrix': matrix}


def _build_hubs(station_stats, station_names):
    top = sorted(station_stats.items(), key=lambda item: item[1], reverse=True)[:4]
    if not top:
        return []
    max_value = max(value for _, value in top)
    hubs = []
    for station_id, value in top:
        ratio = value / max_value if max_value else 0
        hubs.append({
            'name': station_names.get(station_id, f'站点 {station_id}'),
            'role': '枢纽站点',
            'degree': round(ratio, 2),
            'betweenness': round(ratio * 0.85, 2),
            'closeness': round(ratio * 0.8, 2),
            'trend': 2,
        })
    return hubs


def _build_recommendations(lines, hubs):
    recommendations = []
    if lines:
        top = max(lines, key=lambda item: item['sectionLoad'])
        recommendations.append({
            'priority': 'P0',
            'priorityClass': 'priority-high',
            'type': '增开建议',
            'title': f'{top["name"]} 早高峰增开 2 列',
            'detail': f'断面“{top["peakSegment"]}”持续高负载，建议加开短线区间车。',
            'impact': '预计削峰 6%',
            'line': top['name'],
        })
        idle = min(lines, key=lambda item: item['occupancy'])
        recommendations.append({
            'priority': 'P1',
            'priorityClass': 'priority-medium',
            'type': '时刻表优化',
            'title': f'{idle["name"]} 平峰期延长发车间隔',
            'detail': '平峰客流低于阈值，建议适度压缩运力。',
            'impact': '运力节约 4%',
            'line': idle['name'],
        })
    if hubs:
        recommendations.append({
            'priority': 'P2',
            'priorityClass': 'priority-low',
            'type': '枢纽优化',
            'title': f'{hubs[0]["name"]} 优化换乘动线',
            'detail': '枢纽高峰拥堵明显，建议增设引导与分流标识。',
            'impact': '换乘效率 +5%',
            'line': '枢纽网络',
        })
    return recommendations


def _list_scenarios():
    return [
        {
            'id': scenario.code,
            'name': scenario.name,
            'status': scenario.status,
            'updatedAt': scenario.updated_at.strftime('%H:%M'),
            'owner': scenario.owner,
            'tags': scenario.tags,
        }
        for scenario in OptimizationScenario.objects.order_by('id')
    ]


def _list_insights():
    return [
        {
            'title': insight.title,
            'detail': insight.detail,
            'tag': insight.tag,
            'impact': insight.impact,
        }
        for insight in OptimizationInsight.objects.order_by('-created_at')
    ][:3]


class OptimizationOverviewView(APIView):
    def get(self, request):
        filters = {
            'rangeType': request.GET.get('rangeType', 'week'),
            'startDate': request.GET.get('startDate'),
            'endDate': request.GET.get('endDate'),
            'lineGroup': request.GET.get('lineGroup', 'all'),
            'dayType': request.GET.get('dayType', 'weekday'),
        }
        overview = _build_overview(filters)
        last_plan = OptimizationPlan.objects.order_by('-created_at').first()
        if last_plan:
            overview['lastPlan'] = {
                'id': last_plan.plan_id,
                'title': last_plan.title,
                'status': last_plan.status,
                'createdAt': last_plan.created_at.strftime('%Y-%m-%d %H:%M'),
                'expectedImpact': last_plan.expected_impact,
            }
        return Response(overview)


class OptimizationPlanView(APIView):
    def post(self, request):
        payload = request.data or {}
        filters = payload.get('filters', {})
        overview = _build_overview({
            'rangeType': filters.get('timeRange', {}).get('type', 'week'),
            'startDate': filters.get('timeRange', {}).get('startDate'),
            'endDate': filters.get('timeRange', {}).get('endDate'),
            'lineGroup': filters.get('lineGroup', 'all'),
            'dayType': filters.get('dayType', 'weekday'),
        })

        plan_id = f'plan-{uuid.uuid4().hex[:10]}'
        summary = {
            'id': plan_id,
            'title': '自动生成方案',
            'status': 'ready',
            'createdAt': timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M'),
            'expectedImpact': '削峰 6%，节约 3%',
        }

        plan = OptimizationPlan.objects.create(
            plan_id=plan_id,
            title=summary['title'],
            status=summary['status'],
            expected_impact=summary['expectedImpact'],
            filters=filters,
            goal=payload.get('goal', ''),
            constraints=payload.get('constraints', []),
            notes=payload.get('notes', ''),
            recommendations=overview.get('recommendations', []),
        )

        result = {
            'planId': plan.plan_id,
            'status': plan.status,
            'summary': summary,
            'recommendations': plan.recommendations,
        }
        return Response(result, status=status.HTTP_201_CREATED)


class OptimizationPlanDetailView(APIView):
    def get(self, request, plan_id: str):
        plan = OptimizationPlan.objects.filter(plan_id=plan_id).first()
        if not plan:
            return Response({'detail': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'planId': plan.plan_id,
            'status': plan.status,
            'summary': {
                'id': plan.plan_id,
                'title': plan.title,
                'status': plan.status,
                'createdAt': plan.created_at.strftime('%Y-%m-%d %H:%M'),
                'expectedImpact': plan.expected_impact,
            },
            'recommendations': plan.recommendations,
        })


class OptimizationPlanExportView(APIView):
    def get(self, request, plan_id: str):
        plan = OptimizationPlan.objects.filter(plan_id=plan_id).first()
        if not plan:
            return Response({'detail': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        content = 'plan_id,title,status,expected_impact\n{},{},{},{}\n'.format(
            plan.plan_id, plan.title, plan.status, plan.expected_impact
        )
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=\"{plan.plan_id}.csv\"'
        return response
