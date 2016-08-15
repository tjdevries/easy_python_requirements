#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from easy_python_requirements.parsed import parse_doc
from easy_python_requirements.exceptions import MultipleStringError


class TestParseDoc:
    def test_parse_doc_no_result(self):
        docstring = """
        This has got nothing important in it.
        Move along
        """
        assert(parse_doc(docstring) == {'requires_update': False, 'description': None})

    def test_parse_doc_empty_info(self):
        docstring = """
        This one has no information
        TEST DESCRIPTION BEGIN
        But it does have some description
        TEST DESCRIPTION END
        """
        assert(parse_doc(docstring) == {'description': 'But it does have some description', 'requires_update': True})

    def test_parse_doc_existing_info(self):
        docstring = """
        This one has info
        TEST INFO: at least something is here
        TEST DESCRIPTION BEGIN
        Also with description
        TEST DESCRIPTION END
        """
        requirement_info = parse_doc(docstring)
        desc = requirement_info['description']

        assert(desc == 'Also with description')
        assert(requirement_info['requires_update'] is True)

        docstring = """
        This one has almost valid info
        TEST INFO: {"bad_id": 6}
        TEST DESCRIPTION BEGIN
        This is bad
        TEST DESCRIPTION END
        """
        requirement_info = parse_doc(docstring)
        desc = requirement_info['description']

        assert(desc == 'This is bad')
        assert(requirement_info['requires_update'] is True)

    def test_parse_doc_no_begin(self):
        docstring = """
        This doesn't have a begin
        TEST INFO: {"test_id": 6, "time_stamp": "2016-06-30T13:51:04.061138"}
        This is not good.
        TEST DESCRIPTION END
        """
        requirement_info = parse_doc(docstring)
        desc = requirement_info['description']
        print(desc)

    def test_parse_doc_no_end(self):
        docstring = """
        This does have a begin.
        But it does not have an end
        TEST INFO: {"test_id": 6, "time_stamp": "2016-06-30T13:51:04.061138"}
        TEST DESCRIPTION BEGIN
        Some information but this isn't good
        """
        requirement_info = parse_doc(docstring)
        desc = requirement_info['description']
        print(desc)

    def test_parse_doc_correct(self):
        docstring = """
        This one has valid info
        TEST INFO: {"test_id": 6, "time_stamp": "2016-06-30T13:51:04.061138"}
        TEST DESCRIPTION BEGIN
        This is good
        TEST DESCRIPTION END
        """
        requirement_info = parse_doc(docstring)
        desc = requirement_info['description']

        assert(desc == 'This is good')
        assert(requirement_info['requires_update'] is False)

    def test_parse_double_info(self):
        # Test double test info, one valid
        docstring = """
        This one has valid info
        TEST INFO: {"test_id": 6, "time_stamp": "2016-06-30T13:51:04.061138"}
        TEST INFO:
        TEST DESCRIPTION BEGIN
        This is good
        TEST DESCRIPTION END
        """
        with pytest.raises(MultipleStringError):
            requirement_info = parse_doc(docstring)

        # Test double test info, one valid
        docstring = """
        This one has valid info
        TEST INFO:
        TEST INFO: {"test_id": 6, "time_stamp": "2016-06-30T13:51:04.061138"}
        TEST DESCRIPTION BEGIN
        This is good
        TEST DESCRIPTION END
        """
        with pytest.raises(MultipleStringError):
            requirement_info = parse_doc(docstring)
            print(requirement_info)

    def test_parse_double_begin(self):
        docstring = """
        This one has valid info
        TEST INFO: {"test_id": 6, "time_stamp": "2016-06-30T13:51:04.061138"}
        TEST DESCRIPTION BEGIN
        TEST DESCRIPTION BEGIN
        This is good
        TEST DESCRIPTION END
        """
        requirement_info = parse_doc(docstring)
        print(requirement_info)

    def test_parse_double_end(self):
        docstring = """
        This one has valid info
        TEST INFO: {"test_id": 6, "time_stamp": "2016-06-30T13:51:04.061138"}
        TEST DESCRIPTION BEGIN
        This is good
        TEST DESCRIPTION END
        TEST DESCRIPTION END
        """
        requirement_info = parse_doc(docstring)
        print(requirement_info)
