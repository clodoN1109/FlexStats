from abc import ABC, abstractmethod
from typing import List

from domain.event import Event
from domain.observable import Observable


class IRepository(ABC):

    @abstractmethod
    def load_observables(self) -> List[Observable]:
        pass

    def load_events(self) -> List[Event]:
        pass

    @abstractmethod
    def save_observables(self, data: List[Observable]) -> None:
        pass

    def save_events(self, data: List[Event]) -> None:
        pass
