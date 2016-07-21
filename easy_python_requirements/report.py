class Report:
    """
    Use to generate reports. Also used to update.
    """

    def __init__(self, path, recursive=True):
        self.path = path
        self.children = []
        pass

    def update(self):
        pass

    def generate(self):
        pass

    def to_json(self):
        pass

    def to_yaml(self):
        pass

    def to_markdown(self):
        pass

    def to_rst(self):
        pass
