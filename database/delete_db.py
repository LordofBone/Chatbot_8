import argparse
from time import sleep

from utils.db_connection import ConnectionCreator
from utils.load_bar_non_iterable import progress_bar
from utils.postgres_command_processor import command_processor
from utils.print_colors import *

load_bar_mode = LOAD_BAR
load_bar_colour = '#E23838'


# todo: find out why this isn't erasing the db
@progress_bar(expected_time=1, increments=100, description=text_color("Erasing DB", RED), ascii_bar=load_bar_mode,
              colour_bar_set=load_bar_colour)
def delete_db(database_name="words_database", keep_alive=False):
    """Erases entire DB by name passed in """
    root_connection = ConnectionCreator(root=True)
    postgres_connection = root_connection.get_connection()

    commands = [
        """DROP DATABASE IF EXISTS {0}""".format(database_name)
    ]

    command_processor(postgres_connection, commands, keep_alive)


if __name__ == "__main__":
    """When called directly can be used to delete one or both DB's """
    parser = argparse.ArgumentParser(description='Deletes the entire PostgreSQL DB')

    parser.add_argument('-r', '--reindex', action="store_true", dest="reindex", help='Will reindex existing '
                                                                                     'indexes instead of '
                                                                                     'creating new')

    parser.add_argument('-m', '--multi-bot', action="store_true", dest="multi_bot",
                        help='Whether to setup both bot databases')

    args = parser.parse_args()

    multi_bot = args.multi_bot

    print(text_color("Deleting DB bot 1", UNDERLINE))

    delete_db()

    if multi_bot:
        print(text_color("\nDeleting DB bot 2", UNDERLINE))

        sleep(0.1)

        delete_db(database_name="words_database_2")
