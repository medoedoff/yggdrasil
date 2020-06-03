import os
import requests


def check_package_dir_existence(directory):
    """
    Checking directories existence
    if does not exists will create

    :param directory: str of directories
    :return: None if ok
    """
    if os.path.isdir(directory) is False:
        os.makedirs(directory)
    return


def check_package_existence(base_path, base_url):
    """
    Checking package existence
    if does not exists will download

    :param base_path: str path to package
    :param base_url: str url
    :return: None if ok
    """
    if os.path.isfile(base_path) is False:
        response = requests.get(base_url)
        with open(base_path, 'wb') as file:
            file.write(response.content)
    return
