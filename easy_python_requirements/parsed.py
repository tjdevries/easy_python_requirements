

class Parsed:
    """
    The class that represents a parsed object.

    Args:
        obj (object): Could be of type [class, function]

    Attributes:
        description (str): The test description provided in the docstring
        test_id (int): The unique ID that this test has
        time_stamp (datetime): The time when this requirement was originally created
        children (list): List of objects that are children of this object.
            For example, a class could have several functions within it.
            Functions could even have functions within it.

    Functions:
        to_json: Serialize the object to JSON
        to_yaml: Serialize the object to YAML
        to_markdown: Serialize the object to a markdown document
    """

    def __init__(self, obj):
        self.description = ''
        self.test_info = {}
        self.children = []

    def to_json(self):
        pass

    def to_yaml(self):
        pass

    def to_markdown(self):
        pass

    def to_rst(self):
        pass
