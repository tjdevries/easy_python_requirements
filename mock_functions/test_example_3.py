#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class FirstClassExample:
    def function_that_should_not_change(self):
        """
        TEST INFO:
        TEST DESCRIPTION BEGIN
        This should never be touched
        TEST DESCRIPTION END
        Other stuff here
        """
        pass


class SecondClassExample:
    """
    TEST INFO:
    TEST DESCRIPTION BEGIN
    This class shall demonstrate changing its functions!
    TEST DESCRIPTION END
    """
    def this_doc_string_should_change(self):
        """
        TEST INFO:
        TEST DESCRIPTION BEGIN
        This is the only info that should be read or changed
        TEST DESCRIPTION END
        """
        pass


class ThirdClassExample:
    def this_should_be_ignored(self):
        """
        TEST INFO:
        TEST DESCRIPTION BEGIN
        Really does not matter
        TEST DESCRIPTION END
        """
        pass
