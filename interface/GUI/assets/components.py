import calendar
import datetime
import tkinter as tk
from tkinter import ttk

class SimpleDateEntry(ttk.Frame):
    """
    Small date-picker replacement for DateEntry.
    Shows Month / Day / Year comboboxes (can start empty).
    Methods:
      - get_date() -> datetime.datetime | None
      - get_date_string() -> "mm-dd-YYYY" or ""
      - set_date(datetime_or_none) -> fill or clear the controls
    """

    def __init__(self, parent, start_year=None, end_year=None, year_range=10, **kwargs):
        super().__init__(parent, **kwargs)

        today = datetime.date.today()
        sy = start_year if start_year is not None else today.year - year_range
        ey = end_year if end_year is not None else today.year + year_range

        # variables
        self.var_month = tk.StringVar(value="")
        self.var_day = tk.StringVar(value="")
        self.var_year = tk.StringVar(value="")

        # values
        months = [""] + [f"{m:02d}" for m in range(1, 13)]
        days = [""] + [f"{d:02d}" for d in range(1, 32)]
        years = [""] + [str(y) for y in range(sy, ey + 1)]

        # widgets
        self.cb_month = ttk.Combobox(self, textvariable=self.var_month, values=months, width=2, state="readonly")
        self.cb_day   = ttk.Combobox(self, textvariable=self.var_day,   values=days,   width=2, state="readonly")
        self.cb_year  = ttk.Combobox(self, textvariable=self.var_year,  values=years,  width=4, state="readonly")

        # layout (compact)
        self.cb_month.grid(row=0, column=0, padx=(0, 4))
        self.cb_day.grid(  row=0, column=1, padx=(0, 4))
        self.cb_year.grid( row=0, column=2)

        # update days when month or year changes
        self.cb_month.bind("<<ComboboxSelected>>", self._on_month_or_year_change)
        self.cb_year.bind("<<ComboboxSelected>>",  self._on_month_or_year_change)

    # keep days in sync with month/year (handles leap years)
    def _on_month_or_year_change(self, event=None):
        m = self.var_month.get()
        y = self.var_year.get()
        if m and y:
            try:
                mm = int(m)
                yy = int(y)
                ndays = calendar.monthrange(yy, mm)[1]
                days = [""] + [f"{d:02d}" for d in range(1, ndays + 1)]
                # update combobox values while preserving current (if valid)
                cur = self.var_day.get()
                self.cb_day.config(values=days)
                if cur:
                    try:
                        if int(cur) > ndays:
                            self.var_day.set("")  # invalid now
                    except Exception:
                        self.var_day.set("")
            except Exception:
                # if parsing fails, keep full day list
                self.cb_day.config(values=[""] + [f"{d:02d}" for d in range(1, 32)])
        else:
            # month or year missing → allow up to 31 days
            self.cb_day.config(values=[""] + [f"{d:02d}" for d in range(1, 32)])

    def get_date(self) -> datetime.datetime | None:
        """Return a datetime (00:00) or None if any part is empty."""
        m = self.var_month.get()
        d = self.var_day.get()
        y = self.var_year.get()
        if not (m and d and y):
            return None
        try:
            return datetime.datetime(int(y), int(m), int(d))
        except Exception:
            return None

    def get_date_string(self) -> str:
        """Returns 'mm-dd-YYYY' or '' if not set."""
        dt = self.get_date()
        return dt.strftime("%m-%d-%Y") if dt else ""

    def set_date(self, dt: datetime.datetime | None):
        """Set the controls from a datetime (or clear if None)."""
        if dt is None:
            self.var_month.set("")
            self.var_day.set("")
            self.var_year.set("")
        else:
            self.var_month.set(f"{dt.month:02d}")
            # update days list to match month/year before setting day
            self._on_month_or_year_change()
            self.var_day.set(f"{dt.day:02d}")
            self.var_year.set(str(dt.year))

    def clear(self):
        self.set_date(None)
