import inspect
import sys
from pathlib import Path
import platform
import ctypes
import subprocess

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

    @staticmethod
    def get_scripts_dir() -> Path:
        if getattr(sys, "frozen", False):
            # Running in a PyInstaller bundle
            return Path(sys.executable).parent.resolve().joinpath("scripts").resolve()
        else:
            # Running in normal Python environment
            return Path(__file__).parent.parent.parent.joinpath("scripts").resolve()

    @staticmethod
    def get_window() -> dict:
        system = platform.system()
        info = {"os": system}

        try:
            if system == "Windows":
                user32 = ctypes.windll.user32
                info["screen_width"] = user32.GetSystemMetrics(0)
                info["screen_height"] = user32.GetSystemMetrics(1)

            elif system == "Linux":
                # use xrandr to get current resolution
                output = subprocess.check_output("xrandr | grep '*' | awk '{print $1}'", shell=True)
                width, height = map(int, output.decode().strip().split("x"))
                info["screen_width"] = width
                info["screen_height"] = height

            elif system == "Darwin":  # macOS
                output = subprocess.check_output(
                    "system_profiler SPDisplaysDataType | grep Resolution", shell=True
                ).decode().strip()
                # Example: "Resolution: 2560 x 1600 Retina"
                parts = [int(p) for p in output.split() if p.isdigit()]
                if len(parts) >= 2:
                    info["screen_width"], info["screen_height"] = parts[0], parts[1]

        except Exception as e:
            info["error"] = str(e)

        return info
