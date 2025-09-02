from dataclasses import field, dataclass
from typing import Dict
from domain.variable import Variable


@dataclass
class Object:
    name: str
    variables: Dict[str, Variable] = field(default_factory=dict)