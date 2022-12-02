from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class YAMLData:
    """
    This class will load the YAML file and return the data as a class.
    """
    postgresql_password: str = ""

    def __post_init__(self):
        path = Path(__file__).parent / "../config/postgresql_config.yaml"

        with open(path) as file:
            documents = yaml.full_load(file)

            self.postgresql_password = documents['db_password']


# Instantiates the yaml dataclass so that other modules can import it and use the latest yaml data
YAMLAccess = YAMLData()

if __name__ == "__main__":
    """
    This will print the yaml data to the console.
    """
    print(YAMLAccess.postgresql_password)
