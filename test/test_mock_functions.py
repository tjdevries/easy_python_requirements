#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from shutil import copyfile
from os import remove

from easy_python_requirements import parse_func, update_func


class FileCleaner:
    def __init__(self, filename, temp_file='._tmp'):
        self.filename = filename
        self.temp_file = temp_file

    def __enter__(self):
        copyfile(self.filename, self.temp_file)
        return

    def __exit__(self, type, value, traceback):
        copyfile(self.temp_file, self.filename)
        remove(self.temp_file)


def test_mock_test_example_1():
    with FileCleaner('./mock_functions/test_example_1.py'):
        from mock_functions.test_example_1 import test_feature_example_1

        desc, requirement_info = parse_func(test_feature_example_1)

        assert(desc == 'This **shall** be caught')
        assert(requirement_info['requires_update'] is True)

        update_func(test_feature_example_1)

        with open('./mock_functions/test_example_1.py') as f:
            f_list = f.read().split('\n')

        info_line = ''
        for line in f_list:
            if 'TEST INFO' in line:
                info_line = line
                break

        assert('test_id' in info_line)
