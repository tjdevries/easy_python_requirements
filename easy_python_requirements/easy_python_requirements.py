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
    indent_string, get_source_lines,
    get_classes, get_functions, get_depth_of_file, get_type, get_relative_path,
)
from easy_python_requirements.test_info import (
    create_json_info, append_json_info,
)
from easy_python_requirements.parsed import Parsed


logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# 
# 
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

    p = Parsed(obj)
    p.parse()

    output['description'] = p.description
    output['test_info'] = p.test_info

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

    p = Parsed(obj)
    p.parse()

    json_dict['description'] = p.description.split('\n')
    json_dict['test_info'] = p.test_info

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
