import os

not_found_error = 404
permission_error = 403
ok_status = 200
success_message = 'Success!'


def check_dir_existence(directory):
    """
    Checking directories existence

    :param directory: list of directories
    :return: None if ok or list of errors
    """
    if os.path.isdir(directory) is False:
        try:
            os.makedirs(directory)
        except PermissionError as error:
            return str(error), permission_error
    return success_message, ok_status


def check_file_existence(file):
    """
    Checking files existence

    :param files: list of files
    :return: None if ok or list of errors
    """
    if os.path.isfile(file) is False:
        return not_found_error
    return
