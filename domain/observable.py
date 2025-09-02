from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
from typing import List
import json
import requests

from domain.property import Property


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
        try:
            if self.is_url:
                response = requests.get(self.source, timeout=5)
                response.raise_for_status()
                raw_data = response.json()
            elif self.is_local:
                with open(self.source, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            else:
                raise ValueError(f"Invalid source path or URL: {self.source}")

            if isinstance(raw_data, dict):
                return [Property(name=k, value=v) for k, v in raw_data.items()]
            elif isinstance(raw_data, list):
                # if it's already list of dicts {name, value}
                props = []
                for item in raw_data:
                    if isinstance(item, dict) and "name" in item and "value" in item:
                        props.append(Property(name=item["name"], value=item["value"]))
                return props
            else:
                return []

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
