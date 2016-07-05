#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from easy_python_requirements import report_object, report_file, report_folder


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
    print(report_folder(path))
