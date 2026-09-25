"""Phase 10: Multi-source data ingestion — CSV, JSON, mock APIs with deduplication."""

import csv
import json
import logging
from dataclasses import dataclass
from typing import Any, Generator

logger = logging.getLogger(__name__)


@dataclass
class DataRecord:
    """A single ingested record with metadata."""
    source: str  # "csv", "json", "api"
    record_id: str
    content: str
    metadata: dict[str, Any]


class DataLoader:
    """Load data from CSV, JSON files, or mock APIs with deduplication."""

    def __init__(self):
        self.seen_ids = set()

    def load_csv(self, filepath: str) -> Generator[DataRecord, None, None]:
        """Load CSV; yield deduplicated records."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    record_id = row.get("id") or row.get("ID")
                    if not record_id or record_id in self.seen_ids:
                        continue
                    self.seen_ids.add(record_id)
                    yield DataRecord(
                        source="csv",
                        record_id=record_id,
                        content=row.get("text") or row.get("description") or str(row),
                        metadata={k: v for k, v in row.items() if k not in ["id", "ID", "text", "description"]},
                    )
        except Exception as e:
            logger.error(f"CSV load failed: {e}")

    def load_json(self, filepath: str) -> Generator[DataRecord, None, None]:
        """Load JSON array; yield deduplicated records."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]
                for item in data:
                    record_id = item.get("id")
                    if not record_id or record_id in self.seen_ids:
                        continue
                    self.seen_ids.add(record_id)
                    yield DataRecord(
                        source="json",
                        record_id=record_id,
                        content=item.get("content") or item.get("text") or json.dumps(item),
                        metadata={k: v for k, v in item.items() if k not in ["id", "content", "text"]},
                    )
        except Exception as e:
            logger.error(f"JSON load failed: {e}")

    def load_mock_api(self, num_records: int = 50) -> Generator[DataRecord, None, None]:
        """Generate mock customer data (simulates API calls)."""
        categories = ["shipping", "return", "billing", "technical", "account"]
        for i in range(num_records):
            record_id = f"api-{i}"
            if record_id in self.seen_ids:
                continue
            self.seen_ids.add(record_id)
            category = categories[i % len(categories)]
            yield DataRecord(
                source="api",
                record_id=record_id,
                content=f"Customer inquiry #{i}: {category} issue with order OD-{1000+i}.",
                metadata={"category": category, "order_id": f"OD-{1000+i}", "priority": "medium" if i % 3 == 0 else "low"},
            )
