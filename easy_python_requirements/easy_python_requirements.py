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

from easy_python_requirements.util import (
    trim, indent_string, index_containing_substring, get_source_lines,
    get_classes, get_functions, get_depth_of_file, get_type, get_relative_path,
)
from easy_python_requirements.test_info import (
    create_json_info, append_json_info, info_line_status
)


logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

config = {
    'requirement_begin': 'TEST DESCRIPTION BEGIN',
    'requirement_end': 'TEST DESCRIPTION END',
    'requirement_info': 'TEST INFO:',
    'info_format': ['test_id', 'time_stamp'],
}


# {{{ Parsing Functions
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
    info_dict = parse_doc(f.__doc__)

    if not info_dict['requires_update']:
        return info_dict

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
    info_dict = parse_doc(cls.__doc__)

    if not info_dict['requires_update']:
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

    parsed = parse_func(obj)
    print(parsed)
    output['description'] = parsed['description']
    output['test_info'] = parsed

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
                        info_string = '- {0}: {1}'.format(function_dict['name'], function_dict['test_info']['test_info'])

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
                        info_string = '- {0}: {1}'.format(function_dict['name'], function_dict['test_info']['test_info'])

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


def json_report(obj):
    """
    Take an object and create a JSON object that represents all the pertinent report information

    Args:
        obj (object): The object to be created
    """
    json_dict = {}
    json_dict['type'] = get_type(obj)

    info_dict = parse_doc(obj.__doc__)
    parsed = info_dict['description']

    json_dict['description'] = parsed.split('\n')
    json_dict['test_info'] = info_dict['test_info']

    return json.dumps(json_dict)


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
