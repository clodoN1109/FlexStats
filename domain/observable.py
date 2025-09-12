from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
from typing import List
import json
import requests

from domain.property import Property
from infrastructure.processing.external_script_handler import ExternalScriptHandler


class Observable:
    def __init__(self, name: str, source: str):
        self.name: str = name
        self.source: str = source
        self.is_url: bool = False
        self.is_local: bool = False
        self._validate_source()

    def _validate_source(self):
        """Check if the source is a valid local path or URL."""
        parsed = urlparse(self.source)
        if parsed.scheme in ("http", "https"):
            self.is_url = True
        else:
            self.is_local = Path(self.source).exists()

    def fetch_state(self) -> List["Property"]:
        def flatten(data, parent_key=""):
            items = []
            if isinstance(data, dict):
                for k, v in data.items():
                    new_key = f"{parent_key}/{k}" if parent_key else k
                    items.extend(flatten(v, new_key))
            elif isinstance(data, list):
                for idx, v in enumerate(data):
                    new_key = f"{parent_key}/{idx}" if parent_key else str(idx)
                    items.extend(flatten(v, new_key))
            else:
                if isinstance(data, (str, int, float)):
                    items.append((parent_key, data))
            return items

        try:
            if self.is_url:
                response = requests.get(self.source, timeout=5)
                response.raise_for_status()
                raw_data = response.json()
            elif self.is_local:
                path = Path(self.source)
                if path.suffix.lower() == ".json":
                    with open(path, "r", encoding="utf-8") as f:
                        raw_data = json.load(f)
                else:
                    # Treat as script
                    class DummyScript:
                        def __init__(self, path):
                            self.path = str(path)
                            self.extension = path.suffix
                            self.name = path.stem

                    script = DummyScript(path)
                    output = ExternalScriptHandler.run_script_and_capture(script)
                    raw_data = json.loads(output)
            else:
                raise ValueError(f"Invalid source path or URL: {self.source}")

            props = []
            if isinstance(raw_data, (dict, list)):
                for k, v in flatten(raw_data):
                    props.append(Property(name=k, value=v))
            elif isinstance(raw_data, list):
                for item in raw_data:
                    if isinstance(item, dict) and "name" in item and "value" in item:
                        props.append(Property(name=item["name"], value=item["value"]))

            return props

        except Exception as e:
            print(f"Failed to fetch or parse state for {self.name}: {e}")
            return []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source": self.source,
        }

    def __repr__(self) -> str:
        return f"Observable(name={self.name!r}, source={self.source!r})"

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)
