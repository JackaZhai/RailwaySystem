"""Database models for passenger data management."""
from __future__ import annotations

from django.db import models


class PassengerRecord(models.Model):
    """Stores passenger counts for a single station/line/timestamp."""

    timestamp = models.DateTimeField()
    station = models.CharField(max_length=255)
    line = models.CharField(max_length=255)
    direction = models.CharField(max_length=50, blank=True)
    passengers_in = models.PositiveIntegerField(default=0)
    passengers_out = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["timestamp", "station", "line"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["station"]),
            models.Index(fields=["line"]),
        ]
        unique_together = ("timestamp", "station", "line", "direction")

    def __str__(self) -> str:
        return f"{self.timestamp.isoformat()} {self.station} {self.line}"
