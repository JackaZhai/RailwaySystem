from datetime import date, time, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Station, Train, Route, PassengerFlow


class DateRangeValidationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.station = Station.objects.create(
            id=1,
            name='Test Station',
            telecode='TS',
        )
        self.train = Train.objects.create(
            id=1,
            code='G1',
            capacity=100,
        )
        self.route = Route.objects.create(
            id=1,
            code=1,
            name='Test Route',
        )

        today = date.today()
        PassengerFlow.objects.create(
            route=self.route,
            train=self.train,
            station=self.station,
            operation_date=today - timedelta(days=10),
            arrival_time=time(8, 0, 0),
            passengers_in=100,
            passengers_out=50,
            revenue=1000,
        )
        PassengerFlow.objects.create(
            route=self.route,
            train=self.train,
            station=self.station,
            operation_date=today - timedelta(days=5),
            arrival_time=time(9, 0, 0),
            passengers_in=200,
            passengers_out=100,
            revenue=2000,
        )
        PassengerFlow.objects.create(
            route=self.route,
            train=self.train,
            station=self.station,
            operation_date=today,
            arrival_time=time(10, 0, 0),
            passengers_in=300,
            passengers_out=150,
            revenue=3000,
        )

    def test_kpi_requires_date_range(self):
        url = reverse('kpi')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('startDate', resp.data)
        self.assertIn('endDate', resp.data)

    def test_kpi_applies_date_range_filter(self):
        url = reverse('kpi')
        start = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        end = date.today().strftime('%Y-%m-%d')
        resp = self.client.get(url, {'startDate': start, 'endDate': end})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['totalPassengers'], (200 + 100) + (300 + 150))

    def test_missing_one_date_rejected(self):
        url = reverse('kpi')
        resp = self.client.get(url, {'startDate': date.today().strftime('%Y-%m-%d')})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('startDate', resp.data)
        self.assertIn('endDate', resp.data)

    def test_exceed_max_range_rejected(self):
        url = reverse('kpi')
        start = (date.today() - timedelta(days=400)).strftime('%Y-%m-%d')
        end = date.today().strftime('%Y-%m-%d')
        resp = self.client.get(url, {'startDate': start, 'endDate': end})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('日期范围不能超过', str(resp.data))

    def test_other_analysis_endpoints_require_date_range(self):
        endpoints = [
            reverse('heatmap'),
            reverse('station-assessment'),
            reverse('station-role-analysis'),
            reverse('busy-ranking'),
        ]
        for url in endpoints:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, url)
