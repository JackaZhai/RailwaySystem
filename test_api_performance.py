
import os
import sys
import django
import time
from django.db.models import Sum, Count, F, Max
from datetime import timedelta

# Setup Django environment
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "railway_backend.settings")
django.setup()

from data_management.models import PassengerFlow, RouteStation

def test_line_loads():
    print("Starting test_line_loads...")
    start_time = time.time()

    # Simulate _get_date_range logic
    last_record = PassengerFlow.objects.order_by('-operation_date').first()
    if last_record:
        end_date = last_record.operation_date
    else:
        from django.utils import timezone
        end_date = timezone.localdate()
    
    start_date = end_date - timedelta(days=29)
    print(f"Date range: {start_date} to {end_date}")

    queryset = PassengerFlow.objects.filter(operation_date__range=[start_date, end_date])
    count = queryset.count()
    print(f"Queryset count: {count}")

    t1 = time.time()
    route_totals = list(queryset.values(
        'route_id',
        'route__name',
        'route__code'
    ).annotate(
        total_passengers=Sum(F('passengers_in') + F('passengers_out')),
        stations=Count('station', distinct=True)
    ).order_by('-total_passengers'))
    print(f"Route totals query took: {time.time() - t1:.4f}s")

    if not route_totals:
        print("No route totals found.")
        return

    route_ids = [row['route_id'] for row in route_totals]

    t2 = time.time()
    # The problematic part
    trip_rows = queryset.values(
        'route_id', 'train_id', 'operation_date', 'train__capacity'
    ).distinct()
    
    # Force evaluation
    trip_rows_list = list(trip_rows)
    print(f"Trip rows query took: {time.time() - t2:.4f}s. Rows: {len(trip_rows_list)}")

    t3 = time.time()
    capacity_by_route = {}
    for row in trip_rows_list:
        r_id = row['route_id']
        cap = row['train__capacity'] or 0
        if r_id in capacity_by_route:
            capacity_by_route[r_id] += cap
        else:
            capacity_by_route[r_id] = cap
    print(f"Capacity calculation took: {time.time() - t3:.4f}s")

    print(f"Total time: {time.time() - start_time:.4f}s")

if __name__ == "__main__":
    test_line_loads()
