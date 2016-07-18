#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import inspect
import pkgutil
import importlib
import os
import logging
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import PurePath

from easy_python_requirements.exceptions import MultipleStringError


logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

config = {
    'requirement_begin': 'TEST DESCRIPTION BEGIN',
    'requirement_end': 'TEST DESCRIPTION END',
    'requirement_info': 'TEST INFO:',
    'info_format': ['test_id', 'time_stamp'],
}

highest_id = 0


# {{{ Utility Functions
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


# }}}
# {{{ TEST INFO functions
def create_json_info():
    global highest_id

    highest_id += 1
    test_id = highest_id

    time_stamp = str(datetime.today().isoformat())

    return json.dumps({'test_id': test_id, 'time_stamp': time_stamp})


def read_json_info(test_info_line: str):
    """
    Essentially the reverse of create_json_info.
    Gets the json info from a line.

    Args:
        test_info_line (str): The line containing the json info

    Returns:
        dict: JSON info dictionary
    """
    return json.loads(':'.join(test_info_line.split(':')[1:]))


def append_json_info(filename, index, value):
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

    logger.debug('Appending {0} to line {1} of {2}'.format(
        value,
        index,
        filename
    ))
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
    global highest_id
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

        # Any specific cleanup required
        # print(info_dict)
        highest_id = max(info_dict['info']['test_id'], highest_id)

    return info_dict


# }}}
# {{{ Parsing Functions
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
        requirement_info = index_containing_substring(doclist, config['requirement_info'], multiples=False)
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


# }}}
# {{{ Updating Functions
def update_func(f):
    """
    Update the info for a function

    Args:
        f (function): The function to update

    Returns:
        dict: function information
            test_id: id of the function encountered
    """
    desc, info_status = parse_doc(f.__doc__)

    if not info_status['requires_update']:
        return info_status

    filename = inspect.getfile(f)
    with open(filename, 'r+') as location:
        for index, line in enumerate(location.readlines()):
            # We have not reached the function yet
            if index < f.__code__.co_firstlineno:
                continue

            if 'TEST INFO' in line:
                test_info_index = index
                break

    new_json = create_json_info()
    append_json_info(filename, test_info_index, new_json)

    return new_json


def update_class(cls):
    """
    Update the info for a class

    Returns:
        None
    """
    desc, info_status = parse_doc(cls.__doc__)

    if not info_status['requires_update']:
        return

    filename = inspect.getfile(cls)

    with open(filename, 'r+') as location:
        lines = location.readlines()

    first_line, last_line = get_source_lines(lines, cls)

    with open(filename, 'r+') as location:
        for index, line in enumerate(location.readlines()):
            # We have not reached the function yet
            if index < first_line or index > last_line:
                continue

            if config['requirement_info'] in line:
                test_info_index = index
                break

    append_json_info(filename, test_info_index, create_json_info())


def update_file(filename):
    """
    Get, parse and update the file with the correct info
    """
    explored = OrderedDict()
    explored = explore_file(filename)

    for c_name, c_value in explored['module'].items():
        update_class(c_name)
        for f_name, f_value in c_value.items():
            update_func(f_value)

    for f_name, f_value in explored['function'].items():
        update_func(f_value)


def update_folder(path, recursive=True):
    explored = explore_folder(path, recursive)
    # pprint(explored)

    for name in explored.keys():
        update_file(name)

    return


# }}}
# {{{ Exploring Functions
def explore_file(filename):
    # loader = importlib.machinery.SourceFileLoader('', filename)
    # module = loader.load_module('')
    if filename[0:2] == './' or filename[0:2] == '.\\':
        filename = filename[2:]

    mod_name = filename.replace('/', '.').replace('\\', '.')[:-3]
    logger.debug('Importing filename {0} from filename {1} with cwd: {2}'.format(mod_name, filename, os.getcwd()))

    module = importlib.import_module(mod_name)
    # module = importlib.reload(module)

    explored = {'module': OrderedDict(), 'function': OrderedDict()}
    for c_name, c_member in get_classes(module):
        current = OrderedDict()
        parse_doc(c_member.__doc__)
        for f_name, f_member in get_functions(c_member):
            current[f_name] = f_member
            parse_doc(f_member.__doc__)

        explored['module'][c_member] = current

    for f_name, f_member in get_functions(module):
        explored['function'][f_name] = f_member

    return explored


def explore_folder(foldername, recursive=True):
    files_to_load = []
    explored = OrderedDict()

    logger.debug('Exploring folder {0} from folder {1}'.format(foldername, os.getcwd()))
    for load, name, is_pkg in pkgutil.walk_packages([foldername]):
        # if not recursive and is_pkg:
        #     continue
        if is_pkg:
            path = load.path + name + os.sep
            logger.debug(path)
            temp_explored = explore_folder(path)
            for key, value in temp_explored.items():
                explored[key] = value
                # explored.move_to_end(key)
        else:
            files_to_load.append(load.path + name + '.py')

    for f in files_to_load:
        logger.info('File: {0}'.format(f))
        explored[f] = explore_file(f)

    # TODO: Get the order sorted by files, then directories
    explored = OrderedDict(sorted(explored.items(), key=lambda x: get_depth_of_file(x[0])))

    return explored


