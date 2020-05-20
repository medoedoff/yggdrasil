import os
import json
import string

conflict_status = 409
success_status = 200


class Index:
    def __init__(self, package_name, package_info, index_path):
        """
        :param package_name: str package name
        :param index_path: str path to index directory
        :param package_info: json information about package
        """
        self.package_name = package_name.lower()
        self.index_path = index_path
        self.package_info = package_info

    def _divide_string(self):
        """
        for more information visit https://doc.rust-lang.org/cargo/reference/registries.html#index-format
        :return: divided_string for example 'td/s-/tds-package'
        """
        package_name = self.package_name
        length = len(package_name)
        if length <= 2:
            divided_string = f'{length}'
            return divided_string
        elif length == 3:
            divided_string = f'{length}/{package_name[0]}'
            return divided_string
        else:
            divided_string = f'{package_name[0:2]}/{package_name[2:4]}'
            return divided_string

    def _create(self, path_to_save_package_info):
        package_info = self.package_info
        package_info = json.dumps(package_info)
        # Remove all whitespaces
        package_info = package_info.translate({ord(package_info): None for package_info in string.whitespace})
        with open(path_to_save_package_info, 'w') as json_file:
            json_file.write(package_info)
            json_file.write('\n')
        return

    def _update(self, path_to_save_package_info):
        package_info = self.package_info
        package_info = json.dumps(package_info)
        # Remove all whitespaces
        package_info = package_info.translate({ord(package_info): None for package_info in string.whitespace})
        with open(path_to_save_package_info, 'a') as json_file:
            json_file.write(package_info)
            json_file.write('\n')
        return

    def synchronise(self):
        """
        :return: 200 package created
        :return: 200 package updated
        :return: 409 current package version already exists
        """
        package_index = self._divide_string()
        package_info = self.package_info
        index_path = self.index_path
        package_name = self.package_name
        package_index_path = f'{index_path}/{package_index}'
        path_to_save_package_info = f'{index_path}/{package_index}/{package_name}'
        if os.path.isfile(path_to_save_package_info) is False:
            os.makedirs(package_index_path)
            self._create(path_to_save_package_info)
            return success_status
        else:
            with open(path_to_save_package_info) as file:
                for line in file.readlines():
                    current_package_info = json.loads(line)
                    if current_package_info['vers'] == package_info['vers']:
                        return conflict_status
            self._update(path_to_save_package_info)
            return success_status


class ReformatPackageJson:
    """
    Reformatting package meta information to correct view for indexes
    """

    def __init__(self, package_metadata, package_hash):
        self.package_metadata = package_metadata
        self.package_hash = package_hash

    def _reformat_deps(self):
        package_metadata = self.package_metadata
        list_of_deps = list()
        package_dependency_structure = {
            'name': str(),
            'req': str(),
            'features': list(),
            'optional': bool(),
            'default_features': bool(),
            'target': str(),
            'kind': str()
        }

        for obj in package_metadata['deps']:
            for key, value in obj.items():
                if key in package_dependency_structure:
                    package_dependency_structure[key] = value
                if key == 'version_req':
                    package_dependency_structure['req'] = value
            list_of_deps.append(package_dependency_structure.copy())

        return list_of_deps

    def reformat(self):
        package_metadata = self.package_metadata
        package_hash = self.package_hash

        package_structure = {
            'name': str(),
            'vers': str(),
            'deps': list(),
            'features': dict(),
            'cksum': str(),
            'yanked': False,
            'links': str()
        }

        for key, value in package_metadata.items():
            if key in package_structure:
                package_structure[key] = value

        package_structure['cksum'] = package_hash

        if len(package_metadata['deps']) > 0:
            deps = self._reformat_deps()
            package_structure['deps'] = deps

        return package_structure


class SavePackage:
    def __init__(self, path_to_save, package_data):
        self.path_to_save = path_to_save
        self.package_data = package_data

    def save(self):
        path_to_save = self.path_to_save
        package_data = self.package_data
        with open(path_to_save, 'wb') as package:
            package.write(package_data)
        return
