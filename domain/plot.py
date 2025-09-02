from dataclasses import dataclass
from typing import List, Optional

from domain.stats import Stats


@dataclass
class PlotData:
    object_name: str
    variable_name: str
    plot_type: str

    # For plotting
    x: List
    y: List

    # Metadata for GUI display
    title: str
    subtitle: Optional[str] = None
    x_label: str = "X"
    y_label: str = "Y"

    # Stats object
    stats: Optional["Stats"] = None

    def __str__(self) -> str:
        def sample(lst, n=5):
            """Return a preview of list values with ellipsis if too long."""
            if not lst:
                return "[]"
            if len(lst) <= n:
                return str(lst)
            return f"[{', '.join(map(str, lst[:n]))}, …] (len={len(lst)})"

        lines = [
            f"  Title       : {self.title}"
        ]
        if self.subtitle:
            lines.append(f"  Subtitle    : {self.subtitle}")
        lines.extend([
            f"  Object      : {self.object_name}",
            f"  Variable    : {self.variable_name}",
            f"  Plot type   : {self.plot_type}",
            f"  X label     : {self.x_label}",
            f"    sample    : {sample(self.x)}",
            f"  Y label     : {self.y_label}",
            f"    sample    : {sample(self.y)}",
        ])
        if self.stats:
            lines.append("  Stats       :")
            for field, value in self.stats.__dict__.items():
                lines.append(f"    {field:<10} = {value}")
        return "\n".join(lines)


