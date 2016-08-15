from easy_python_requirements.parsed import Parsed


class TestParse:
    def test_basic_parse_attributes(self):
        from mock_functions.test_module_stuff import FirstClass

        p = Parsed(FirstClass)
        p.parse()

        assert(p.obj_type == 'class')
        assert(p.test_info.time_stamp == '2016-07-02T10:45:57.539011')
        assert(p.test_info.test_id == 4)
        assert(p.description == '\n'.join(["This is a class description",
                                           "It is multiple lines",
                                           "It should all be nicely formatted"]))

    def test_nested_parse_attributes(self):
        from mock_functions.test_module_stuff import FirstClass

        p = Parsed(FirstClass)
        p.parse()

        assert(p.children != {})
        assert('function_that_should_not_change' in p.children.keys())
        assert(p.children['function_that_should_not_change'].obj_type == 'function')

    def test_parsed_string_repr(self):
        from mock_functions.test_module_stuff import FirstClass

        p = Parsed(FirstClass)
        p.parse()

        assert(str(p) == '<Parsed: FirstClass>')
