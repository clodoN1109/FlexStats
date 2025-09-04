from domain.domain import RangeDomain, EnumerationDomain, Domain
from dataclasses import dataclass
from typing import Dict, Union, List
import statistics

from domain.variable import Variable

ValueType = Union[int, float, str]


@dataclass
class Stats:
    events: int
    mean: float = None
    median: float = None
    std: float = None
    min: float = None
    max: float = None
    frequencies: Dict[ValueType, int] = None
    mode: ValueType = None


class StatsAnalyzer:
    """Static utility class to compute statistics for variables within a selected domain."""

    @staticmethod
    def compute(variable: Variable, domain: "Domain") -> Stats:
        # Filter values that belong to the domain
        values: List[ValueType] = [
            v for v in variable.data.values() if domain.belongs(v)
        ]

        if not values:
            return Stats(events=0)

        # Numeric stats
        if isinstance(domain, RangeDomain):
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            freq: Dict[ValueType, int] = {}
            for v in values:
                freq[v] = freq.get(v, 0) + 1
            mode = max(freq.items(), key=lambda x: x[1])[0] if freq else None
            return Stats(
                events=len(numeric_values),
                mean=statistics.mean(numeric_values) if numeric_values else None,
                median=statistics.median(numeric_values) if numeric_values else None,
                std=statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0,
                min=min(numeric_values) if numeric_values else None,
                max=max(numeric_values) if numeric_values else None,
                mode=mode,
            )

        # Enumeration stats
        elif isinstance(domain, EnumerationDomain):
            freq: Dict[ValueType, int] = {}
            for v in values:
                freq[v] = freq.get(v, 0) + 1
            mode = max(freq.items(), key=lambda x: x[1])[0] if freq else None
            return Stats(
                events=len(values),
                frequencies=freq,
                mode=mode,
            )

        # Fallback for unknown domain types
        return Stats(events=len(values))
