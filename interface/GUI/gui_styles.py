class GUIStyle:
    def __init__(self, mode: str = "dark"):
        if mode == "dark":
            self.primary_bg = "#252526"  # deep background (like VS Code dark)
            self.primary_fg = "#f0f0f0"  # main text, near-white
            self.accent_bg = "#333333"  # buttons, inputs (entry field)
            self.accent_hover = "#444444"  # button hover
            self.separator_bg = "#333333"  # subtle dividers (kept subtle/invisible)
            self.text_bg = "#252526"  # sub-panes / stats background
            self.text_fg = "#f0f0f0"  # text in sub-panes
            self.grid_color = "#3a3a3a"  # chart grid, softer than fg
            self.semantic_info = "#569cd6"  # highlights (blue, like VS Code)
            self.button_border_color_accent = "#569cd6"
            self.section_separator_fg = "#f0f0f0"
            self.section_separator_bg = "#434343"
            self.footer_bg = "#333333"
            self.prefix = "Dark"

        elif mode == "light":
            self.primary_bg = "#ffffff"  # clean white
            self.primary_fg = "#252526"  # strong black text
            self.accent_bg = "#f0f0f0"  # buttons, inputs (entry field)
            self.accent_hover = "#e0e0e0"  # button hover
            self.separator_bg = "#e5e5e5"  # subtle divider
            self.text_bg = "#fafafa"  # sub-panes background
            self.text_fg = "#2b2b2b"  # text in sub-panes
            self.grid_color = "#d0d0d0"  # chart grid
            self.semantic_info = "#2e7d32"  # Pythonic green
            self.button_border_color_accent = "#ffd43b" # Pythonic yellow
            self.section_separator_fg = "#252526"
            self.section_separator_bg = "#f0f0f0"
            self.footer_bg = "#f0f0f0"
            self.prefix = "Light"
        else:
            raise ValueError(f"Unknown style mode: {mode}")