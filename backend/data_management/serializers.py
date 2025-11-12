"""Serialization utilities for passenger records."""
from __future__ import annotations

from rest_framework import serializers

from .models import PassengerRecord


class PassengerRecordSerializer(serializers.ModelSerializer):
    """Serializer for passenger record objects."""

    class Meta:
        model = PassengerRecord
        fields = [
            "id",
            "timestamp",
            "station",
            "line",
            "direction",
            "passengers_in",
            "passengers_out",
            "metadata",
        ]
