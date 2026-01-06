import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'railway_backend.settings')
django.setup()

from data_management.models import Station, Train, Route, RouteStation, PassengerFlow

def check_counts():
    print(f"Stations: {Station.objects.count()}")
    print(f"Trains: {Train.objects.count()}")
    print(f"Routes: {Route.objects.count()}")
    print(f"RouteStations: {RouteStation.objects.count()}")
    print(f"PassengerFlows: {PassengerFlow.objects.count()}")

if __name__ == "__main__":
    check_counts()
