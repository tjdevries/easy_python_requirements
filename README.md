# easy_python_requirements

[![Coverage Status](https://coveralls.io/repos/github/tjdevries/easy_python_requirements/badge.svg?branch=master)](https://coveralls.io/github/tjdevries/easy_python_requirements?branch=master)
[![Build Status](https://travis-ci.org/tjdevries/easy_python_requirements.svg?branch=master)](https://travis-ci.org/tjdevries/easy_python_requirements)
[![Code Health](https://landscape.io/github/tjdevries/easy_python_requirements/master/landscape.svg?style=flat)](https://landscape.io/github/tjdevries/easy_python_requirements/master)

Light program to specify test requirements in the docstring of a test and get easy documentation.

This package was designed to combat those times where you want to track some basic information about the tests (particularly functional tests) in a project, but don't want to spend a lot of time editing markdown documents, managing / tracking information and overall feel like you're wasting time.

`easy_python_requirements` aims to fix that having you write your documentation while you write your tests, and outputting any necessary information that you need to link, track and analyze the requirements set out by your team. Perhaps this is best shown by example.

## Examples

```python
from my_package import this_feature

def test_this_feature():
    """
    You can insert some test up here, that won't get tracked

    TEST INFO:
    TEST DESCRIPTION BEGIN
    - This feature **shall** do the things it needs to.
        - This feature **shall** always work.
    TEST DESCRIPTION END
    """
    assert(this_feature.do == 'DONE')
```

After running `easy_python_requirements`, first it will update the test info, so the test will appear as the following:

```python
from my_package import this_feature

def test_this_feature():
    """
    You can insert some test up here, that won't get tracked

    TEST INFO: {'test_id': 1, 'time_stamp: today}
    TEST DESCRIPTION BEGIN
    - This feature **shall** do the things it needs to.
        - This feature **shall** always work.
    TEST DESCRIPTION END
    """
    assert(this_feature.do == 'DONE')
```

and then it will output your test specifications:

```YAML
test_id: 1
    description: |
        - This feature **shall** do the things it needs to.
            - This feature **shall** always work.
    time_stamp: 'today'
```

Using `easy_python_requirements` lets you quickly write tests with very little boilerplate and have all your documentation, requirements tracking and testing done in the same place.
