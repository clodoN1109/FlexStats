class StringHandler:
    """Utility class for string/path handling."""

    @staticmethod
    def truncate_path(source: str, parts: int = 3) -> str:
        """
        Return the last `parts` segments of a path or URL, joined with '/'.
        Works for both local paths and URLs.

        Args:
            source (str): The original path or URL.
            parts (int): How many trailing parts to keep (default=3).

        Returns:
            str: The truncated path string.
        """
        if not source:
            return ""

        normalized = str(source).replace("\\", "/")
        segments = normalized.split("/")
        return "/".join(segments[-parts:]) if len(segments) >= parts else normalized
