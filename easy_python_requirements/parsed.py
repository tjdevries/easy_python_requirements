
from easy_python_requirements import config
from easy_python_requirements.util import (
    trim, index_containing_substring, get_type, get_functions
)
from easy_python_requirements.test_info import (
    info_line_status,
)


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
        self.obj = obj
        self.obj_type = get_type(obj)
        self.obj_docstring = obj.__doc__
        self.description = ''
        self.test_info = {}
        self.children = {}

    def parse(self):
        obj_dict = parse_doc(self.obj_docstring)

        self.description = obj_dict.pop('description', None)
        self.requires_update = obj_dict.pop('requires_update', True)
        self.test_info = obj_dict.pop('test_info', None)

        # Handle differences between functions and classes
        if self.obj_type == 'function':
            pass
        elif self.obj_type == 'class':
            funcs = get_functions(self.obj)

            for func in funcs:
                temp_parsed = Parsed(func[1])
                temp_parsed.parse()
                self.children[func[0]] = temp_parsed

    def to_json(self):
        pass

    def to_yaml(self):
        pass

    def to_markdown(self):
        pass

    def to_rst(self):
        pass

    def __str__(self):
        return '<Parsed: {0}>'.format(self.obj.__name__)


def parse_doc(docstring: str):
    """
    Parse the requirement and information from a docstring

    Args:
        docstring (str): the docstring of the test function

    Returns:
        dict: dictionary with info

        description: None if it could not be found,
        otherwise it is a string with the description inside of it

        test_info: A dictionary filled with information
        about the current test specification.

        requires_update: Bool representing whether this docstring needs
        to be updated
    """
    doclist = trim(docstring).split('\n')

    try:
        requirement_begin = index_containing_substring(doclist, config['requirement_begin'])
    except ValueError:
        return {'requires_update': False, 'description': None}

    try:
        requirement_end = index_containing_substring(doclist, config['requirement_end'])
    except ValueError:
        return {'requires_update': False, 'description': None}

    requirement_description = '\n'.join(doclist[requirement_begin + 1:requirement_end])

    try:
        requirement_info = index_containing_substring(doclist, config['requirement_info'], multiples=False)
    except ValueError:
        return {'requires_update': True, 'description': requirement_description}

    info_dict = info_line_status(doclist, requirement_info)
    info_dict['description'] = requirement_description

    return info_dict
