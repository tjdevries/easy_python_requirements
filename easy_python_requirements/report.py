#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inspect
import logging
import sys
from collections import OrderedDict

from easy_python_requirements.parsed import Parsed
from easy_python_requirements.update import (explore_folder,
                                             explore_file
                                             )
from easy_python_requirements.util import (indent_string,
                                           get_depth_of_file,
                                           get_relative_path,
                                           get_type
                                           )

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Report:
    """
    Use to generate reports. Also used to update.
    """

    def __init__(self, path, recursive=True):
        self.path = path
        self.explored = explore_folder(self.path, recursive)

        self._report = OrderedDict()

        for file_name, file_dict in self.explored.items():
            self._report[file_name] = report_file(file_name)

    def update(self):
        pass

    def generate(self):
        pass

    def to_json(self):
        pass

    def to_yaml(self):
        pass

    def to_rst(self):
        pass

    def to_markdown(self):
        logger.info('Reporting on path: {0}'.format(self.path))

        # TODO: Create a nicer formatting and section formatter
        # import pprint
        # pprint.pprint(dict(get_sorted_file_directory_structure(report.keys())))
        # section_tracker = [-1]

        processed = ''
        for file_name, file_dict in self._report.items():
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
