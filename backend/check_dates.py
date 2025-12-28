import os
import django
from django.db.models import Min, Max, Count, Sum, F

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'railway_backend.settings')
django.setup()

from data_management.models import PassengerFlow, Station

def check_dates():
    result = PassengerFlow.objects.aggregate(
        min_date=Min('operation_date'),
        max_date=Max('operation_date'),
        count=Count('id')
    )
    print(f"Min Date: {result['min_date']}")
    print(f"Max Date: {result['max_date']}")
    print(f"Total Records: {result['count']}")

    # Check for data in the specific range we are using
    count_in_range = PassengerFlow.objects.filter(
        operation_date__gte='2016-01-14',
        operation_date__lte='2016-02-12'
    ).count()
    print(f"Records in range 2016-01-14 to 2016-02-12: {count_in_range}")

    # Check for null telecodes
    null_start = PassengerFlow.objects.filter(start_station_telecode__isnull=True).count()
    null_end = PassengerFlow.objects.filter(end_station_telecode__isnull=True).count()
    print(f"Records with null start_station_telecode: {null_start}")
    print(f"Records with null end_station_telecode: {null_end}")

    # Check telecode matching
    start_telecodes = set(PassengerFlow.objects.values_list('start_station_telecode', flat=True).distinct())
    end_telecodes = set(PassengerFlow.objects.values_list('end_station_telecode', flat=True).distinct())
    flow_telecodes = start_telecodes.union(end_telecodes)
    
    station_telecodes = set(Station.objects.values_list('telecode', flat=True))
    
    missing_telecodes = flow_telecodes - station_telecodes
    print(f"Total distinct start telecodes in flows: {len(start_telecodes)}")
    print(f"Total distinct end telecodes in flows: {len(end_telecodes)}")
    
    # Print the actual stations
    all_flow_telecodes = start_telecodes.union(end_telecodes)
    stations = Station.objects.filter(telecode__in=all_flow_telecodes)
    print("Stations involved in flows:")
    for s in stations:
        print(f"  {s.name} ({s.telecode})")

    print(f"Total telecodes in stations: {len(station_telecodes)}")
    print(f"Missing telecodes in stations: {len(missing_telecodes)}")
    if missing_telecodes:
        print(f"Example missing: {list(missing_telecodes)[:5]}")

    # Check for non-zero passengers
    total_passengers = PassengerFlow.objects.filter(
        operation_date__gte='2016-01-14',
        operation_date__lte='2016-02-12'
    ).aggregate(
        total=Sum(F('passengers_in') + F('passengers_out'))
    )
    print(f"Total passengers in range: {total_passengers['total']}")

if __name__ == '__main__':
    check_dates()
