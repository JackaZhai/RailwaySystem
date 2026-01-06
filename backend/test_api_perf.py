import os
import django
import time
import json

# Setup Django environment BEFORE importing anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'railway_backend.settings')
django.setup()

from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from data_management.views import StationAssessmentView, PassengerFlowViewSet

def test_apis():
    factory = APIRequestFactory()
    
    print("Testing StationAssessmentView...")
    start_time = time.time()
    view = StationAssessmentView.as_view()
    request = factory.get('/api/analytics/stations/')
    try:
        response = view(request)
        elapsed = time.time() - start_time
        print(f"StationAssessmentView Status: {response.status_code}")
        print(f"Time elapsed: {elapsed:.2f}s")
        if response.status_code == 200:
            data = response.data
            print(f"Data length: {len(data)}")
            if len(data) > 0:
                print(f"First item: {data[0]}")
        else:
            print(f"Error: {response.data}")
    except Exception as e:
        print(f"StationAssessmentView Exception: {e}")

    print("\nTesting PassengerFlowViewSet time_distribution...")
    start_time = time.time()
    view = PassengerFlowViewSet.as_view({'get': 'time_distribution'})
    request = factory.get('/api/passenger-flows/time_distribution/')
    try:
        response = view(request)
        elapsed = time.time() - start_time
        print(f"TimeDistribution Status: {response.status_code}")
        print(f"Time elapsed: {elapsed:.2f}s")
        if response.status_code == 200:
            data = response.data
            print(f"Data length: {len(data)}")
    except Exception as e:
        print(f"TimeDistribution Exception: {e}")

if __name__ == '__main__':
    test_apis()
