import sys
import shutil
import subprocess

class ExternalScriptHandler:
    def __init__(self, scripts):
        self.scripts = scripts

    @staticmethod
    def run_script(script):
        """Run the script without capturing output."""
        return ExternalScriptHandler._execute(script, capture_output=False)

    @staticmethod
    def run_script_and_capture(script):
        """Run the script and capture JSON output from stdout."""
        return ExternalScriptHandler._execute(script, capture_output=True)

    @staticmethod
    def _execute(script, capture_output: bool):
        import subprocess, shutil, sys

        ext = script.extension.lower()
        path = script.path

        if getattr(sys, "frozen", False):
            python_exec = shutil.which("python") or shutil.which("python3")
            if not python_exec:
                raise RuntimeError("Python interpreter not found in PATH.")
        else:
            python_exec = sys.executable

        interpreters = {
            ".py": [python_exec],
            ".ps1": ["pwsh", "-ExecutionPolicy", "Bypass", "-File"],
            ".sh": ["bash"],
            ".bat": None,
            ".rb": ["ruby"],
        }

        if ext not in interpreters:
            raise RuntimeError(f"Unsupported script type: {ext}")

        cmd = interpreters[ext]

        if cmd is None:
            cmdline = [path]
        else:
            if shutil.which(cmd[0]) is None:
                raise RuntimeError(f"Interpreter not found: {cmd[0]}")
            cmdline = cmd + [path]

        try:
            if capture_output:
                result = subprocess.run(
                    cmdline, check=True, capture_output=True, text=True
                )
                return result.stdout
            else:
                subprocess.run(cmdline, check=True)
                return None
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Script failed with exit code {e.returncode}")


