class Script:
    def __init__(self, name: str, extension: str, path: str):
        self.name = name
        self.extension = extension
        self.path = path
    def __repr__(self):
        return f"Script(name={self.name}, ext={self.extension}, path={self.path})"