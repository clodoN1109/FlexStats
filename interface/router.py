from application.app import App
from infrastructure.persistence.json_repository import JsonRepository
from interface.CLI.input.cli_controller import CLIController
from interface.CLI.input.cli_preprocessor import InputPreProcessor
from interface.GUI.gui_launcher import GUILauncher


class Router:

    @staticmethod
    def execute(args):

        preprocessed_args = [InputPreProcessor.normalize(option) for option in args[1:]]

        if preprocessed_args[0] == "gui":
            print(f"Routing to GUI.")
            gui = GUILauncher()
            gui.prepare(App(JsonRepository()), preprocessed_args[1:])
            gui.launch()
        else:
            CLIController.execute(preprocessed_args)
