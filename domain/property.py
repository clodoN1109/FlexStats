from __future__ import annotations
from typing import Union


class Property:
    def __init__(self, name: str, value: Union[str, int, float]):
        self.name = name
        self.value = value

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict) -> Property:
        return cls(name=data["name"], value=data["value"])
