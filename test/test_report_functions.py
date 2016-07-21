#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import walk
import pathlib
import json

from easy_python_requirements import (report_object,
                                      report_file,
                                      report_folder,
                                      update_folder,
                                      create_report,
                                      json_report)
from test.test_mock_functions import ListFileCleaner


def test_print_obj():
    from mock_functions.test_module_stuff import FirstClass

    if False:
        print()
        report_object(FirstClass)


def test_print_file():
    filename = 'mock_functions/test_module_stuff.py'
    if False:
        print(report_file(filename))


def test_print_folder():
    path = 'mock_functions/'
    if False:
        print(report_folder(path))


def test_create_report():
    effected_files = []
    for path, subdirs, files in walk('./mock_functions/'):
        for name in files:
            if '__' in name:
                continue
            if 'pyc' in name:
                continue
            effected_files.append(str(pathlib.PurePath(path, name)))

    with ListFileCleaner(effected_files):
        folder_to_check = './mock_functions/'

        update_folder(folder_to_check, False)

        print(create_report(folder_to_check))


class TestYaml:
    def test_yaml_output(self):
        pass


class TestJSON:
    def test_basic_json_output(self):
        from mock_functions.test_module_stuff import FirstClass

        json_class = json.loads(json_report(FirstClass))

        assert(json_class['type'] == 'class')
        assert(json_class['test_info'] == {"time_stamp": "2016-07-02T10:45:57.539011", "test_id": 4})
        assert(json_class['description'] == ["This is a class description",
                                             "It is multiple lines",
                                             "It should all be nicely formatted"
                                             ])

    def test_recursive_json_output(self):
        from mock_functions.test_module_stuff import FirstClass

        json_class = json.loads(json_report(FirstClass))
        print(json_class)

        # assert(json_class['functions'])


'''
class FirstClass:
    """
    TEST INFO: {"time_stamp": "2016-07-02T10:45:57.539011", "test_id": 4}
    TEST DESCRIPTION BEGIN
    This is a class description
    It is multiple lines
    It should all be nicely formatted
    TEST DESCRIPTION END
    Doesn't really matter
    """
    def function_that_should_not_change(self):
        """
        TEST INFO: {"time_stamp": "2016-07-01T10:45:56.539011", "test_id": 5}
        TEST DESCRIPTION BEGIN
        This should never be touched
        TEST DESCRIPTION END
        Other stuff here
        """
        pass
'''
