from interface.CLI.input.cli_controller import CLIController
from interface.CLI.input.cli_preprocessor import InputPreProcessor


class Router:

    @staticmethod
    def execute(args):

        preprocessed_args = [InputPreProcessor.normalize(option) for option in args[1:]]

        if preprocessed_args[0] == "gui":
            print(f"Routing to GUI.")
        else:
            CLIController.execute(preprocessed_args)
