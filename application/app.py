from datetime import datetime, timezone
from typing import List

from application.ports.i_repository import IRepository
from domain import (
    RangeDomain, EnumerationDomain,
    Event, Model, Object, Observable,
    PlotData, Property, Record,
    Stats, StatsAnalyzer,
    Variable, VariableData,
)


class App:

    def __init__(self, repository: IRepository):
        self.repository : IRepository      = repository
        self.observables: List[Observable] = self.repository.load_observables()
        self.events     : List[Event]      = self.repository.load_events()
        self.model      : Model            = Model(self.events)

    def new_observable(self, name: str, source: str):
        obs = Observable(name=name, source=source)
        self.observables.append(obs)
        self.repository.save_observables(self.observables)

    def new_event(self):
        time = datetime.now(timezone.utc)
        records: List[Record] = []
        for observable in self.observables:
            state: List[Property] = observable.fetch_state()
            record = Record(observable.name, state)
            records.append(record)

        event = Event(records, time)
        events = self.repository.load_events()
        events.append(event)
        self.repository.save_events(events)

    def list_observables(self) -> List[Observable]:
        return self.observables

    def list_objects(self) -> List[Object]:
        objects = self.model.objects
        return objects

    def list_variables(self, object_name: str) -> List[Variable]:
        obj = next(item for item in self.model.objects if item.name == object_name)
        variables = list(obj.variables.values())
        return variables

    def compute_stats_within_range(self, object_name: str, variable_name: str, domain_min, domain_max) -> Stats:
        obj = next(item for item in self.model.objects if item.name == object_name)
        domain = RangeDomain(domain_min, domain_max)
        variable = obj.variables.get(variable_name)
        stats = StatsAnalyzer.compute(variable, domain)
        return stats

    def compute_stats_for_values(self, object_name: str, variable_name: str) -> Stats:
        obj = next(item for item in self.model.objects if item.name == object_name)
        variable = obj.variables[variable_name]
        known_values = variable.data.all_values()
        domain = EnumerationDomain(known_values)
        stats = StatsAnalyzer.compute(variable, domain)
        return stats

    def get_variable_data(self, object_name: str, variable_name: str) -> VariableData:
        obj = next(item for item in self.model.objects if item.name == object_name)
        variable = obj.variables[variable_name]
        data = variable.data
        return data

    def get_plot_data(self, object_name: str, variable_name: str, plot_type: str) -> PlotData:
        obj = next(item for item in self.model.objects if item.name == object_name)
        variable = obj.variables[variable_name]
        variable_data = variable.data

        # Extract values from the data
        values = list(variable_data.values())

        # Decide if values are numeric (all values must be numeric)
        from numbers import Number
        is_all_numeric = bool(values) and all(isinstance(v, Number) for v in values)

        # Choose stats computation
        if is_all_numeric:
            # Use numeric min/max from the numeric values
            numeric_vals = [v for v in values if isinstance(v, Number)]
            stats = self.compute_stats_within_range(
                object_name, variable_name,
                min(numeric_vals), max(numeric_vals)
            )
        else:
            stats = self.compute_stats_for_values(object_name, variable_name)

        if plot_type == "time series":
            # X is timestamps, Y is values
            x = list(variable_data.keys())
            y = list(variable_data.values())
            title = f"Time Series for {variable_name}"
            subtitle = f"{object_name}"
            x_label = "Time"
            y_label = variable.name

        elif plot_type == "distribution":
            freq = getattr(stats, "frequencies", None) or {}

            if not freq:
                # Build frequencies safely (handle unhashable items by stringifying)
                freq = {}
                for v in values:
                    try:
                        freq[v] = freq.get(v, 0) + 1
                    except TypeError:
                        key = str(v)
                        freq[key] = freq.get(key, 0) + 1

            # Build axes from the frequencies
            # Prefer a stable, readable order: try by key; if mixed types, fall back to frequency desc
            try:
                x = sorted(freq.keys())  # categories
                y = [freq[k] for k in x]  # counts
            except TypeError:
                items = sorted(freq.items(), key=lambda kv: (-kv[1], str(kv[0])))
                x = [k for k, _ in items]
                y = [v for _, v in items]

            title = f"Distribution of {variable_name}"
            subtitle = f"{object_name}"
            x_label = variable.name
            y_label = "Frequency"

        else:
            raise ValueError(f"Unsupported plot_type: {plot_type}")

        return PlotData(
            object_name=object_name,
            variable_name=variable_name,
            plot_type=plot_type,
            x=x,
            y=y,
            title=title,
            subtitle=subtitle,
            x_label=x_label,
            y_label=y_label,
            stats=stats,
        )

    @staticmethod
    def cli_help() -> str:
        """Prints an organized description of how to use the CLI interface."""

        help_text = """
=====================================================
                Observables CLI Help
=====================================================

Available Commands:

- new-observable <observable_name> <source>
   - Creates a new observable with the given name and source.
   - Example: new-observable temperature ./data/temp.json

- list-observables
   - Lists all registered observables.

- list-objects
   - Lists all objects currently in the model.

- list-variables <object_name>
   - Lists all variables for the specified object.
   - Example: list-variables temperature_sensor

- new-event <observable_name> <var1=value1> <var2=value2> ...
   - Creates a new event for the specified observable with variable assignments.
   - Example: new-event temperature value=22.5 timestamp=2025-08-31T12:00

- compute-stats-range <object_name> <variable_name> <domain_min> <domain_max>
   - Computes statistics for a variable within a numeric range.
   - Example: compute-stats-range temperature value 10 30

- compute-stats-values <object_name> <variable_name>
   - Computes statistics for a variable across all observed values.
   - Example: compute-stats-values climate temperature
   
- get-variable-data <object_name> <variable_name>
   - Retrieve the data for a given variable of an object.
   - Example: get-plot-data economics cash

- get-plot-data <object_name> <variable_name> <plot_type>
   - Retrieve data for a given variable of an object, suitable for plotting.
   - Supported plot types: 'time_series', 'distribution'
   - Example: get-plot-data temperature value time_series

- help
   - Displays this help message.

=====================================================
    """
        return help_text

