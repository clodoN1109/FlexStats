import math
import os
from typing import List, Dict
import datetime
import numpy as np
from application.ports.i_repository import IRepository
from domain import (
    RangeDomain, EnumerationDomain,
    Event, Model, Object, Observable,
    PlotData, Property, Record,
    Stats, StatsAnalyzer,
    Variable, VariableData,
)
from domain.domain import ValueType
from domain.script import Script
from infrastructure.environment.environment import Env


class App:

    def __init__(self, repository: IRepository):
        self.repository : IRepository      = repository
        self.observables: List[Observable] = self.repository.load_observables()
        self.events     : List[Event]      = self.repository.load_events()
        self.model      : Model            = Model(self.events)

    def update_repository(self, repository: IRepository):
        self.repository: IRepository = repository
        self.observables: List[Observable] = self.repository.load_observables()
        self.events: List[Event] = self.repository.load_events()
        self.model: Model = Model(self.events)

    def new_observable(self, name: str, source: str):
        obs = Observable(name=name, source=source)
        self.observables.append(obs)
        self.repository.save_observables(self.observables)

    def new_event(self):
        time = datetime.datetime.now(datetime.timezone.utc)
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

    @staticmethod
    def list_scripts() -> List[Script]:
        scripts_path = Env.get_scripts_dir()

        allowed_exts = {".py", ".ps1", ".sh", ".bat", ".rb"}
        scripts: List[Script] = []

        if not os.path.isdir(scripts_path):
            return scripts

        for fname in os.listdir(scripts_path):
            fpath = os.path.join(scripts_path, fname)
            if not os.path.isfile(fpath):
                continue

            name, ext = os.path.splitext(fname)
            if ext.lower() in allowed_exts:
                scripts.append(Script(name, ext.lower(), fpath))

        return scripts


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

    def compute_extrapolation(
            self,
            object_name: str,
            variable_name: str,
            x_min=None,
            x_max=None,
            precision: int = 86400,  # in seconds
            method: str = "linear"
    ):

        obj = next(item for item in self.model.objects if item.name == object_name)
        variable = obj.variables[variable_name]
        x = list(variable.data.keys())
        y = list(variable.data.values())

        if not x or not y:
            return {}

        # --- Normalize x_min and x_max ---
        # They may already be datetime objects (from DateEntry) or None
        if isinstance(x_min, str) and x_min.strip():
            x_min_dt = datetime.datetime.strptime(x_min, "%m-%d-%Y")
        elif isinstance(x_min, datetime.datetime):
            x_min_dt = x_min
        else:
            x_min_dt = min(x)

        if isinstance(x_max, str) and x_max.strip():
            x_max_dt = datetime.datetime.strptime(x_max, "%m-%d-%Y")
        elif isinstance(x_max, datetime.datetime):
            x_max_dt = x_max
        else:
            x_max_dt = max(x)

        # Align with tzinfo if needed
        if x and x[0].tzinfo is not None:
            if x_min_dt.tzinfo is None:
                x_min_dt = x_min_dt.replace(tzinfo=x[0].tzinfo)
            if x_max_dt.tzinfo is None:
                x_max_dt = x_max_dt.replace(tzinfo=x[0].tzinfo)

        # Ensure x_max_dt > x_min_dt
        if x_max_dt <= x_min_dt:
            x_max_dt = x_min_dt + datetime.timedelta(seconds=precision)

        # Build new_x using precision directly
        new_x = []
        current = x_min_dt
        while current <= x_max_dt:
            new_x.append(current)
            current += datetime.timedelta(seconds=precision)

        # Ensure last point is exactly x_max_dt
        if new_x[-1] != x_max_dt:
            new_x.append(x_max_dt)

        # Fit & extrapolate
        x_num = np.array([dt.timestamp() for dt in x])
        y_num = np.array(y)
        new_x_num = np.array([dt.timestamp() for dt in new_x])

        if method == "linear":
            coeffs = np.polyfit(x_num, y_num, 1)
        elif method == "quadratic":
            coeffs = np.polyfit(x_num, y_num, 2)
        else:
            raise ValueError(f"Unknown extrapolation method: {method}")

        poly = np.poly1d(coeffs)
        new_y = poly(new_x_num)

        return {dt: float(val) for dt, val in zip(new_x, new_y)}

    def get_extrapolation_plot_data(self,
                                    object_name: str,
                                    variable_name: str,
                                    method: str,
                                    x_min,
                                    x_max,
                                    precision: int = 86400):

        extrapolation_data = self.compute_extrapolation(
            object_name, variable_name, x_min, x_max, precision, method
        )
        return extrapolation_data

    def get_variable_data(self, object_name: str, variable_name: str) -> VariableData:
        obj = next(item for item in self.model.objects if item.name == object_name)
        variable = obj.variables[variable_name]
        data = variable.data
        return data

    def get_plot_data(self, object_name: str, variable_name: str, plot_type: str, variable_data: VariableData, y_resolution = 2) -> PlotData:
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
            y_label = variable_name

        elif plot_type == "distribution":

            freq: Dict[ValueType, int] = {}

            def apply_precision(v):
                if isinstance(v, (int, float)) and y_resolution is not None:
                    factor = 10 ** y_resolution
                    return math.floor(v * factor) / factor
                return v

            for v in values:
                try:
                    v_precise = apply_precision(v)
                    freq[v_precise] = freq.get(v_precise, 0) + 1
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
            x_label = variable_name
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

