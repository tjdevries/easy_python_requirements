#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import json

from easy_python_requirements.report import (ReportObject,
                                             ReportFile,
                                             Report
                                             )
# from easy_python_requirements.update import update_folder
# from test.test_mock_functions import ListFileCleaner


class TestReportObject:
    def test_init(self):
        report = Report('./mock_functions/')

        print(report.to_markdown())


def test_basic_report_object():
    from mock_functions.test_module_stuff import FirstClass

    ro = ReportObject(FirstClass)

    assert ro.description == 'This is a class description\n' \
        'It is multiple lines\n' \
        'It should all be nicely formatted'
    assert ro.type == 'class'
    assert ro.file_info.line_number == 5
    assert ro.file_info.relative_name == 'mock_functions/test_module_stuff.py'


def test_basic_report_object_function():
    from mock_functions.test_module_stuff import FirstClass

    ro = ReportObject(FirstClass.function_that_should_not_change)

    assert ro.description == 'This should never be touched'
    assert ro.type == 'function'


def test_print_file():
    filename = 'mock_functions/test_module_stuff.py'
    rf = ReportFile(filename)

    print(rf.objects)


class TestYaml:
    def test_yaml_output(self):
        pass


# class TestJSON:
#     def test_basic_json_output(self):
#         from mock_functions.test_module_stuff import FirstClass

#         json_class = json.loads(json_report(FirstClass))

#         assert(json_class['type'] == 'class')
#         assert(json_class['test_info'] == {"time_stamp": "2016-07-02T10:45:57.539011", "test_id": 4})
#         assert(json_class['description'] == ["This is a class description",
#                                              "It is multiple lines",
#                                              "It should all be nicely formatted"
#                                              ])

#     def test_recursive_json_output(self):
#         from mock_functions.test_module_stuff import FirstClass

#         json_class = json.loads(json_report(FirstClass))
#         print(json_class)

#         # assert(json_class['functions'])


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
