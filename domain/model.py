from typing import List, Dict
from domain.event import Event
from domain.object import Object
from domain.variable import Variable


class Model:
    def __init__(self, events: List[Event]):
        self.objects: List[Object] = self._abstract_objects(events)

    @staticmethod
    def _abstract_objects(events: List[Event]) -> List[Object]:
        objects_map: Dict[str, Object] = {}

        for event in events:
            for record in event.records:
                # ensure observable object exists
                if record.observable not in objects_map:
                    objects_map[record.observable] = Object(name=record.observable)

                obj = objects_map[record.observable]

                # for each property in the record, add/update variable
                for prop in record.state:
                    if prop.name not in obj.variables:
                        obj.variables[prop.name] = Variable(name=prop.name)

                    # store value in variable’s time series at record timestamp
                    obj.variables[prop.name].data[event.timestamp] = prop.value

        return list(objects_map.values())

    def __str__(self) -> str:
        lines = []
        for obj in self.objects:
            lines.append(f"Observable: {obj.name}")
            for var_name, var in obj.variables.items():
                # display first few entries for brevity
                values_preview = ", ".join(
                    f"{ts}: {val}" for ts, val in list(var.data.items())[:5]
                )
                if len(var.data) > 5:
                    values_preview += ", ..."
                lines.append(f"  Variable: {var_name} -> {values_preview}")
        return "\n".join(lines)