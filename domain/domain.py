from abc import ABC, abstractmethod
from typing import Union, List
import random

ValueType = Union[int, float, str]


class Domain(ABC):
    """Abstract base class for variable domains."""

    @abstractmethod
    def belongs(self, value: ValueType) -> bool:
        """Return True if the value is in the domain."""
        pass

    @abstractmethod
    def generate_random_sample(self, n: int) -> List[ValueType]:
        """Generate a list of n random values from the domain."""
        pass


class RangeDomain(Domain):
    """Numeric domain defined by min/max."""

    def __init__(self, min_value: float, max_value: float):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value

    def belongs(self, value: ValueType) -> bool:
        return isinstance(value, (int, float)) and self.min_value <= value <= self.max_value

    def generate_random_sample(self, n: int) -> List[ValueType]:
        return [random.uniform(self.min_value, self.max_value) for _ in range(n)]


class EnumerationDomain(Domain):
    """Domain defined by a set of discrete values."""

    def __init__(self, values: List[ValueType]):
        super().__init__()
        self.values = values

    def belongs(self, value: ValueType) -> bool:
        return value in self.values

    def generate_random_sample(self, n: int) -> List[ValueType]:
        return random.choices(self.values, k=n)

