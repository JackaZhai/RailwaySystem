"""REST endpoints for data management."""
from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import PassengerRecord
from .serializers import PassengerRecordSerializer
from .services import DataIngestionService


class PassengerRecordViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Read-only access to passenger records."""

    queryset = PassengerRecord.objects.all()
    serializer_class = PassengerRecordSerializer
    filterset_fields = ["station", "line", "direction"]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["timestamp", "station", "line"]
    search_fields = ["station", "line"]

    @method_decorator(csrf_exempt)
    @action(detail=False, methods=["post"], url_path="ingest")
    def ingest(self, request: Request) -> Response:
        """Endpoint for uploading CSV/Excel files."""
        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        service = DataIngestionService()
        file_name = getattr(upload, "name", "upload.csv")
        report = service.import_file(upload.read(), file_type=file_name.split(".")[-1].lower())
        return Response({
            "total_rows": report.total_rows,
            "rows_ingested": report.rows_ingested,
            "rows_failed": report.rows_failed,
            "errors": report.errors,
        })
