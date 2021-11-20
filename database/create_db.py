import argparse
from time import sleep

from utils.db_connection import ConnectionCreator
from utils.load_bar_non_iterable import progress_bar
from utils.postgres_command_processor import command_processor
from utils.print_colors import *

load_bar_mode = LOAD_BAR
load_bar_colour = '#F78200'


@progress_bar(expected_time=1, increments=100, description=text_color("Creating DB", ORANGE), ascii_bar=load_bar_mode,
              colour_bar_set=load_bar_colour)
def create_db(database_name="words_database", keep_alive=False):
    """Create database, configurable to make different name databases on the same PostgreSQL instance """
    root_connection = ConnectionCreator(root=True)
    postgres_connection = root_connection.get_connection()

    commands = [
        """CREATE DATABASE {0}""".format(database_name)
    ]

    command_processor(postgres_connection, commands, keep_alive)


if __name__ == "__main__":
    """When called directly this can be used to create one bot DB or two (for getting two bots to talk to each other) 
    """
    parser = argparse.ArgumentParser(description='Create DB on PostgreSQL')

    parser.add_argument('-m', '--multi-bot', action="store_true", dest="multi_bot",
                        help='Whether to setup both bot databases')

    args = parser.parse_args()

    multi_bot = args.multi_bot

    print(text_color("Creating DB bot 1", UNDERLINE))

    create_db()

    if multi_bot:
        print(text_color("\nCreating DB bot 2", UNDERLINE))

        sleep(0.1)

        create_db(database_name="words_database_2")
