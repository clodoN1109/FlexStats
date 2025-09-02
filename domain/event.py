from __future__ import annotations
from domain.record import Record
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


@dataclass
class Event:
    records: List["Record"]
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.astimezone(timezone.utc).isoformat(),
            "records": [rec.to_dict() for rec in self.records],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        ts = datetime.fromisoformat(data["timestamp"])
        # Normalize to UTC
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        else:
            ts = ts.astimezone(timezone.utc)

        return cls(
            timestamp=ts,
            records=[Record.from_dict(r) for r in data["records"]],
        )
