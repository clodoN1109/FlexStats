from pathlib import Path


def get_observables_file_path(filename: str = "observables.json") -> Path:
    base_path = Path(__file__).parent.parent.joinpath("database").resolve()
    return base_path / filename


def get_events_file_path(filename: str = "events.json") -> Path:
    base_path = Path(__file__).parent.parent.joinpath("database").resolve()
    return base_path / filename
