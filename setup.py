from distutils.core import setup

long_description = '''Write your requirements in your tests. This way your requirements and your tests
are right next to each other! Easy to reaad and keep up-to-date.'''

setup(
    name='easy_python_requirements',
    packages=['easy_python_requirements'],
    version='0.1',
    description='Requirements in tests!',
    long_description=long_description,
    author='TJ DeVries',
    author_email='devries.timothyj@gmail.com',
    url='https://github.com/tjdevries/easy_python_requirements',
    download_url='https://github.com/tjdevries/easy_python_requirements/tarball/0.1',
    keywords=['testing', 'requirements', 'easy'],
    license='MIT',
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest',],
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
