#!/usr/bin/env python3
# -*- coding: utf-8 -*-


config = {
    'requirement_begin': 'TEST DESCRIPTION BEGIN',
    'requirement_end': 'TEST DESCRIPTION END',
    'requirement_info': 'TEST INFO:',
}

def parse_doc(docstring):
    """
    Parse the requirement and information from a docstring

    Args:
        docstring (str): the docstring of the test function

    Returns:
        list: [requirement description, requirement info]
    """
    pass
