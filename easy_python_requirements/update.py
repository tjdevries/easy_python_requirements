import inspect
import logging
import sys
import os
import importlib
import pkgutil
from collections import OrderedDict

from easy_python_requirements import config
from easy_python_requirements.parsed import Parsed
from easy_python_requirements.test_info import (
    create_json_info, append_json_info
)
from easy_python_requirements.util import (
    get_source_lines, get_classes, get_functions, get_depth_of_file
)

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()  # noqa
logger.setLevel(logging.INFO)


def update_func(function):
    """
    Update the info for a function

    Args:
        f (function): The function to update

    Returns:
        dict: function information
            test_id: id of the function encountered
    """
    parsed = Parsed(function)
    parsed.parse()

    info_dict = parsed.test_info
    if not parsed.requires_update:
        return info_dict

    filename = inspect.getfile(function)
    with open(filename, 'r+') as location:
        for index, line in enumerate(location.readlines()):
            # We have not reached the function yet
            if index < function.__code__.co_firstlineno:
                continue

            if 'TEST INFO' in line:
                test_info_index = index
                break

    new_json = create_json_info()
    append_json_info(filename, test_info_index, new_json)

    return new_json


def update_class(cls):
    """
    Update the info for a class

    Returns:
        None
    """
    parsed = Parsed(cls)
    parsed.parse()

    if not parsed.requires_update:
        return

    filename = inspect.getfile(cls)

    with open(filename, 'r+') as location:
        lines = location.readlines()

    first_line, last_line = get_source_lines(lines, cls)

    with open(filename, 'r+') as location:
        for index, line in enumerate(location.readlines()[first_line:last_line]):
            if config['requirement_info'] in line:
                test_info_index = index + first_line
                break

    append_json_info(filename, test_info_index, create_json_info())


def update_file(filename):
    """
    Get, parse and update the file with the correct info
    """
    explored = ExploredFile(filename)
    explored.explore()

    for c_name, c_value in explored.module.items():
        update_class(c_name)
        for _, f_value in c_value.items():
            update_func(f_value)

    for _, f_value in explored.function.items():
        update_func(f_value)


def update_folder(path, recursive=True):
    explored = explore_folder(path, recursive)
    # pprint(explored)

    for name in explored.keys():
        update_file(name)

    return


class ExploredFile:
    def __init__(self, filename):
        if filename[0:2] == './' or filename[0:2] == '.\\':
            filename = filename[2:]
        self.filename = filename
        self.mod_name = filename.replace('/', '.').replace('\\', '.')[:-3]

        logger.debug('Importing filename %s from filename %s with cwd: %s', self.mod_name, self.filename, str(os.getcwd()))
        self.imported_module = importlib.import_module(self.mod_name)

        self.module = OrderedDict()
        self.function = OrderedDict()

    def explore(self):
        """
        Explore the file and update any internal attributes required

        Returns: None
        """
        for _, c_member in self.classes:
            current = OrderedDict()
            Parsed(c_member).parse()
            for f_name, f_member in get_functions(c_member):
                current[f_name] = f_member
                Parsed(f_member).parse()

            self.module[c_member] = current

        for f_name, f_member in get_functions(self.imported_module):
            self.function[f_name] = f_member

    @property
    def classes(self):
        """
        Return a list of tuples containing the name and a member of the classes

        Returns:
            list: Of the form [ (c_name, c_member), (c_name, c_member), ... ]
        """
        return get_classes(self.imported_module)


def explore_folder(foldername: str, recursive=True):
    files_to_load = []
    explored = OrderedDict()

    logger.debug('Exploring folder %s from folder %s', foldername, str(os.getcwd()))
    for load, name, is_pkg in pkgutil.walk_packages([foldername]):
        if not recursive and is_pkg:
            continue

        if is_pkg:
            path = load.path + name + os.sep
            logger.debug(path)
            temp_explored = explore_folder(path)
            for key, value in temp_explored.items():
                explored[key] = value
                # explored.move_to_end(key)
        else:
            files_to_load.append(load.path + name + '.py')

    for current_file in files_to_load:
        logger.info('File: %s', str(current_file))
        temp = ExploredFile(current_file)
        temp.explore()
        explored[current_file] = temp

    # TODO: Get the order sorted by files, then directories
    explored = OrderedDict(sorted(explored.items(), key=lambda x: get_depth_of_file(x[0])))

    return explored
