import json
import logging
import sys
from datetime import datetime

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

config = {
    'requirement_begin': 'TEST DESCRIPTION BEGIN',
    'requirement_end': 'TEST DESCRIPTION END',
    'requirement_info': 'TEST INFO:',
    'info_format': ['test_id', 'time_stamp'],
}

highest_id = 0


def create_json_info():
    global highest_id

    highest_id += 1
    test_id = highest_id

    time_stamp = str(datetime.today().isoformat())

    return json.dumps({'test_id': test_id, 'time_stamp': time_stamp})


def read_json_info(test_info_line: str):
    """
    Essentially the reverse of create_json_info.
    Gets the json info from a line.

    Args:
        test_info_line (str): The line containing the json info

    Returns:
        dict: JSON info dictionary
    """
    return json.loads(':'.join(test_info_line.split(':')[1:]))


def append_json_info(filename, index, value):
    """
    Append the json info to the correct line in the file.

    Args:
        index (int): The line number to append to.
        value (str): The item to append to the line
        previous_info (dict): The previous info in the dictionary
            TODO: Use this

    Returns:
        None
    """
    with open(filename, "r") as f:
        contents = f.readlines()

    logger.debug('Appending {0} to line {1} of {2}'.format(
        value,
        index,
        filename
    ))
    contents[index] = contents[index].replace('\n', '') + ' ' + value + '\n'

    with open(filename, "w") as f:
        f.writelines(contents)


def info_line_status(doclist, info_index):
    """
    Determine the attributes of the info line

    Args:
        doclist (list): The docstring -> list
        info_index (int): The index to begin checking at

    Returns:
        dict: Information dictionary, specifying important info
    """
    global highest_id
    info_dict = {}

    # If the test info line contains just a place holder
    if doclist[info_index] == config['requirement_info']:
        info_dict['requires_update'] = True
    else:
        # Proper info is automatically recorded in JSON,
        #   so if it doesn't properly load into JSON then it's wrong
        try:
            info_json = json.loads(doclist[info_index].split(config['requirement_info'])[1])

            if all(x in info_json.keys() for x in config['info_format']):
                info_dict['requires_update'] = False
            else:
                info_dict['requires_update'] = True
        except ValueError:
            info_dict['requires_update'] = True

    # Get info if it doesn't need to be updated
    if info_dict['requires_update'] is False:
        info_dict['test_info'] = {}
        for key in info_json.keys():
            info_dict['test_info'][key] = info_json[key]

        # Any specific cleanup required
        # print(info_dict)
        highest_id = max(info_dict['test_info']['test_id'], highest_id)

    return info_dict


# }}}
