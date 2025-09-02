from dataclasses import dataclass, field
from datetime import datetime
from typing import Union, Dict, Iterator

ValueType = Union[int, float, str]

class VariableData:
    def __init__(self) -> None:
        self._values: Dict[datetime, ValueType] = {}

    def add(self, timestamp: datetime, value: ValueType) -> None:
        self._values[timestamp] = value

    def all_values(self) -> list[ValueType]:
        """Return all unique values, ignoring timestamps."""
        return list(set(self._values.values()))

    # --- container-like methods ---
    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, key: datetime) -> ValueType:
        return self._values[key]

    def __setitem__(self, key: datetime, value: ValueType) -> None:
        self._values[key] = value

    def __iter__(self) -> Iterator[datetime]:
        return iter(self._values)

    def items(self):
        return self._values.items()

    def values(self):
        return self._values.values()

    def keys(self):
        return self._values.keys()

    def __str__(self) -> str:
        if not self._values:
            return "VariableData(empty)"

        lines = []
        for ts, value in sorted(self._values.items()):
            lines.append(f"{ts.isoformat()} → {value}")
        return "VariableData{\n  " + "\n  ".join(lines) + "\n}"


@dataclass
class Variable:
    name: str
    data: VariableData = field(default_factory=VariableData)


@dataclass
class Variable:
    name: str
    data: VariableData = field(default_factory=VariableData)

