from interface.CLI.input.commands import *


class CLIParser:
    @staticmethod
    def parse_as_command(command_name: str, args: List[str]) -> Command:
        return {
            "help"                  : CLIHelpCommand,
            "new-observable"        : NewObservableCommand,
            "list-observables"      : ListObservablesCommand,
            "list-objects"          : ListObjectsCommand,
            "list-variables"        : ListVariablesCommand,
            "list-scripts"          : ListScriptsCommand,
            "new-event"             : NewEventCommand,
            "compute-stats-range"   : ComputeStatsWithinRangeCommand,
            "compute-stats-values"  : ComputeStatsForValuesCommand,
            "get-variable-data"     : GetVariableDataCommand,
            "get-plot-data"         : GetPlotDataCommand
        }[command_name](args)