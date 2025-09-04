import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from typing import List
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from domain import Object, Variable
from domain.plot import PlotData
import matplotlib.dates as mdates

from interface.GUI.gui_styles import GUIStyle


class GUIRenderer:

    def __init__(self, gui):
        self.gui = gui
        self.style: GUIStyle = gui.style
        self.section_items_padding_x = 10
        self.section_items_padding_y = 0
        self.button_padding = 10
        self.apply_style()
        self._is_maximized = False


    def config_window_navbar(self):
        self.gui.overrideredirect(True)
        try:
            self.gui.iconphoto(False, tk.PhotoImage(file=f"{self.gui.gui_path}/assets/icon.png"))
        except Exception:
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
        # Base style
        self.gui.style.configure(
            f"{self.style.prefix}.TButton",
            background=self.style.accent_bg,
            foreground=self.style.primary_fg,
            borderwidth=1,
            relief="flat",
            focusthickness=0,
            focuscolor=self.style.accent_bg,
        )
        # State-specific overrides
        self.gui.style.map(
            f"{self.style.prefix}.TButton",
            background=[
                ("active", self.style.accent_bg),  # keep same background on hover
                ("pressed", self.style.accent_bg),  # no inversion
            ],
            foreground=[
                ("active", self.style.primary_fg),  # keep text color readable
                ("pressed", self.style.primary_fg),
            ],
            bordercolor=[
                ("active", self.style.button_border_color_accent),  # white border on hover
                ("pressed", self.style.primary_fg),
            ],
            relief=[
                ("active", "solid"),
                ("pressed", "sunken"),
                ("!active", "flat"),
            ]
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
            container, width=250, relief=tk.RAISED, style=f"{self.style.prefix}.TFrame", padding=2, borderwidth=0
        )
        container.add(self.gui.left_frame)
        # --- DATA Section ---
        self.section_separator("DATA")
        self._add_button_row(
            self.gui.left_frame,
            [
                ("➕ observable", self.plot_selected_data),
                ("➕ event", self.plot_selected_data),
            ],
        )
        self._add_dropdown(
            self.gui.left_frame,
            "scripts",
            var_name="script_var",
            values=[],
            button=("▷", self.plot_selected_data),  # small run button
        )
        # --- MODEL Section ---
        self.section_separator("MODEL")
        (self.gui.obj_cb, self.gui.obj_var) = self._add_dropdown(self.gui.left_frame, "objects", var_name="obj_var", values=[])
        self.section_item_separator()
        (self.gui.var_cb, self.gui.vars_var) = self._add_dropdown(self.gui.left_frame, "variables", var_name="var_var", values=[])

        # --- STATISTICS Section ---
        self.section_separator("STATISTICS")
        self._add_dropdown(
            self.gui.left_frame,
            "plots",
            var_name="plot_var",
            values=["time_series", "distribution"],
            button=("▷", self.plot_selected_data),  # small plot button
        )

        # --- FORECASTING Section ---
        self.section_separator("FORECASTING")
        self._add_dropdown(
            self.gui.left_frame,
            "extrapolations",
            var_name="forecast_var",
            values=[],
            button=("▷", self.plot_selected_data),  # small forecast plot button
        )

    # --- Helper Methods ---

    def _add_button_row(self, parent, buttons):
        """Add a horizontal row of buttons."""
        frame = ttk.Frame(parent, style=f"{self.style.prefix}.TFrame")
        frame.pack(fill="x", padx=self.section_items_padding_x, pady=(self.button_padding, self.button_padding))
        for text, cmd in buttons:
            ttk.Button(
                frame,
                text=text,
                command=cmd,
                style=f"{self.style.prefix}.TButton",
            ).pack(side="left", padx=(0, 5))

    def _add_dropdown(self, parent, label, var_name, values, button=None):
        """Add a labeled dropdown, with optional small square button on the right."""
        ttk.Label(parent, text=label, style=f"{self.style.prefix}.TLabel").pack(
            anchor="w", padx=self.section_items_padding_x, pady=self.section_items_padding_y
        )

        frame = ttk.Frame(parent, style=f"{self.style.prefix}.TFrame")
        frame.pack(fill="x", padx=self.section_items_padding_x, pady=self.section_items_padding_y)

        var = tk.StringVar(master=self.gui)
        setattr(self.gui, var_name, var)

        cb = ttk.Combobox(
            frame,
            textvariable=var,
            state="readonly",
            style=f"{self.style.prefix}.TCombobox",
            values=values,
        )
        cb.pack(side="left", fill="x", expand=True)

        if button:
            text, cmd = button
            ttk.Button(
                frame,
                text=text,
                width=3,  # small square button
                padding=3,
                command=cmd,
                style=f"{self.style.prefix}.TButton",
            ).pack(side="right", padx=(5, 0))

        return cb, var

    def right_pane(self, container):
        self.gui.right_frame = ttk.Frame(container, style=f"{self.style.prefix}.TFrame", borderwidth=0)
        container.add(self.gui.right_frame)

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
            bg=self.style.primary_bg,
            fg=self.style.text_fg,
            insertbackground=self.style.primary_bg,
            borderwidth= 0.5
        )
        self.gui.stats_text.pack(fill="x", padx=0, pady=0)
        self.gui.stats_text.configure(state="disabled")

    def panes(self):
        container = tk.PanedWindow(orient="horizontal", sashwidth=5, bg="#dcdad5")
        container.pack(fill="both", expand=True)
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

        def display_stats_table(stats, fixed_column_width: int | None = None, max_column_width: int = 20, max_value_length: int = 8):
            """
            Display stats in a tabular format in the stats_text widget.

            Args:
                stats: The stats object to display.
                fixed_column_width: If set, forces all columns to use this exact width.
                max_column_width: When dynamic, caps each column width to this length.
            """
            if not stats:
                return

            # Enable the Text widget temporarily
            self.gui.stats_text.configure(state="normal")
            self.gui.stats_text.delete("1.0", tk.END)

            # Extract non-None values
            stats_dict = {k: str(v)[0:max_value_length] for k, v in vars(stats).items() if v is not None}

            if not stats_dict:
                self.gui.stats_text.insert(tk.END, "No statistics available.\n")
                self.gui.stats_text.configure(state="disabled")
                return

            if fixed_column_width:
                col_widths = {k: fixed_column_width for k in stats_dict}

                def fmt_header(k: str) -> str:
                    s = k[:fixed_column_width]
                    return f"{s:^{fixed_column_width}}"  # centered

                def fmt_value(v: str) -> str:
                    s = v[:fixed_column_width]
                    return f"{s:>{fixed_column_width}}"  # right-aligned

            else:
                col_widths = {
                    k: min(max(len(k), len(str(v))), max_column_width)
                    for k, v in stats_dict.items()
                }

                def fmt_header(k: str) -> str:
                    s = k[:col_widths[k]]
                    return f"{s:^{col_widths[k]}}"  # centered

                def fmt_value(k: str, v: str) -> str:
                    s = v[:col_widths[k]]
                    return f"{s:>{col_widths[k]}}"  # right-aligned

            # Header row
            header = " " + " │ ".join(fmt_header(k) for k in stats_dict.keys()) + " │ "
            self.gui.stats_text.insert(tk.END, header + "\n")

            # Values row
            if fixed_column_width:
                values = " " + " │ ".join(fmt_value(v) for v in stats_dict.values()) + " │ "
            else:
                values = " " + " │ ".join(fmt_value(k, v) for k, v in stats_dict.items()) + " │ "
            self.gui.stats_text.insert(tk.END, values + "\n")

            # Disable again
            self.gui.stats_text.configure(state="disabled")
        display_stats_table(plot_data.stats)

    def build_title_bar(self):
        # Title bar frame
        title_bar = ttk.Frame(self.gui)
        title_bar.pack(fill="x")

        # Icon (if provided)
        icon_path = f"{self.gui.gui_path}/assets/logo_small.png"
        try:
            self.gui.icon_image = tk.PhotoImage(file=icon_path)
            icon_label = ttk.Label(title_bar, image=self.gui.icon_image)
            icon_label.pack(side="left", padx=(5, 2))
        except Exception as e:
            print(f"Failed to load icon: {e}")

        # Title text (align left)
        self.gui.title_label = ttk.Label(
            title_bar, text="——  See Your Software Grow Like Never Before", anchor="w"
        )
        self.gui.title_label.pack(side="left", padx=5)

        # Control buttons
        btn_frame = ttk.Frame(title_bar)
        btn_frame.pack(side="right", padx=5)

        style = ttk.Style()
        style.configure("TitleBar.TButton", relief="flat", padding=5)

        ttk.Button(
            btn_frame, text="🗕", style="TitleBar.TButton",
            command=self._minimize
        ).pack(side="left")
        ttk.Button(
            btn_frame, text="🗖", style="TitleBar.TButton",
            command=self._toggle_maximize
        ).pack(side="left")
        ttk.Button(
            btn_frame, text="✕", style="TitleBar.TButton",
            command=self.gui.destroy
        ).pack(side="left")

        # Enable dragging by clicking the title area
        def start_move(event):
            self.gui._x = event.x
            self.gui._y = event.y

        def on_move(event):
            x = self.gui.winfo_pointerx() - self.gui._x
            y = self.gui.winfo_pointery() - self.gui._y
            self.gui.geometry(f"+{x}+{y}")

        # Bind dragging to both the title label and the icon (if present)
        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", on_move)
        self.gui.title_label.bind("<Button-1>", start_move)
        self.gui.title_label.bind("<B1-Motion>", on_move)
        if icon_path:
            icon_label.bind("<Button-1>", start_move)
            icon_label.bind("<B1-Motion>", on_move)

    def _minimize(self):
        self.gui.update_idletasks()
        # Enables the OS window management before calling iconify.
        self.gui.overrideredirect(False)
        self.gui.iconify()

    def _toggle_maximize(self):
        if self._is_maximized:
            self.gui.geometry(self.gui._restore_geometry)
            self._is_maximized = False
        else:
            self.gui._restore_geometry = self.gui.geometry()
            self.gui.geometry(f"{self.gui.winfo_screenwidth()}x{self.gui.winfo_screenheight()}+0+0")
            self._is_maximized = True

    def ensure_overrideredirect(self, interval_ms: int = 500):
        """
        Ensure the window stays in overrideredirect mode.
        This checks every `interval_ms` milliseconds.
        """
        # Only apply if the window is visible
        if self.gui.state() != "iconic":  # not minimized
            if not self.gui.overrideredirect():
                self.gui.overrideredirect(True)

        # Schedule the next check
        self.gui.after(interval_ms, self.ensure_overrideredirect, interval_ms)
