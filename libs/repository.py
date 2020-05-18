import os
import json


class Index:
    def __init__(self, package_name, package_info, index_path):
        """
        :param package_name: str package name
        :param index_path: str path to index directory
        """
        self.package_name = package_name.lower()
        self.index_path = index_path
        self.package_info = package_info

    def _update(self, package_index_path):
        path_to_save = f'{package_index_path}'
        package_info = self.package_info
        with open(path_to_save, 'a') as json_file:
            json_file.write(json.dumps(package_info))

    def _create(self, package_index_path):
        path_to_save = f'{package_index_path}'
        package_info = self.package_info
        with open(path_to_save, 'w') as json_file:
            json_file.write(json.dumps(package_info))

    def _divide_string(self):
        """
        for more information visit https://doc.rust-lang.org/cargo/reference/registries.html#index-format
        :return: divided_string for example 'td/s-/tds-package'
        """
        package_name = self.package_name
        length = len(package_name)
        if length <= 2:
            divided_string = f'{length}/{package_name}'
            return divided_string
        elif length == 3:
            divided_string = f'{length}/{package_name[0]}/{package_name}'
            return divided_string
        else:
            divided_string = f'{package_name[0:2]}/{package_name[2:4]}/{package_name}'
            return divided_string

    def synchronise(self):
        package_index = self._divide_string()
        index_path = self.index_path
        package_name = self.package_name
        package_index_path = f'{index_path}/{package_index}/{package_name}'
        if os.path.isfile(package_index_path) is False:
            self._create()
        else:
            self._update()
        return
