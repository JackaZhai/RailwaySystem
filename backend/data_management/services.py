"""Data ingestion services for CSV/Excel imports."""
from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from django.db import transaction

from .models import PassengerRecord


@dataclass(slots=True)
class IngestionReport:
    """Summary of the ingestion run."""

    total_rows: int
    rows_ingested: int
    rows_failed: int
    errors: list[str]


class DataIngestionService:
    """Service for importing passenger records from tabular data sources."""

    REQUIRED_COLUMNS = {"timestamp", "station", "line", "passengers_in", "passengers_out"}

    def __init__(self, *, chunk_size: int = 5_000) -> None:
        self.chunk_size = chunk_size

    def import_file(self, file_bytes: bytes, file_type: str) -> IngestionReport:
        """Import the provided file, returning a summary report."""
        if file_type not in {"csv", "xlsx", "xls"}:
            raise ValueError(f"Unsupported file type: {file_type}")

        if file_type == "csv":
            dataframe = pd.read_csv(io.BytesIO(file_bytes))
        else:
            dataframe = pd.read_excel(io.BytesIO(file_bytes))

        return self._import_dataframe(dataframe)

    def _import_dataframe(self, dataframe: pd.DataFrame) -> IngestionReport:
        normalized = self._normalize_columns(dataframe)
        cleaned = self._clean_dataframe(normalized)
        total_rows = len(cleaned)
        errors: list[str] = []
        rows_ingested = 0

        for chunk in self._yield_chunks(cleaned):
            try:
                rows_ingested += self._persist_chunk(chunk)
            except Exception as exc:  # pragma: no cover - unexpected DB failure
                errors.append(str(exc))

        return IngestionReport(
            total_rows=total_rows,
            rows_ingested=rows_ingested,
            rows_failed=total_rows - rows_ingested,
            errors=errors,
        )

    def _normalize_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and formats."""
        rename_map = {col: col.strip().lower() for col in dataframe.columns}
        normalized = dataframe.rename(columns=rename_map)

        missing = self.REQUIRED_COLUMNS - set(normalized.columns)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        normalized["timestamp"] = pd.to_datetime(normalized["timestamp"], utc=True, errors="coerce")
        normalized["station"] = normalized["station"].astype(str).str.strip()
        normalized["line"] = normalized["line"].astype(str).str.strip()
        normalized["direction"] = normalized.get("direction", "").fillna("").astype(str).str.upper()
        normalized["passengers_in"] = pd.to_numeric(normalized["passengers_in"], errors="coerce").fillna(0).astype(int)
        normalized["passengers_out"] = pd.to_numeric(normalized["passengers_out"], errors="coerce").fillna(0).astype(int)
        return normalized

    def _clean_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates and invalid data."""
        deduped = dataframe.drop_duplicates(subset=["timestamp", "station", "line", "direction"])
        valid = deduped.dropna(subset=["timestamp", "station", "line"])
        valid = valid[valid["station"] != ""]
        valid = valid[valid["line"] != ""]
        return valid

    def _yield_chunks(self, dataframe: pd.DataFrame) -> Iterable[pd.DataFrame]:
        for start in range(0, len(dataframe), self.chunk_size):
            yield dataframe.iloc[start : start + self.chunk_size]

    def _persist_chunk(self, chunk: pd.DataFrame) -> int:
        records = [
            PassengerRecord(
                timestamp=row["timestamp"],
                station=row["station"],
                line=row["line"],
                direction=row.get("direction", ""),
                passengers_in=row.get("passengers_in", 0),
                passengers_out=row.get("passengers_out", 0),
                metadata=row.get("metadata", {}),
            )
            for _, row in chunk.iterrows()
        ]
        with transaction.atomic():
            before = PassengerRecord.objects.count()
            PassengerRecord.objects.bulk_create(records, ignore_conflicts=True)
            after = PassengerRecord.objects.count()
        return after - before


def load_sample_data() -> IngestionReport:
    """Utility for tests to load deterministic sample data."""
    dataframe = pd.DataFrame(
        [
            {
                "timestamp": "2024-01-01T08:00:00Z",
                "station": "Central",
                "line": "Red",
                "direction": "N",
                "passengers_in": 120,
                "passengers_out": 80,
            },
            {
                "timestamp": "2024-01-01T08:05:00Z",
                "station": "Central",
                "line": "Red",
                "direction": "S",
                "passengers_in": 95,
                "passengers_out": 110,
            },
        ]
    )

    service = DataIngestionService(chunk_size=1000)
    return service._import_dataframe(dataframe)
