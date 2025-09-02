from pathlib import Path
import unicodedata
from interface.CLI.input.commands import *


class InputPreProcessor:

    @staticmethod
    def normalize(arg: str, is_path: bool = False) -> str:
        arg = unicodedata.normalize("NFC", arg).strip()
        if is_path:
            arg = str(Path(arg))
        return arg