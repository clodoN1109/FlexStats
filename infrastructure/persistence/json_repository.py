import json
from pathlib import Path
from typing import List
from application.ports.i_repository import IRepository
from domain.event import Event
from domain.observable import Observable
from infrastructure.environment.environment import Env


class JsonRepository(IRepository):
    """Concrete repository using a JSON file."""

    def __init__(self):
        self.observables_file_path: Path = Env.get_observables_file_path()
        self.events_file_path: Path = Env.get_events_file_path()
        if not self.observables_file_path.exists():
            # initialize empty file
            self.save_observables([])

    def load_observables(self) -> List[Observable]:
        with open(self.observables_file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        observables: List[Observable] = []
        for item in raw_data:
            try:
                obs = Observable(name=item["name"], source=item["source"])
                observables.append(obs)
            except Exception as e:
                print(f"Skipping invalid observable in storage: {item}, error: {e}")
        return observables

    def load_events(self) -> List[Event]:
        try:
            with open(self.events_file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except FileNotFoundError:
            return []

        events: List[Event] = []
        for item in raw_data:
            try:
                events.append(Event.from_dict(item))
            except Exception as e:
                print(f"Skipping invalid event in storage: {item}, error: {e}")
        return events

    def save_observables(self, observables: List[Observable]) -> None:
        data = [{"name": obs.name, "source": obs.source} for obs in observables]
        with open(self.observables_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def save_events(self, events: List[Event]) -> None:
        data = [event.to_dict() for event in events]
        with open(self.events_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
