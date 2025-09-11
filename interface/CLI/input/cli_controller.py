from application.app import App
from interface.CLI.input.cli_parser import CLIParser
from interface.CLI.input.commands import *
from infrastructure.persistence.json_repository import JsonRepository


class CLIController:
    @staticmethod
    def execute(args: List[str]):

        command_name = args[0]
        options = args[1:]
        cmd = CLIParser.parse_as_command(command_name, options)

        app = App(JsonRepository())

        if isinstance(cmd, CLIHelpCommand):
            cli_help_instructions = app.cli_help()
            print(cli_help_instructions)

        if isinstance(cmd, NewObservableCommand):
            app.new_observable(cmd.observable_name, cmd.source)

        if isinstance(cmd, ListObservablesCommand):
            print(app.list_observables())

        if isinstance(cmd, ListObjectsCommand):
            print(app.list_objects())

        if isinstance(cmd, ListScriptsCommand):
            print(app.list_scripts())

        if isinstance(cmd, ListVariablesCommand):
            print(app.list_variables(cmd.object_name))

        if isinstance(cmd, NewEventCommand):
            app.new_event()

        if isinstance(cmd, ComputeStatsWithinRangeCommand):
            app.compute_stats_within_range(
                cmd.object_name,
                cmd.variable_name,
                cmd.domain_min,
                cmd.domain_max
            )

        if isinstance(cmd, ComputeStatsForValuesCommand):
            app.compute_stats_for_values(
                cmd.object_name,
                cmd.variable_name
            )

        if isinstance(cmd, GetVariableDataCommand):
            variable_data = app.get_variable_data(
                cmd.object_name,
                cmd.variable_name
            )
            print(variable_data)

        if isinstance(cmd, GetPlotDataCommand):
            obj = next(item for item in app.model.objects if item.name == cmd.object_name)
            variable = obj.variables[cmd.variable_name]
            variable_data = variable.data

            plot_data = app.get_plot_data(
                cmd.object_name,
                cmd.variable_name,
                cmd.plot_type,
                variable_data
            )
            print(plot_data)
