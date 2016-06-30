#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
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


def module_to_filename(name):
    name = name.replace('.', os.sep)

    return name + '.py'


def update_func(f):
    """
    Update the info for a function

    Args:
        f (function): The function to update

    Returns:
        None
    """
    print()
    print(f.__module__)
    filename = module_to_filename(f.__module__)
    with open(filename, 'r+') as location:
        for index, line in enumerate(location):
            if 'TEST INFO' in line:
                index_to_write = index
                break

    with open(filename, 'r') as location:
        for line in location:
            print(line, end='')

    print(f.__qualname__)
