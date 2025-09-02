from __future__ import annotations
from domain.property import Property
from dataclasses import dataclass
from typing import List

@dataclass
class Record:
    observable: str
    state: List["Property"]

    def to_dict(self) -> dict:
        return {
            "observable": self.observable,
            "state": [prop.to_dict() for prop in self.state],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Record":
        return cls(
            observable=data["observable"],
            state=[Property.from_dict(p) for p in data["state"]],
        )

