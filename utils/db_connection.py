import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from utils.yaml_loader import YAMLAccess


class ConnectionCreator:
    """This will create and return a connection; allows for connecting to a specific DB or for accessing the root
    PostgreSQL to create and destroy DB's """

    def __init__(self, port=5432, dbname="words_database", root=False):
        if root:
            self.connection = psycopg2.connect(f"user=postgres password={YAMLAccess.postgresql_password} port={port}")
        else:
            self.connection = psycopg2.connect(
                f"user=postgres password={YAMLAccess.postgresql_password} port={port} dbname={dbname}")

        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    def get_connection(self):
        return self.connection
