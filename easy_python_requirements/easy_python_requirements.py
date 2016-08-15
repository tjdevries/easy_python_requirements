#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
