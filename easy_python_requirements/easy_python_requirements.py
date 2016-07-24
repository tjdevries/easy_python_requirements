#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import logging
import sys

from easy_python_requirements.util import (
    get_type,
)
from easy_python_requirements.parsed import Parsed


logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def otherstuff():
    pass
    # output += 'Class: {0}, defined at line `{1}` in {2}\n'.format(c_value.__name__,
    #                                                               inspect.getsourcelines(c_value)[1],
    #                                                               get_relative_path(c_value))


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
    print(args)

#     if args.mode == 'r':
#         report = create_report(args.folder_name)

#         if args.output_file:
#             with open(args.output_file, 'w+') as f:
#                 f.write(report)
#         else:
#             print(report)
#     elif args.mode == 'u':
#         update_folder(args.folder_name)
#     elif args.mode == 'a':
#         update_folder(args.folder_name)

#         report = create_report(args.folder_name)
#         if args.output_file:
#             with open(args.output_file, 'r') as f:
#                 f.write(report)
#         else:
#             print(report)
