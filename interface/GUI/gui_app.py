import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from typing import List
from application.app import App
from domain import Object, Variable
from domain.plot import PlotData


class TkinterGUI(tk.Tk):
    """GUI application to visualize object variable data and statistics."""

    def __init__(self, app: App, settings: List[str]) -> None:
        super().__init__()
        self.app = app
        self.model = app.model

        # --- Window ---
        self.title("flexstats")
        self.geometry("1000x600")
        self.configure(bg="#2e2e2e")

        # --- Styles for dark mode ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # safer for custom colors

        self.style.configure("Dark.TFrame", background="#2e2e2e")
        self.style.configure("Dark.TLabel", background="#2e2e2e", foreground="#f5f5f5")
        self.style.configure("Dark.TButton", background="#3e3e3e", foreground="#f5f5f5")
        self.style.configure("Dark.TCombobox",
                             fieldbackground="#3e3e3e",
                             background="#2e2e2e",
                             foreground="#f5f5f5")

        # Layout: 2 main panes
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # --- Left control pane ---
        self.left_frame = ttk.Frame(paned, width=250, relief=tk.RAISED, style="Dark.TFrame", padding=2)
        paned.add(self.left_frame, weight=1)

        # Object dropdown
        ttk.Label(self.left_frame, text="object", style="Dark.TLabel").pack(anchor="w", padx=5, pady=2)
        self.obj_var = tk.StringVar()
        self.obj_cb = ttk.Combobox(self.left_frame, textvariable=self.obj_var, state="readonly", style="Light.TCombobox")
        self.obj_cb.pack(fill="x", padx=5, pady=2)

        # Variable dropdown
        ttk.Label(self.left_frame, text="variable", style="Dark.TLabel").pack(anchor="w", padx=5, pady=2)
        self.var_var = tk.StringVar()
        self.var_cb = ttk.Combobox(self.left_frame, textvariable=self.var_var, state="readonly", style="Light.TCombobox")
        self.var_cb.pack(fill="x", padx=5, pady=2)

        # Plot type dropdown
        ttk.Label(self.left_frame, text="plot type", style="Dark.TLabel").pack(anchor="w", padx=5, pady=2)
        self.plot_var = tk.StringVar(value="time_series")
        self.plot_cb = ttk.Combobox(self.left_frame, textvariable=self.plot_var, state="readonly", style="Light.TCombobox")
        self.plot_cb["values"] = ["time_series", "distribution"]
        self.plot_cb.pack(fill="x", padx=5, pady=2)

        ttk.Button(self.left_frame, text="Plot", command=self.plot_selected_data, style="Dark.TButton").pack(pady=10)

        # --- Right pane: plot + stats ---
        self.right_frame = ttk.Frame(paned, style="Dark.TFrame")
        paned.add(self.right_frame, weight=4)

        # Plot area
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor="#2e2e2e", edgecolor="#2e2e2e")
        self.ax = self.fig.add_subplot(111)

        # Dark background for the axes
        self.ax.set_facecolor("#1e1e1e")

        # Light-colored ticks
        self.ax.tick_params(colors="#f5f5f5")  # tick labels and lines

        # Light-colored axis labels and title
        self.ax.xaxis.label.set_color("#f5f5f5")  # X axis label
        self.ax.yaxis.label.set_color("#f5f5f5")  # Y axis label
        self.ax.title.set_color("#f5f5f5")  # Plot title

        # Optional: make grid lines a bit lighter but subtle
        self.ax.grid(color="#444444", linestyle="--", linewidth=0.5)

        # Create the canvas in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Stats area (read-only)
        self.stats_text = tk.Text(self.right_frame, height=2, bg="#1e1e1e", fg="#f5f5f5", insertbackground="#f5f5f5")
        self.stats_text.pack(fill="x", padx=140, pady=30)
        self.stats_text.configure(state="disabled")  # keep disabled, enable only when updating

        # Load initial object list
        self.refresh_objects()

    def refresh_objects(self):
        objects: List[Object] = self.app.list_objects()
        self.obj_cb["values"] = [obj.name for obj in objects]
        if objects:
            self.obj_var.set(objects[0].name)
            self.refresh_variables()

        self.obj_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_variables())

    def refresh_variables(self):
        obj_name = self.obj_var.get()
        if not obj_name:
            return
        variables: List[Variable] = self.app.list_variables(obj_name)
        self.var_cb["values"] = [var.name for var in variables]
        if variables:
            self.var_var.set(variables[0].name)

    def plot_selected_data(self):
        obj_name = self.obj_var.get()
        var_name = self.var_var.get()
        plot_type = self.plot_var.get()
        if not (obj_name and var_name and plot_type):
            return

        # Use application layer to get PlotData
        plot_data: PlotData = self.app.get_plot_data(obj_name, var_name, plot_type)
        # Clear previous plot
        self.ax.clear()

        # Plot x vs y
        if plot_data.plot_type == "time_series":
            self.ax.plot(plot_data.x, plot_data.y, marker="o")

            # Format x-axis as MM/DD/YYYY and show hours:minutes
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y\n%H:%M'))
            self.fig.autofmt_xdate()  # rotates and aligns dates nicely
        else:
            self.ax.bar(plot_data.x, plot_data.y)

        self.ax.set_title(plot_data.title, color="#f5f5f5")
        if plot_data.subtitle:
            self.ax.set_title(plot_data.subtitle, fontsize=10, loc="right", color="#f5f5f5")
        self.ax.set_xlabel(plot_data.x_label, color="#f5f5f5")
        self.ax.set_ylabel(plot_data.y_label, color="#f5f5f5")

        self.canvas.draw()

        def display_stats_table(stats):
            """Display stats in a tabular format in the stats_text widget."""
            if not stats:
                return

            # Enable the Text widget temporarily
            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", tk.END)

            # Filter out None values
            stats_dict = {k: v for k, v in vars(stats).items() if v is not None}

            if not stats_dict:
                self.stats_text.insert(tk.END, "No statistics available.\n")
                self.stats_text.configure(state="disabled")
                return

            # Determine column widths
            col_widths = {k: max(len(k), len(str(v))) for k, v in stats_dict.items()}

            # Header row
            header = " " + " │ ".join(f"{k:>{col_widths[k]}}" for k in stats_dict.keys()) + " │ "
            self.stats_text.insert(tk.END, header + "\n")

            # Values row
            values = " " + " │ ".join(f"{str(v):>{col_widths[k]}}" for k, v in stats_dict.items()) + " │ "
            self.stats_text.insert(tk.END, values + "\n")

            # Disable again
            self.stats_text.configure(state="disabled")
        # Show stats in text
        if plot_data.stats:
            display_stats_table(plot_data.stats)


