#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from shutil import copyfile
from os import remove, sep

from easy_python_requirements import parse_func, update_func, update_file, read_json_info


class FileCleaner:
    def __init__(self, filename: str, temp_prefix='._tmp'):
        self.filename = filename
        self.temp_file = temp_prefix + filename.replace(sep, '')

    def __enter__(self):
        copyfile(self.filename, self.temp_file)

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


def test_mock_function_in_module_1():
    with FileCleaner('./mock_functions/test_example_2.py'):
        from mock_functions.test_example_2 import ExampleClass

        desc, requirement_info = parse_func(ExampleClass.function_2)

        assert(desc == 'Requirement info')
        assert(requirement_info['requires_update'] is True)

        update_func(ExampleClass.function_2)

        with open('./mock_functions/test_example_2.py') as f:
            f_list = f.read().split('\n')

        info_line = ''
        for line in f_list:
            if 'TEST INFO' in line:
                info_line = line
                break

        assert('test_id' in info_line)


def test_mock_function_with_multiple_modules():
    with FileCleaner('./mock_functions/test_example_3.py'):
        from mock_functions.test_example_3 import SecondClass

        desc, requirement_info = parse_func(SecondClass.this_doc_string_should_change)

        assert(desc == 'This is the only info that should be read or changed')
        assert(requirement_info['requires_update'] is True)

        update_func(SecondClass.this_doc_string_should_change)

        with open('./mock_functions/test_example_3.py') as f:
            f_list = f.read().split('\n')

        for line in f_list[SecondClass.this_doc_string_should_change.__code__.co_firstlineno:]:
            if 'TEST INFO' in line:
                assert('test_id' in line)
                break


def test_mock_module_with_two_updates():
    """
    This test should demonstrate adding two INFOs, one to the class and one to its function.
    It should add the module one first, and then the function.

    It should make sure that it uses the highest id found.
    """
    with FileCleaner('./mock_functions/test_module_stuff.py'):
        # Pretend we just ran into this when cycling through the files
        files_to_check = ['mock_functions/test_module_stuff.py']

        for f in files_to_check:
            update_file(f)

        for f in files_to_check:
            index = 0
            with open(f, 'r') as reader:
                for line in reader.readlines():
                    print(line, end='')
                    if index == 18:
                        json_info = read_json_info(line)
                        assert(json_info['test_id'] == 6)

                    index += 1
