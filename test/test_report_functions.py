#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import walk
import pathlib

from easy_python_requirements import report_object, report_file, report_folder, update_folder, create_report
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
    def test_yaml_output():
        pass
