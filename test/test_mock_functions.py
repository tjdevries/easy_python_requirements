#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from shutil import copyfile
from os import remove, sep, walk
import pathlib

from easy_python_requirements.update import update_func, update_file, update_folder, update_class
from easy_python_requirements.parsed import Parsed
from easy_python_requirements.test_info import read_json_info


class FileCleaner:
    def __init__(self, filename: str, temp_prefix='._tmp'):
        self.filename = filename
        self.temp_file = temp_prefix + filename.replace(sep, '')

    def __enter__(self):
        copyfile(self.filename, self.temp_file)

    def __exit__(self, type, value, traceback):
        copyfile(self.temp_file, self.filename)
        remove(self.temp_file)


class ListFileCleaner:
    def __init__(self, filenames: list, temp_prefix='._tmp'):
        self.filenames = filenames

        self.filecleaners = []
        for filename in self.filenames:
            self.filecleaners.append(FileCleaner(filename))

    def __enter__(self):
        for filecleaner in self.filecleaners:
            filecleaner.__enter__()

    def __exit__(self, type, value, traceback):
        for filecleaner in self.filecleaners:
            filecleaner.__exit__(type, value, traceback)


def test_mock_test_example_1():
    with FileCleaner('./mock_functions/test_example_1.py'):
        from mock_functions.test_example_1 import test_feature_example_1

        p = Parsed(test_feature_example_1)
        p.parse()
        desc = p.description

        assert(desc == 'This **shall** be caught')
        assert(p.requires_update is True)

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

        p = Parsed(ExampleClass.function_2)
        p.parse()

        desc = p.description

        assert(desc == 'Requirement info')
        assert(p.requires_update is True)

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
        from mock_functions.test_example_3 import SecondClassExample

        p = Parsed(SecondClassExample.this_doc_string_should_change)
        p.parse()
        desc = p.description

        assert(desc == 'This is the only info that should be read or changed')
        assert(p.requires_update is True)

        update_func(SecondClassExample.this_doc_string_should_change)

        with open('./mock_functions/test_example_3.py') as f:
            f_list = f.read().split('\n')

        for line in f_list[SecondClassExample.this_doc_string_should_change.__code__.co_firstlineno:]:
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
                    if index == 27:
                        print(line)
                        json_info = read_json_info(line)
                        assert(json_info['test_id'] == 6)

                    index += 1


def test_mock_folder_update():
    """
    This test will take a directory and update all of the files there.
    Folder update does not check recursively if False is set.
    """
    effected_files = []
    for path, subdirs, files in walk('./mock_functions/'):
        for name in files:
            if '__' in name:
                continue
            if 'pyc' in name:
                continue
            effected_files.append(str(pathlib.PurePath(path, name)))

    print(effected_files)
    with ListFileCleaner(effected_files):
        folder_to_check = './mock_functions/'

        update_folder(folder_to_check, False)

        for f in effected_files:
            with open(f, 'r') as reader:
                for line in reader.readlines():
                    if 'TEST INFO' in line:
                        print(f, line)


def test_mock_class_update():
    with FileCleaner('./mock_functions/test_module_stuff.py'):
        from mock_functions.test_module_stuff import SecondClass

        update_class(SecondClass)

        with open('./mock_functions/test_module_stuff.py', 'r') as reader:
            desired_line = -1
            index = 0
            for line in reader.readlines():
                if 'SecondClass' in line:
                    desired_line = index + 2

                if index == desired_line:
                    print(line)
                    json_info = read_json_info(line)
                    assert(json_info['test_id'] > 1)

                index += 1
