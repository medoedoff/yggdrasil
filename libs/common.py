import os
import requests

error_status = 406
permission_error = 403
ok_status = 200
success_message = 'Success!'


def check_dir_existence(directory):
    """
    Checking directories existence

    :param directory: str of directories
    :return: None if ok or list of errors
    """
    if os.path.isdir(directory) is False:
        try:
            os.makedirs(directory)
        except (PermissionError, OSError, IOError) as error:
            return str(error), error_status
    return success_message, ok_status


def check_file_existence(file):
    """
    Checking files existence

    :param file: str of files
    :return: None if ok or list of errors
    """
    base_path = 'packages/{}'.format(file)
    base_url = 'https://crates.io/api/v1/crates/{}'.format(file)
    if os.path.isfile(file) is False:
        response = requests.get(base_url)
        try:
            with open(base_path, 'wb') as file:
                file.write(response.content)
        except (PermissionError, OSError, IOError) as error:
            return str(error), error_status
    return success_message, ok_status
