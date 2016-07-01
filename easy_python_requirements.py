#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import inspect
import pkgutil
import importlib
from datetime import datetime


config = {
    'requirement_begin': 'TEST DESCRIPTION BEGIN',
    'requirement_end': 'TEST DESCRIPTION END',
    'requirement_info': 'TEST INFO:',
    'info_format': ['test_id', 'time_stamp'],
}

highest_id = 0


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


def index_containing_substring(search_list, substring):
    for index, s in enumerate(search_list):
        if substring in s:
            return index

    raise ValueError(search_list.index(substring))


def create_json_info():
    global highest_id

    test_id = highest_id
    highest_id += 1

    time_stamp = str(datetime.today().isoformat())

    return json.dumps({'test_id': test_id, 'time_stamp': time_stamp})


def append_json_info(filename, index, value, previous_info=None):
    """
    Append the json info to the correct line in the file.

    Args:
        index (int): The line number to append to.
        value (str): The item to append to the line
        previous_info (dict): The previous info in the dictionary
            TODO: Use this

    Returns:
        None
    """
    with open(filename, "r") as f:
        contents = f.readlines()

    contents[index] = contents[index].replace('\n', '') + ' ' + value + '\n'

    with open(filename, "w") as f:
        f.writelines(contents)


def info_line_status(doclist, info_index):
    """
    Determine the attributes of the info line

    Args:
        doclist (list): The docstring -> list
        info_index (int): The index to begin checking at

    Returns:
        dict: Information dictionary, specifying important info
    """
    info_dict = {}

    # If the test info line contains just a place holder
    if doclist[info_index] == config['requirement_info']:
        info_dict['requires_update'] = True
    else:
        # Proper info is automatically recorded in JSON,
        #   so if it doesn't properly load into JSON then it's wrong
        try:
            info_json = json.loads(doclist[info_index].split(config['requirement_info'])[1])

            if all(x in info_json.keys() for x in config['info_format']):
                info_dict['requires_update'] = False
            else:
                info_dict['requires_update'] = True
        except ValueError:
            info_dict['requires_update'] = True

    # Get info if it doesn't need to be updated
    if info_dict['requires_update'] is False:
        info_dict['info'] = {}
        for key in info_json.keys():
            info_dict['info'][key] = info_json[key]

    return info_dict


def parse_doc(docstring: str):
    """
    Parse the requirement and information from a docstring

    Args:
        docstring (str): the docstring of the test function

    Returns:
        list: [requirement_description, dictionary with info]
            requirement_description: None if it could not be found,
            otherwise it is a string with the description inside of it

            dictionary_with_info: A dictionary filled with information
            about the current test specification.
    """
    doclist = trim(docstring).split('\n')

    try:
        requirement_begin = index_containing_substring(doclist, config['requirement_begin'])
    except ValueError:
        return [None, {'requires_update': False}]

    try:
        requirement_end = index_containing_substring(doclist, config['requirement_end'])
    except ValueError:
        return [None, {'requires_update': False}]

    requirement_description = '\n'.join(doclist[requirement_begin + 1:requirement_end])

    try:
        requirement_info = index_containing_substring(doclist, config['requirement_info'])
    except ValueError:
        return [requirement_description, {'requires_update': True}]

    info_dict = info_line_status(doclist, requirement_info)

    return [requirement_description, info_dict]


def parse_func(f):
    """
    Parse the function given

    Args:
        f (function): The test function to be parsed

    Returns:
        undecided
    """
    docstring = f.__doc__

    return parse_doc(docstring)


def update_func(f):
    """
    Update the info for a function

    Args:
        f (function): The function to update

    Returns:
        None
    """
    desc, info_status = parse_doc(f.__doc__)

    if not info_status['requires_update']:
        return

    filename = inspect.getfile(f)
    with open(filename, 'r+') as location:
        for index, line in enumerate(location.readlines()):
            # We have not reached the function yet
            if index < f.__code__.co_firstlineno:
                continue

            if 'TEST INFO' in line:
                test_info_index = index
                break

    append_json_info(filename, test_info_index, create_json_info())

    # print()
    # print(f.__module__)
    # print(dir(f.__code__))
    # print(f.__code__.co_filename)
    # print(f.__code__.co_firstlineno)
    # with open(filename, 'r') as this_file:
    #     print(this_file.read())
    # print(f.__qualname__)


def get_functions(obj):
    return inspect.getmembers(obj, inspect.isfunction)


def get_classes(obj):
    return inspect.getmembers(obj, inspect.isclass)


def get_modules(obj):
    return inspect.getmembers(obj, inspect.getmodule)


def explore_file(filename):
    loader = importlib.machinery.SourceFileLoader('', filename)
    module = loader.load_module('')

    explored = {'module': {}, 'function': {}}
    for c_name, c_member in get_classes(module):
        current = {}
        for f_name, f_member in get_functions(c_member):
            current[f_name] = f_member

        explored['module'][c_name] = current

    for f_name, f_member in get_functions(module):
        explored['function'][f_name] = f_member

    return explored


def update_file(filename):
    """
    Get, parse and update the file with the correct info
    """
    # prefix = '.'.join(filename.split('/')[:-1])
    # name = filename.split('/')[-1].replace('.py', '')
    # print(prefix, name)

    explored = explore_file(filename)

    import pprint
    pprint.pprint(explored)

    for c_name, c_value in explored['module'].items():
        print(c_name)
        for f_name, f_value in c_value.items():
            print(f_name)
            # print(f_values.__doc__)
            update_func(f_value)


def update_folder(path):
    for load, name, is_pkg in pkgutil.walk_packages([path]):
        print(name)

    return

    """
    for name, member in get_modules(mock_functions):
        print(name)
        mod = getattr(mock_functions, name)
        # Get all the classes
        for c_name, member in get_classes(mod):
            print('\t', c_name)
            c_class = getattr(mod, c_name)
            for f_name, f_member in get_functions(c_class):
                print('\t\t', f_name)

        for f_name, member in get_functions(mod):
            print('\t', f_name)

    if False:
        importlib.find_spec("", filename)
    """
