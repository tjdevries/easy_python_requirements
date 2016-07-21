import inspect
import os
import logging
import sys
from pathlib import PurePath
from collections import OrderedDict

from easy_python_requirements.exceptions import MultipleStringError

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def trim(docstring):
    """ From PEP """
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = 99
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < 99:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


def indent_string(string, level=1):
    if string is None:
        return ''
    output = '\n'.join(['    ' * level + line for line in string.split('\n')])
    if output[:-2] != '\n':
        output += '\n'

    return output


def get_relative_path(obj):
    file_path = PurePath(inspect.getfile(obj))
    try:
        return str(file_path.relative_to(os.getcwd()))
    except ValueError:
        logger.warning('Could not get relative for {0} and {1}'.format(str(file_path), os.getcwd()))
        return str(file_path)


def get_depth_of_file(file_name):
    """
    Get the filename length
    """
    if file_name[0:2] == './' or file_name[0:2] == '.\\':
        file_name = file_name[2:]

    return max(len(file_name.split('\\')), len(file_name.split('/')))


def get_separator(file_name):
    if '\\' in file_name:
        return '\\'
    else:
        return '/'


def get_sorted_file_directory_structure(file_list, previous_info=None):
    # TODO: This is the file to handle the nicer formatting structure
    # sorted dict
    sd = OrderedDict()

    for name in file_list:
        sd[name] = name

    return sd
    # sd['./'] = []
    # # print('.' + get_separator(file_list[0]))

    # for name in file_list:
    #     depth = get_depth_of_file(name) - 1

    #     beginning = name.split(get_separator(name))[0]
    #     end = get_separator(name).join(name.split(get_separator(name))[1:])

    #     print(beginning, end, depth)

    #     if depth > 0:
    #         if beginning not in sd.keys():
    #             if previous_info:
    #                 previous_info[0][previous_info[1]][beginning] = []
    #                 print(dict(previous_info[0].items()), previous_info[1] + '/' + beginning)
    #             else:
    #                 sd[beginning] = []

    #         # sd[beginning].append(get_sorted_file_directory_structure([end], (sd, beginning)))
    #         get_sorted_file_directory_structure([end], (sd, beginning))
    #     else:
    #         # sd['./'].append(name)
    #         if previous_info:
    #             print(previous_info)
    #             previous_info[0][previous_info[1]].append(name)
    #         else:
    #             sd['./'].append(name)

    # return sd


def index_containing_substring(search_list, substring, multiples=True):
    """
    Find the index of the line that contains a substring

    Args:
        search_list (list): A list containing strings
        substring (str): The string to search for in the list
        multiples (Optional[bool]): Allow more than one string to be found
    """
    num_found = 0
    list_index = -1

    for index, s in enumerate(search_list):
        if substring in s:
            if num_found == 0:
                list_index = index

            num_found += 1

    if list_index == -1:
        raise ValueError(search_list.index(substring))
    else:
        if not multiples and num_found > 1:
            raise MultipleStringError("Multiple {0} found in search_list.".format(substring))
        else:
            return list_index


def get_functions(obj):
    return inspect.getmembers(obj, inspect.isfunction)


def get_classes(obj):
    return inspect.getmembers(obj, inspect.isclass)


def get_modules(obj):
    return inspect.getmembers(obj, inspect.getmodule)


def get_type(obj):
    if inspect.isclass(obj):
        return 'class'
    elif inspect.isfunction(obj):
        return 'function'
    else:
        return str(type(obj))


def get_source_lines(lines: list, obj) -> int:
    """
    Get the line number where the object definition occurs

    Args:
        lines (list): The lines of the file
        obj: An obect (either a class or function) to get the line number

    Returns:
        (int, int): The line number where the definition first occurs, and the last line of source
    """
    source_lines = inspect.getsourcelines(obj)[0]
    source_length = len(source_lines)

    for index in range(len(lines) - source_length):
        if source_lines == lines[index:index + source_length]:
            return index, index + source_length

    return None, None
