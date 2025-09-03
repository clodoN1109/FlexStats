import inspect
import sys
from pathlib import Path

class Env:

    @staticmethod
    def get_script_path():
        frame = inspect.stack()[1]
        caller_file = Path(frame.filename).resolve().parent
        return caller_file.as_posix()

    @staticmethod
    def base_path() -> Path:
        if getattr(sys, "frozen", False):
            # Running in a PyInstaller bundle
            return Path(sys.executable).parent.resolve()
        else:
            # Running in normal Python environment
            return Path(__file__).parent.parent.joinpath("database").resolve()

    @staticmethod
    def get_observables_file_path(filename: str = "observables.json") -> Path:
        return Env.base_path() / filename

    @staticmethod
    def get_events_file_path(filename: str = "events.json") -> Path:
        return Env.base_path() / filename
