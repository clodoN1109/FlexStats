from dataclasses import dataclass
from typing import List


@dataclass
class Command:
    """Base class for CLI commands."""
    name: str
    args: List[str]


@dataclass
class NewObservableCommand(Command):
    observable_name: str
    source: str

    @classmethod
    def command_name(cls) -> str:
        return "new-observable"

    @classmethod
    def __init__(cls, args: list[str]):
        cls.name = cls.command_name()
        cls.args = args
        cls.observable_name = args[0]
        cls.source = args[1]


@dataclass
class ListObservablesCommand(Command):

    @classmethod
    def command_name(cls) -> str:
        return "list-observables"

    @classmethod
    def __init__(cls, args: list[str]):
        cls.name = cls.command_name()
        cls.args = args

@dataclass
class ListObjectsCommand(Command):

    @classmethod
    def command_name(cls) -> str:
        return "list-objects"

    @classmethod
    def __init__(cls, args: list[str]):
        cls.name = cls.command_name()
        cls.args = args

@dataclass
class ListVariablesCommand(Command):

    @classmethod
    def command_name(cls) -> str:
        return "list-variables"

    @classmethod
    def __init__(cls, args: list[str]):
        cls.name = cls.command_name()
        cls.args = args
        cls.object_name = args[0]

@dataclass
class NewEventCommand(Command):

    @classmethod
    def command_name(cls) -> str:
        return "new-event"

    @classmethod
    def __init__(cls, args: list[str]):
        cls.name = cls.command_name()
        cls.args = args

@dataclass
class ComputeStatsWithinRangeCommand(Command):
    def __init__(self, args: list[str]):
        self.name = self.command_name()
        self.args = args
        self.object_name = args[0]
        self.variable_name = args[1]
        self.domain_min = float(args[2])
        self.domain_max = float(args[3])

    @classmethod
    def command_name(cls) -> str:
        return "compute-stats-range"


class ComputeStatsForValuesCommand(Command):
    def __init__(self, args: list[str]):
        self.name = self.command_name()
        self.args = args
        self.object_name = args[0]
        self.variable_name = args[1]

    @classmethod
    def command_name(cls) -> str:
        return "compute-stats-values"

class GetVariableDataCommand(Command):
    def __init__(self, args: list[str]):
        self.name = self.command_name()
        self.args = args
        self.object_name = args[0]
        self.variable_name = args[1]

    @classmethod
    def command_name(cls) -> str:
        return "get-variable-data"

class GetPlotDataCommand(Command):
    def __init__(self, args: list[str]):
        self.name = self.command_name()
        self.args = args
        self.object_name = args[0]
        self.variable_name = args[1]
        self.plot_type = args[2]

    @classmethod
    def command_name(cls) -> str:
        return "get-plot-data"

@dataclass
class CLIHelpCommand(Command):

    @classmethod
    def command_name(cls) -> str:
        return "help"

    @classmethod
    def __init__(cls, args: list[str]):
        cls.name = cls.command_name()
        cls.args = args