# }}}
# {{{ Reporting Functions
def report_object(obj: object):
    """
    Report an object by returning a dictionary of key features

    Args:
        obj (object): Object to report on

    Returns:
        dic:
        {
            'type': The objects type (i.e., 'class', 'function')
            'description': The description found from the doc string, or None if not applicable
            'test_info': The info dictionary
            'file_info': {'absolute_name', 'relative_name', 'source', 'line_number'}
        }
    """
    output = {}

    output['name'] = obj.__name__
    output['type'] = get_type(obj)

    output['description'], output['test_info'] = parse_func(obj)

    output['file_info'] = {}
    output['file_info']['source'] = inspect.getsourcelines(obj)[0]
    output['file_info']['line_number'] = inspect.getsourcelines(obj)[1]
    output['file_info']['absolute_name'] = inspect.getfile(obj)
    output['file_info']['relative_name'] = get_relative_path(obj)

    if output['type'] in ['class']:
        output['function'] = {}

    return output


def report_file(filename):
    explored = explore_file(filename)

    output = OrderedDict()
    for c_value, c_functions in explored['module'].items():
        class_report = report_object(c_value)
        output[class_report['name']] = class_report

        for f_name, f_value in c_functions.items():
            object_report = report_object(f_value)
            if object_report['description']:
                output[class_report['name']]['function'][object_report['name']] = object_report

    for f_name, f_value in explored['function'].items():
        function_report = report_object(f_value)
        if function_report['description']:
            if 'function' not in output.keys():
                output['function'] = {}

            output['function'][function_report['name']] = function_report

    return output


def report_folder(path):
    explored = explore_folder(path)

    output = OrderedDict()
    for file_name, file_dict in explored.items():
        output[file_name] = report_file(file_name)

    return output


def create_report(path):
    """
    Create a report from a specified directory

    Args:
        path (str): The path to the folder to search through

    Returns:
        str: The report, nicely formatted and full of happiness
    """
    logger.info('Reporting on path: {0}'.format(path))
    report = report_folder(path)

    # TODO: Create a nicer formatting and section formatter
    # import pprint
    # pprint.pprint(dict(get_sorted_file_directory_structure(report.keys())))
    # section_tracker = [-1]

    processed = ''
    for file_name, file_dict in report.items():
        depth_of_dir = get_depth_of_file(file_name)

        # try:
        #     section_tracker[depth_of_dir] += 1
        # except IndexError:
        #     original_len = len(section_tracker)
        #     while len(section_tracker) < depth_of_dir:
        #         section_tracker.append(-1)

        #     for item in range(1, original_len):
        #         section_tracker[item] += 1

        # processed += '{2} | {1} File: {0}\n\n'.format(file_name,
        #                                               '#' * (depth_of_dir),
        #                                               '.'.join(str(index) for index in section_tracker[0:depth_of_dir]))
        processed += '{1} File: {0}\n\n'.format(file_name, '#' * (depth_of_dir - 1))

        for class_name, class_dict in file_dict.items():
            # Check if we've come to the function key, which specifies functions without a class
            if class_name == 'function':
                for function_name, function_dict in class_dict.items():
                    if function_dict['description'] is None:
                        continue

                    name_string = '- {0}'.format(function_name)

                    if function_dict['test_info']['requires_update']:
                        info_string = '- This function requires an update before being processed'
                    else:
                        info_string = '- {0}: {1}'.format(function_dict['name'], function_dict['test_info']['info'])

                    desc_string = '- {0}'.format(function_dict['description'])

                    processed += indent_string(name_string, 0)
                    processed += indent_string(info_string, 1)
                    processed += indent_string(desc_string, 2)
                continue

            # Now we know we have classes or defined functions left
            processed += indent_string('- ' + class_name, 0)
            if class_dict['type'] == 'class':
                for function_name, function_dict in class_dict['function'].items():
                    if function_dict['description'] is None:
                        continue

                    if function_dict['test_info']['requires_update']:
                        info_string = '- This function requires an update before being processed'
                    else:
                        info_string = '- {0}: {1}'.format(function_dict['name'], function_dict['test_info']['info'])

                    desc_string = '- {0}'.format(function_dict['description'])

                    processed += indent_string(info_string, 1)
                    processed += indent_string(desc_string, 2)

            elif class_dict['type'] == 'function':
                processed += indent_string('- ' + class_dict['name'])

            else:
                pass

        processed += '\n'
    return processed


def otherstuff():
    pass
    # output += 'Class: {0}, defined at line `{1}` in {2}\n'.format(c_value.__name__,
    #                                                               inspect.getsourcelines(c_value)[1],
    #                                                               get_relative_path(c_value))

# }}}
if __name__ == "__main__":
    logger.debug('Appending `{0}` to sys.path'.format(os.getcwd()))
    sys.path.append(os.getcwd())

    parser = argparse.ArgumentParser(description='Update and report on test requirements')
    parser.add_argument('folder_name', type=str,
                        help='The folder name to run the operation on')
    parser.add_argument('mode', choices=['u', 'r', 'a'],
                        help='Choose what mode to run in.\n`u`: update\n`r`: report\n`a`: all')
    parser.add_argument('-o', '--output', dest='output_file', default=None,
                        help='Output file for created report')

    args = parser.parse_args()

    if args.mode == 'r':
        report = create_report(args.folder_name)

        if args.output_file:
            with open(args.output_file, 'w+') as f:
                f.write(report)
        else:
            print(report)
    elif args.mode == 'u':
        update_folder(args.folder_name)
    elif args.mode == 'a':
        update_folder(args.folder_name)

        report = create_report(args.folder_name)
        if args.output_file:
            with open(args.output_file, 'r') as f:
                f.write(report)
        else:
            print(report)
