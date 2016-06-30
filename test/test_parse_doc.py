#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from easy_python_requirements import parse_doc


class TestParseDoc:
    def test_parse_doc_no_result(self):
        docstring = """
        This has got nothing important in it.
        Move along
        """
        assert(parse_doc(docstring) == [None,
                                        {'requires_update': False}
                                        ])

    def test_parse_doc_empty_info(self):
        docstring = """
        This one has no information
        TEST DESCRIPTION BEGIN
        But it does have some description
        TEST DESCRIPTION END
        """
        assert(parse_doc(docstring) == ['But it does have some description',
                                        {'requires_update': True}
                                        ])

    def test_parse_doc_existing_info(self):
        docstring = """
        This one has info
        TEST INFO: at least something is here
        TEST DESCRIPTION BEGIN
        Also with description
        TEST DESCRIPTION END
        """
        desc, requirement_info = parse_doc(docstring)

        assert(desc == 'Also with description')
        assert(requirement_info['requires_update'] is True)

        docstring = """
        This one has almost valid info
        TEST INFO: {"bad_id": 6}
        TEST DESCRIPTION BEGIN
        This is bad
        TEST DESCRIPTION END
        """
        desc, requirement_info = parse_doc(docstring)

        assert(desc == 'This is bad')
        assert(requirement_info['requires_update'] is True)

        docstring = """
        This one has valid info
        TEST INFO: {"test_id": 6}
        TEST DESCRIPTION BEGIN
        This is good
        TEST DESCRIPTION END
        """
        desc, requirement_info = parse_doc(docstring)

        assert(desc == 'This is good')
        assert(requirement_info['requires_update'] is False)

    def test_parse_doc_no_begin(self):
        pass

    def test_parse_doc_no_end(self):
        pass

    def test_parse_doc_correct(self):
        pass
