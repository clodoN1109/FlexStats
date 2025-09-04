import datetime
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
        self.icon_label = None
        self.gui = gui
        self.style: GUIStyle = gui.style
        self.section_items_padding_x = 8
        self.section_items_padding_y = 0
        self.button_padding = 10
        self._is_maximized = False
        self.gui.subtitle_text = None

    def config_window_navbar(self):
        self.gui.overrideredirect(True)
        try:
            self.gui.iconphoto(False, tk.PhotoImage(file=f"{self.gui.gui_path}/assets/icons/icon.png"))
        except Exception:
            pass

    def apply_style(self):
        """
        Apply the current GUIStyle (self.style) to ttk styles and other UI elements.
        Updates all widgets recursively, including those created by helpers.
        """
        gui_style = ttk.Style(self.gui)
        try:
            gui_style.theme_use("clam")
        except Exception:
            pass

        theme = self.style
        prefix = theme.prefix

        self.update_logo_image()

        self.gui.attributes("-alpha", 0.9)  # 0.0 = fully transparent, 1.0 = opaque

        # --- Core ttk styles ---
        gui_style.configure(f"{prefix}.TFrame", background=theme.primary_bg)
        gui_style.configure(f"{prefix}.TLabel",
                            background=theme.primary_bg,
                            foreground=theme.primary_fg)
        gui_style.configure(f"{prefix}.Section.TLabel",
                            background=theme.section_separator_bg,
                            foreground=theme.section_separator_fg,
                            anchor="center")
        gui_style.configure(f"{prefix}.TButton",
                            background=theme.accent_bg,
                            foreground=theme.primary_fg,
                            relief="flat",
                            padding=2,
                            borderwidth=0.5)
        gui_style.map(
            f"{prefix}.TButton",
            background=[
                ("active", theme.accent_hover),
                ("pressed", theme.accent_bg)
            ],
            foreground=[
                ("active", theme.primary_fg),
                ("pressed", theme.primary_fg)
            ],
            relief=[
                ("active", "solid"),
                ("pressed", "sunken"),
                ("!active", "flat")
            ],
        )
        gui_style.configure(f"{prefix}.TCombobox",
                            fieldbackground=theme.accent_bg)
        gui_style.configure(f"{prefix}.TSeparator", background=theme.primary_bg)

        # Title bar custom buttons
        gui_style.configure("TitleBar.TButton",
                            background=self.style.primary_bg,
                            foreground=theme.primary_fg,
                            relief="flat",
                            padding=5)

        # --- Recursive restyle function ---
        def restyle_widget(widget):
            try:
                if isinstance(widget, ttk.Frame):
                    widget.configure(style=f"{prefix}.TFrame")
                elif isinstance(widget, ttk.Label):
                    current = widget.cget("style")
                    if "Section" in current:
                        widget.configure(style=f"{prefix}.Section.TLabel")
                    elif "Title" in current:
                        widget.configure(style=f"{prefix}.TLabel")  # or custom title style
                    else:
                        widget.configure(style=f"{prefix}.TLabel")
                elif isinstance(widget, ttk.Button):
                    if "TitleBar" in widget.cget("style"):
                        widget.configure(style="TitleBar.TButton")
                    else:
                        widget.configure(style=f"{prefix}.TButton")
                elif isinstance(widget, ttk.Combobox):
                    widget.configure(style=f"{prefix}.TCombobox")
                elif isinstance(widget, ttk.Separator):
                    widget.configure(style=f"{prefix}.TSeparator")
                elif isinstance(widget, tk.Text):
                    widget.configure(bg=theme.text_bg,
                                     fg=theme.text_fg,
                                     insertbackground=theme.text_fg)
                elif isinstance(widget, tk.Frame):
                    widget.configure(bg=theme.primary_bg)
            except Exception:
                pass

            for child in widget.winfo_children():
                restyle_widget(child)
        restyle_widget(self.gui)

        # Exclusive styles
        self.gui.window_footer.configure(background=self.style.separator_bg)
        self.gui.container.configure(bg=self.style.separator_bg)
        self.gui.stats_separator.configure(bg=self.style.separator_bg)
        self.gui.title_separator.configure(bg=self.style.separator_bg)

        # --- matplotlib re-style ---
        if hasattr(self.gui, "ax") and hasattr(self.gui, "fig"):
            self.gui.fig.set_facecolor(theme.primary_bg)
            self.gui.ax.set_facecolor(theme.text_bg)
            self.gui.ax.tick_params(colors=theme.primary_fg)
            self.gui.ax.xaxis.label.set_color(theme.primary_fg)
            self.gui.ax.yaxis.label.set_color(theme.primary_fg)
            self.gui.ax.title.set_color(theme.primary_fg)
            # Spines (borders around the plot)
            for spine in self.gui.ax.spines.values():
                spine.set_edgecolor(theme.primary_fg)   # border color
                spine.set_linewidth(0.8)

            if self.gui.subtitle_text:
                self.gui.subtitle_text.set_color(theme.primary_fg)
            self.gui.ax.grid(color=theme.grid_color, linestyle="--", linewidth=0.5)
            if hasattr(self.gui, "canvas"):
                try:
                    self.gui.canvas.draw_idle()
                except Exception:
                    pass

    def window(self, title: str, resolution: str = "1000x600"):
        self.gui.title(title)
        self.gui.geometry(resolution)

    def font(self, font_family, size):
        self.gui.default_font = tkFont.Font(family=font_family, size=size)
        self.gui.option_add("*Font", self.gui.default_font)

    def section_separator(self, section_title: str):
        ttk.Label(
            self.gui.left_frame,
            text=section_title,
            anchor="center",
            style=f"{self.style.prefix}.Section.TLabel"
        ).pack(fill="x", padx=0, pady=(0, 5))

    def section_item_separator(self, height = 2):
        spacer = tk.Frame(self.gui.left_frame, height=2, bg=self.style.primary_bg, borderwidth=0, highlightthickness=0)
        spacer.pack(fill="x", pady=height)

    def left_pane(self, container):
        self.gui.left_frame = ttk.Frame(
            container, width=250, relief=tk.RAISED, style=f"{self.style.prefix}.TFrame", padding=(0, 0), borderwidth=0
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
            button=("▷", self.plot_selected_data, 5),
        )
        self.section_item_separator(5)
        # --- MODEL Section ---
        self.section_separator("MODEL")
        (self.gui.obj_cb, self.gui.obj_var) = self._add_dropdown(self.gui.left_frame, "objects", var_name="obj_var", values=[])
        self.section_item_separator()
        (self.gui.var_cb, self.gui.vars_var) = self._add_dropdown(self.gui.left_frame, "variables", var_name="var_var", values=[])
        self.section_item_separator(5)

        # --- STATISTICS Section ---
        self.section_separator("STATISTICS")
        self._add_dropdown(
            self.gui.left_frame,
            "plots",
            var_name="plot_var",
            values=["time series", "distribution"],
            button=("▷", self.plot_selected_data, 5),  # small plot button
        )
        self.section_item_separator(5)

        # --- FORECASTING Section ---
        self.section_separator("FORECASTING")
        self._add_dropdown(
            self.gui.left_frame,
            "extrapolations",
            var_name="forecast_var",
            values=[],
            button=("▷", self.plot_selected_data, 5),  # small forecast plot button
        )
        self.section_item_separator(5)

    # --- Helper Methods ---
    def _add_button(self, frame, text, cmd, width):
        ttk.Button(
            frame,
            text=text,
            command=cmd,
            width=width,
            style=f"{self.style.prefix}.TButton",
        ).pack(side="left", padx=(2, 5), pady=(2, 2))

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
            ).pack(side="left", padx=(self.section_items_padding_x - 2, 0))

    def _add_dropdown(self, parent, label, var_name, values, button=None):
        """Add a labeled dropdown, with optional small square button on the right."""
        ttk.Label(parent, text=label, style=f"{self.style.prefix}.TLabel").pack(
            anchor="w", padx=self.section_items_padding_x * 2, pady=self.section_items_padding_y
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
        cb.pack(side="left", fill="x", expand=False, padx=(self.section_items_padding_x, self.section_items_padding_x/2))

        if button:
            text, cmd, width= button
            self._add_button(frame, text, cmd, width)
        return cb, var

    def right_pane(self, container):
        self.gui.right_frame = ttk.Frame(container, style=f"{self.style.prefix}.TFrame", borderwidth=0)
        container.add(self.gui.right_frame)

        # --- Inner vertical layout ---
        right_inner = ttk.Frame(self.gui.right_frame, style=f"{self.style.prefix}.TFrame")
        right_inner.pack(fill="both", expand=True)

        # Plot area
        self.gui.fig = Figure(figsize=(5, 4), dpi=100)
        self.gui.ax = self.gui.fig.add_subplot(111)

        self.gui.canvas = FigureCanvasTkAgg(self.gui.fig, master=right_inner)
        self.gui.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Stats area
        stats_container = ttk.Frame(right_inner, style=f"{self.style.prefix}.TFrame")
        stats_container.pack(fill="x", side="bottom")

        self.gui.stats_separator = tk.Frame(
            stats_container,
            height=5,  # thickness of the line
            bg=self.style.separator_bg,  # your desired color
            bd=0
        )
        self.gui.stats_separator.pack(fill="x", pady=(0, 2))

        self.gui.stats_text = tk.Text(
            stats_container,
            height=2,
            bg=self.style.primary_bg,
            fg=self.style.text_fg,
            insertbackground=self.style.text_fg,
            borderwidth=0,
            relief="flat",
        )
        self.gui.stats_text.pack(fill="x", padx=0, pady=0)
        self.gui.stats_text.configure(state="disabled")
        # Footer at bottom
        self.gui.window_footer = tk.Frame(
            self.gui,
            height=10,
            borderwidth=0,
        )
        self.gui.window_footer.pack(fill="x", side="bottom")

    def panes(self):
        self.gui.container = tk.PanedWindow(orient="horizontal", sashwidth=5, bg=self.style.separator_bg, borderwidth=0)
        self.gui.container.pack(fill="both", expand=True)
        self.left_pane(self.gui.container)
        self.right_pane(self.gui.container)

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
        self.gui.ax.grid(color=self.style.grid_color, linestyle="--", linewidth=0.5)

        # Plot x vs y
        if plot_data.plot_type == "time series":
            self.gui.ax.plot(plot_data.x, plot_data.y, marker="o")

            # Format x-axis as MM/DD/YYYY and show hours:minutes, but in local time
            local_tz = datetime.datetime.now().astimezone().tzinfo
            # Local timezone-aware formatter
            formatter = mdates.DateFormatter('%m/%d/%Y\n%H:%M', tz=local_tz)
            self.gui.ax.xaxis.set_major_formatter(formatter)

            # Force labels to stay horizontal
            for label in self.gui.ax.get_xticklabels():
                label.set_rotation(0)
                label.set_ha("center")  # center them under the tick

            # Reduce tick label font size
            self.gui.ax.tick_params(axis="x", labelsize=8)
            self.gui.ax.tick_params(axis="y", labelsize=8)
        else:
            self.gui.ax.bar(plot_data.x, plot_data.y)

        self.gui.ax.set_title(plot_data.title.upper(), color=self.style.primary_fg)
        if plot_data.subtitle:
            subtitle_obj = self.gui.ax.set_title(
                plot_data.subtitle,
                fontsize=10,
                loc="right",
                color=self.style.primary_fg,
            )
            # make sure it stays styled on theme refresh
            self.gui.subtitle_text = subtitle_obj

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

    def set_logo_image(self, frame, icon_path):
        try:
            self.gui.icon_image = tk.PhotoImage(file=icon_path)
            self.icon_label = ttk.Label(frame, image=self.gui.icon_image)
            self.icon_label.pack(side="left", padx=(5, 2))
        except Exception as e:
            print(f"Failed to load icon: {e}")

    def update_logo_image(self):
        icon_path = f"{self.gui.gui_path}/assets/icons/logo_{self.style.prefix}.png"
        self.gui.icon_image = tk.PhotoImage(file=icon_path)
        self.icon_label.configure(image=self.gui.icon_image)

    def build_title_bar(self):
        # Title bar frame
        title_bar = ttk.Frame(self.gui)
        title_bar.pack(fill="x")

        icon_path = f"{self.gui.gui_path}/assets/icons/logo_{self.style.prefix}.png"
        self.set_logo_image(title_bar, icon_path)

        # Title text (align left)s
        self.gui.title_label = ttk.Label(
            title_bar, text="——  See your software developing like never before", anchor="w", font=("Courier", 10, "italic")
        )
        self.gui.title_label.pack(side="left", padx=5)

        # Control buttons
        btn_frame = ttk.Frame(title_bar)
        btn_frame.pack(side="right", padx=5)

        style = ttk.Style()
        style.configure("TitleBar.TButton", relief="flat", padding=5)

        self._add_button(btn_frame, "☽/☀", self.toggle_dark_mode, 10)
        self._add_button(btn_frame, "🗕", self._minimize, 10)
        self._add_button(btn_frame, "🗖", self._toggle_maximize, 10)
        self._add_button(btn_frame, "✕", self.gui.destroy, 10)

        # Title separator
        self.gui.title_separator = tk.Frame(
            self.gui,
            height=5,
            borderwidth=0,
        )
        self.gui.title_separator.pack(fill="x", side="top")

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
            self.icon_label.bind("<Button-1>", start_move)
            self.icon_label.bind("<B1-Motion>", on_move)


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

    def toggle_dark_mode(self):
        if self.style.prefix == "Dark":
            self.style = GUIStyle("light")
        else:
            self.style = GUIStyle("dark")
        self.apply_style()