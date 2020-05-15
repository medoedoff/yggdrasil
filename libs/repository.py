class Index:
    def __init__(self, package_name):
        """
        :param package_name: str package name
        """
        self.package_name = package_name.lower()

    def _update(self):
        pass

    def _create(self):
        pass

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

    def is_exist(self):
        pass
