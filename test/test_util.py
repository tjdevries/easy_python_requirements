from easy_python_requirements import util


class TestIndentString:
    def test_none(self):
        assert util.indent_string(None) == ''

    def test_no_newline(self):
        assert util.indent_string('no newline') == '    no newline\n'

    def test_with_multiple_newlines(self):
        s = 'wow newlines\n\n\n'
        assert util.indent_string(s) == '    wow newlines\n'

    def test_with_newline(self):
        assert util.indent_string('with newline\n') == '    with newline\n'

    def test_with_newline_and_indent(self):
        assert util.indent_string('with newline\n', 2) == '        with newline\n'

    def test_with_other_spacing(self):
        assert util.indent_string('new spacing', 2, '~~~') == '~~~~~~new spacing\n'


class TestGetRelativePath:
    def test_no_relative_path(self):
        from mock_functions.test_module_stuff import FirstClass
        assert util.get_relative_path(FirstClass, 'bad path') != 'mock_functions/test_module_stuff.py'

    def test_relative_path(self):
        from mock_functions.test_module_stuff import FirstClass
        assert util.get_relative_path(FirstClass) == 'mock_functions/test_module_stuff.py'


class TestGetDepthOfFile:
    def test_no_depth(self):
        assert util.get_depth_of_file('file.py') == 1

    def test_get_one_depth(self):
        assert util.get_depth_of_file('folder/file.py') == 2

    def test_ignores_leading_dot_slash(self):
        assert util.get_depth_of_file('.\\folder\\file.py') == 2

    def test_does_not_ignore_leading_slash(self):
        # TODO: Decide if this is the behavior I want
        assert util.get_depth_of_file('/usr/file.py') == 3

    def test_handles_mixed_slashes(self):
        assert util.get_depth_of_file('this/folder\\mixed.py') == 3


class TestGetType:
    def test_is_class(self):
        from mock_functions.test_module_stuff import FirstClass
        assert util.get_type(FirstClass) == 'class'

    def test_is_function(self):
        from mock_functions.test_module_stuff import FirstClass
        assert util.get_type(FirstClass.function_that_should_not_change) == 'function'

    def test_is_string(self):
        assert util.get_type('hello') == "<class 'str'>"


class TestGetters:
    def test_get_functions(self):
        from mock_functions.test_module_stuff import FirstClass
        assert util.get_functions(FirstClass)[0][0] == 'function_that_should_not_change'

    def test_get_classes(self):
        from mock_functions import test_module_stuff

        class_list = util.get_classes(test_module_stuff)
        assert all(any(class_name in item[0] for item in class_list) for class_name in ['FirstClass', 'SecondClass', 'ThirdClass'])

    def test_get_modules(self):
        import mock_functions

        module_list = util.get_modules(mock_functions.test_module_stuff)
        assert any('__loader__' in item[0] for item in module_list)
