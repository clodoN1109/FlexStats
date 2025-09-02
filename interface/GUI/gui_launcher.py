from application.app import App
from interface.GUI.gui_app import TkinterGUI


from typing import List

class GUILauncher:

    def __init__(self):
        self.app = None
        self.settings: List[str] = []

    def prepare(self, app: App, preprocessed_args: List[str]) -> None:
        self.app = app
        self.settings = preprocessed_args[1:]

    def launch(self):
        gui = TkinterGUI(self.app, self.settings)
        gui.mainloop()