import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from typing import List
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from domain import Object, Variable
from domain.plot import PlotData
import matplotlib.dates as mdates

class GUIRenderer:

    def __init__(self, gui):
        self.gui = gui
        self.style = gui.style
        self.section_items_padding_x = 10
        self.section_items_padding_y = 0
        self.button_padding = 10

        # Apply base style early so style names exist before widgets are created
        # (apply_style is safe to call — it checks for widget existence)
        self.apply_style()

    def config_window_navbar(self):
        # Keep using the gui_path from the GUI instance
        try:
            self.gui.iconphoto(False, tk.PhotoImage(file=f"{self.gui.gui_path}/icon.png"))
        except Exception:
            # If icon not found or fails, ignore (non-fatal)
            pass

    def apply_style(self):
        """
        Apply a Style object to ttk widgets and other UI elements.
        Safe to call multiple times; it updates existing elements if present.
        """
        # Create/use ttk style object tied to root
        self.gui.style = ttk.Style(self.gui)
        self.gui.style.theme_use("clam")  # safe base theme that reacts to configure()

        # --- Basic widget styles (frames, labels, buttons, combobox entry) ---
        self.gui.style.configure(f"{self.style.prefix}.TFrame", background=self.style.primary_bg)
        self.gui.style.configure(
            f"{self.style.prefix}.TLabel",
            background=self.style.primary_bg,
            foreground=self.style.primary_fg,
        )
        self.gui.style.configure(
            f"{self.style.prefix}.TButton",
            background=self.style.accent_bg,
            foreground=self.style.primary_fg,
        )
        # hover/active for buttons
        self.gui.style.map(
            f"{self.style.prefix}.TButton",
            background=[("active", self.style.accent_hover)],
            foreground=[("active", self.style.primary_fg)],
        )
        # Combobox entry field (the visible entry area)
        self.gui.style.configure(
            f"{self.style.prefix}.TCombobox",
            fieldbackground=self.style.accent_bg,
            foreground=self.style.primary_fg,
        )

        # --- Combobox dropdown (listbox) colors ---
        # Important: the combobox popdown is a Listbox in a Toplevel; we set
        # option database entries to ensure the list uses readable colors.
        # For dark mode we make the dropdown list light (inverted) with dark text.
        if self.style.prefix == "Dark":
            list_bg = "#f5f5f5"  # popup background
            list_fg = "#1e1e1e"  # popup text
            sel_bg = self.style.semantic_info
            sel_fg = self.style.primary_bg
            field_bg = "#e2e2e2"  # entry background
            field_fg = "#323232"  # entry foreground
        elif self.style.prefix == "Light":
            list_bg = "#f2c55c"
            list_fg = self.style.primary_fg
            sel_bg = self.style.semantic_info
            sel_fg = self.style.primary_bg
            field_bg = "#f2c55c"
            field_fg = "#323232"
        else:
            list_bg = "#f2c55c"
            list_fg = self.style.primary_fg
            sel_bg = self.style.semantic_info
            sel_fg = self.style.primary_bg
            field_bg = "#f2c55c"
            field_fg = "#323232"

        # Configure the dropdown popup (listbox)
        self.gui.option_add("*TCombobox*Listbox.background", list_bg)
        self.gui.option_add("*TCombobox*Listbox.foreground", list_fg)
        self.gui.option_add("*TCombobox*Listbox.selectBackground", sel_bg)
        self.gui.option_add("*TCombobox*Listbox.selectForeground", sel_fg)

        # Configure the entry field (what shows when dropdown is closed)
        self.gui.style.configure(
            f"{self.style.prefix}.TCombobox",
            fieldbackground=field_bg,
            foreground=field_fg,
            background=field_bg,
        )

        # --- Separator style: keep invisible/subtle (do not change with heavy visuals) ---
        # We intentionally do NOT draw bold separators; keep them subtle or match bg.
        # The widget code uses frame separators that already match primary_bg.
        self.gui.style.configure(f"{self.style.prefix}.TSeparator", background=self.style.primary_bg)

        # --- Text areas (non-ttk widgets: Text) ---
        # If stats_text exists already, update its colors
        if hasattr(self.gui, "stats_text") and isinstance(self.gui.stats_text, tk.Text):
            self.gui.stats_text.configure(
                bg=self.style.text_bg,
                fg=self.style.text_fg,
                insertbackground=self.style.text_fg,
            )

        # --- Plot styling ---
        # If the plot (matplotlib) exists already on the GUI, update colors
        if hasattr(self.gui, "ax") and hasattr(self.gui, "fig"):
            self.gui.fig.set_facecolor(self.style.primary_bg)
            self.gui.ax.set_facecolor(self.style.text_bg)
            # ticks and labels
            self.gui.ax.tick_params(colors=self.style.primary_fg)
            self.gui.ax.xaxis.label.set_color(self.style.primary_fg)
            self.gui.ax.yaxis.label.set_color(self.style.primary_fg)
            self.gui.ax.title.set_color(self.style.primary_fg)
            # grid
            self.gui.ax.grid(color=self.style.grid_color, linestyle="--", linewidth=0.5)

            # if canvas exists, schedule redraw
            if hasattr(self.gui, "canvas"):
                try:
                    self.gui.canvas.draw_idle()
                except Exception:
                    pass

    def window(self, title: str, resolution: str = "1000x600"):
        self.gui.title(title)
        self.gui.geometry(resolution)
        # set the background of the root window
        self.gui.configure(bg=self.style.primary_bg)

    def font(self, font_family, size):
        self.gui.default_font = tkFont.Font(family=font_family, size=size)
        self.gui.option_add("*Font", self.gui.default_font)

    def section_separator(self, section_title: str):
        # Use the active theme label style (no hardcoded Light/other)
        ttk.Label(
            self.gui.left_frame,
            text=f"{section_title}",
            style=f"{self.style.prefix}.TLabel",
            anchor="center",
            justify="center",
            background=self.style.accent_bg,
        ).pack(fill="x", padx=0, pady=(10, 10))

        # Intentionally do NOT add a visible ttk.Separator here — you asked separators stay invisible.

    def section_item_separator(self):
        # invisible spacer that matches the primary background
        tk.Frame(self.gui.left_frame, height=10, background=self.style.primary_bg).pack(fill="x", pady=2)

    def left_pane(self, container):
        self.gui.left_frame = ttk.Frame(
            container, width=250, relief=tk.RAISED, style=f"{self.style.prefix}.TFrame", padding=2
        )
        container.add(self.gui.left_frame, weight=1)

        # --- Model Section ---
        self.section_separator("MODEL")

        ttk.Label(
            self.gui.left_frame,
            text="objects",
            style=f"{self.style.prefix}.TLabel",
        ).pack(anchor="w", padx=self.section_items_padding_x, pady=self.section_items_padding_y)

        # IMPORTANT: create StringVar with explicit master to avoid tkinter context issues
        self.gui.obj_var = tk.StringVar(master=self.gui)
        self.gui.obj_cb = ttk.Combobox(
            self.gui.left_frame,
            textvariable=self.gui.obj_var,
            state="readonly",
            style=f"{self.style.prefix}.TCombobox",
        )
        self.gui.obj_cb.pack(fill="x", padx=self.section_items_padding_x, pady=self.section_items_padding_y)
        self.section_item_separator()

        ttk.Label(
            self.gui.left_frame,
            text="variables",
            style=f"{self.style.prefix}.TLabel",
        ).pack(anchor="w", padx=self.section_items_padding_x, pady=self.section_items_padding_y)

        self.gui.var_var = tk.StringVar(master=self.gui)
        self.gui.var_cb = ttk.Combobox(
            self.gui.left_frame,
            textvariable=self.gui.var_var,
            state="readonly",
            style=f"{self.style.prefix}.TCombobox",
        )
        self.gui.var_cb.pack(fill="x", padx=self.section_items_padding_x, pady=self.section_items_padding_y)

        # --- Statistics Section ---
        self.section_separator("STATISTICS")

        ttk.Label(self.gui.left_frame, text="plots", style=f"{self.style.prefix}.TLabel").pack(
            anchor="w", padx=self.section_items_padding_x, pady=2
        )

        self.gui.plot_var = tk.StringVar(master=self.gui, value="time_series")
        self.gui.plot_cb = ttk.Combobox(
            self.gui.left_frame,
            textvariable=self.gui.plot_var,
            state="readonly",
            style=f"{self.style.prefix}.TCombobox",
        )
        self.gui.plot_cb["values"] = ["time_series", "distribution"]
        self.gui.plot_cb.pack(fill="x", padx=self.section_items_padding_x, pady=self.section_items_padding_y)

        # Button aligned to right
        btn_frame = ttk.Frame(self.gui.left_frame, style=f"{self.style.prefix}.TFrame")
        btn_frame.pack(fill="x", padx=self.section_items_padding_x, pady=(self.button_padding, 0))

        ttk.Button(
            btn_frame, text="Plot", command=self.plot_selected_data, style=f"{self.style.prefix}.TButton"
        ).pack(anchor="e")

        # --- Simulations Section ---
        self.section_separator("SIMULATIONS")

    def right_pane(self, container):
        self.gui.right_frame = ttk.Frame(container, style=f"{self.style.prefix}.TFrame")
        container.add(self.gui.right_frame, weight=4)

        # Plot area
        self.gui.fig = Figure(
            figsize=(5, 4), dpi=100, facecolor=self.style.accent_bg, edgecolor=self.style.text_fg
        )
        self.gui.ax = self.gui.fig.add_subplot(111)

        # Apply plot colors
        self.gui.ax.set_facecolor(self.style.text_bg)
        self.gui.ax.tick_params(colors=self.style.primary_fg)
        self.gui.ax.xaxis.label.set_color(self.style.primary_fg)
        self.gui.ax.yaxis.label.set_color(self.style.primary_fg)
        self.gui.ax.title.set_color(self.style.primary_fg)
        self.gui.ax.grid(color=self.style.grid_color, linestyle="--", linewidth=0.5)

        self.gui.canvas = FigureCanvasTkAgg(self.gui.fig, master=self.gui.right_frame)
        self.gui.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Stats area (read-only)
        self.gui.stats_text = tk.Text(
            self.gui.right_frame,
            height=2,
            bg=self.style.text_bg,
            fg=self.style.text_fg,
            insertbackground=self.style.text_fg,
        )
        self.gui.stats_text.pack(fill="x", padx=100, pady=30)
        self.gui.stats_text.configure(state="disabled")

    def panes(self):
        container = ttk.PanedWindow(orient=tk.HORIZONTAL)
        container.pack(fill=tk.BOTH, expand=True)
        self.left_pane(container)
        self.right_pane(container)

    def refresh_objects(self):
        objects: List[Object] = self.gui.app.list_objects()
        self.gui.obj_cb["values"] = [obj.name for obj in objects]
        if objects:
            self.gui.obj_var.set(objects[0].name)
            self.refresh_variables()

        self.gui.obj_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_variables())

    def refresh_variables(self):
        obj_name = self.gui.obj_var.get()
        if not obj_name:
            return
        variables: List[Variable] = self.gui.app.list_variables(obj_name)
        self.gui.var_cb["values"] = [var.name for var in variables]
        if variables:
            self.gui.var_var.set(variables[0].name)

    def plot_selected_data(self):
        obj_name = self.gui.obj_var.get()
        var_name = self.gui.var_var.get()
        plot_type = self.gui.plot_var.get()
        if not (obj_name and var_name and plot_type):
            return

        # Use application layer to get PlotData
        plot_data: PlotData = self.gui.app.get_plot_data(obj_name, var_name, plot_type)
        # Clear previous plot
        self.gui.ax.clear()

        # Plot x vs y
        if plot_data.plot_type == "time_series":
            self.gui.ax.plot(plot_data.x, plot_data.y, marker="o")

            # Format x-axis as MM/DD/YYYY and show hours:minutes
            self.gui.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y\n%H:%M'))
            self.gui.fig.autofmt_xdate()  # rotates and aligns dates nicely
        else:
            self.gui.ax.bar(plot_data.x, plot_data.y)

        self.gui.ax.set_title(plot_data.title.upper(), color=self.style.primary_fg)
        if plot_data.subtitle:
            self.gui.ax.set_title(plot_data.subtitle, fontsize=10, loc="right", color=self.style.primary_fg)
        self.gui.ax.set_xlabel(plot_data.x_label.upper(), color=self.style.primary_fg)
        self.gui.ax.set_ylabel(plot_data.y_label.upper(), color=self.style.primary_fg)

        self.gui.canvas.draw()

        def display_stats_table(stats):
            """Display stats in a tabular format in the stats_text widget."""
            if not stats:
                return

            # Enable the Text widget temporarily
            self.gui.stats_text.configure(state="normal")
            self.gui.stats_text.delete("1.0", tk.END)

            # Filter out None values
            stats_dict = {k: v for k, v in vars(stats).items() if v is not None}

            if not stats_dict:
                self.gui.stats_text.insert(tk.END, "No statistics available.\n")
                self.gui.stats_text.configure(state="disabled")
                return

            # Determine column widths
            col_widths = {k: max(len(k), len(str(v))) for k, v in stats_dict.items()}

            # Header row
            header = " " + " │ ".join(f"{k:>{col_widths[k]}}" for k in stats_dict.keys()) + " │ "
            self.gui.stats_text.insert(tk.END, header + "\n")

            # Values row
            values = " " + " │ ".join(f"{str(v):>{col_widths[k]}}" for k, v in stats_dict.items()) + " │ "
            self.gui.stats_text.insert(tk.END, values + "\n")

            # Disable again
            self.gui.stats_text.configure(state="disabled")
        # Show stats in text
        if plot_data.stats:
            display_stats_table(plot_data.stats)