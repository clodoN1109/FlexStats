import tkinter as tk
from typing import List
from application.app import App
from infrastructure.environment.environment import Env
from interface.GUI.gui_renderer import GUIRenderer
from interface.GUI.gui_styles import GUIStyle


class TkinterGUI(tk.Tk):
    """GUI application to visualize object variable data and statistics."""

    def __init__(self, app: App, settings: List[str]) -> None:
        super().__init__()
        self.app = app
        self.model = app.model
        self.gui_path = Env.get_script_path()
        self.style = GUIStyle("dark")

        renderer = GUIRenderer(self)
        renderer.config_window_navbar()
        renderer.font("courier", 10)
        renderer.window("flexstats", "1000x600")
        renderer.panes()
        renderer.refresh_objects()



