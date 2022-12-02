import argparse
from time import sleep

from database.create_db import create_db
from database.create_index_db import index_db, reindex_db
from database.create_tables_db import create_tables_db
from database.delete_db import delete_db
from utils.db_connection import ConnectionCreator
from utils.print_colors import *


def fresh_db_setup(dbname="words_database", keep_connection=False):
    """
    Create a new database and index it
    :param dbname:
    :param keep_connection:
    :return:
    """
    delete_db(database_name=dbname, keep_alive=False)

    create_db(database_name=dbname, keep_alive=False)

    create_connection_root = ConnectionCreator(dbname=dbname)

    db_connection = create_connection_root.get_connection()

    create_tables_db(postgres_connection=db_connection, keep_alive=True)

    index_db(postgres_connection=db_connection, keep_alive=keep_connection)

    return db_connection


def existing_db_setup(db_connection, keep_connection=False):
    reindex_db(postgres_connection=db_connection, keep_alive=keep_connection)


if __name__ == "__main__":
    """
    When called directly can be used to setup one or both DB's
    """
    parser = argparse.ArgumentParser(description='Setup the PostgreSQL DB')

    parser.add_argument('-f', '--fresh-db', action="store_true", dest="fresh_database",
                        help='Whether to create a clean DB')

    parser.add_argument('-m', '--multi-bot', action="store_true", dest="multi_bot",
                        help='Whether to setup both bot databases')

    args = parser.parse_args()

    multi_bot = args.multi_bot

    if args.fresh_database:
        print(text_color("Creating fresh DB bot 1", UNDERLINE))

        fresh_db_setup(keep_connection=False)

        if multi_bot:
            print(text_color("\nCreating fresh DB bot 2", UNDERLINE))

            sleep(0.1)

            fresh_db_setup("words_database_2", keep_connection=False)
    else:
        print(text_color("Setting up existing DB bot 1", UNDERLINE))

        create_connection = ConnectionCreator()

        connection = create_connection.get_connection()

        existing_db_setup(connection, keep_connection=False)

        if multi_bot:
            create_connection_2 = ConnectionCreator(dbname="words_database_2")

            connection_2 = create_connection_2.get_connection()

            print(text_color("\nCreating fresh DB bot 2", UNDERLINE))

            sleep(0.1)

            existing_db_setup(connection_2, False)
