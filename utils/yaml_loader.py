from dataclasses import dataclass
from pathlib import Path

import yaml


# todo need to figure out a way to make the folders here be able to work in the root folder of another project if
#  installed via pip install (rather than -e for editable) or imported.
@dataclass
class YAMLData:
    """Parses out the YAML data and stores it for use by other modules """
    postgresql_password: str = ""

    def __post_init__(self):
        path = Path(__file__).parent / "../config/postgresql_config.yaml"

        with open(path) as file:
            documents = yaml.full_load(file)

            self.postgresql_password = documents['db_password']


# Instantiates the yaml dataclass so that other modules can import it and use the latest yaml data
YAMLAccess = YAMLData()

if __name__ == "__main__":
    # Perform a test by parsing yaml file and printing the data
    print(YAMLAccess.postgresql_password)
