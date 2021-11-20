import argparse
from time import sleep

from utils.db_connection import ConnectionCreator
from utils.load_bar_non_iterable import progress_bar
from utils.postgres_command_processor import command_processor
from utils.print_colors import *

load_bar_mode = LOAD_BAR
load_bar_colour = '#FFB900'


@progress_bar(expected_time=1, increments=100, description=text_color("Creating tables on DB", YELLOW),
              ascii_bar=load_bar_mode, colour_bar_set=load_bar_colour)
def create_tables_db(postgres_connection, keep_alive=False):
    """Create tables in the PostgreSQL database """

    commands = (
        """
        CREATE TABLE IF NOT EXISTS bot_responses(
           bot_response_id INT GENERATED ALWAYS AS IDENTITY,
           bot_response TEXT CONSTRAINT response_unique UNIQUE,
           PRIMARY KEY(bot_response_id)
        )""",

        """CREATE TABLE IF NOT EXISTS human_replies(
           human_reply_id INT GENERATED ALWAYS AS IDENTITY,
           bot_response_id INT CONSTRAINT response_unique_reply UNIQUE,
           human_reply text[] NOT NULL,
           PRIMARY KEY(human_reply_id),
           CONSTRAINT fk_bot_responses
              FOREIGN KEY(bot_response_id) 
              REFERENCES bot_responses(bot_response_id)
        )""",

        """CREATE TABLE IF NOT EXISTS all_words(
           word_id INT GENERATED ALWAYS AS IDENTITY,
           word TEXT CONSTRAINT response_unique_word UNIQUE
        )""",

        """CREATE EXTENSION IF NOT EXISTS pg_trgm""",
        """CREATE EXTENSION IF NOT EXISTS btree_gin""",
        """CREATE EXTENSION IF NOT EXISTS smlar""",
        """CREATE EXTENSION IF NOT EXISTS fuzzystrmatch"""
    )

    command_processor(postgres_connection, commands, keep_alive)


if __name__ == "__main__":
    """When called directly can be used to create tables on one or both DB's """
    parser = argparse.ArgumentParser(description='Create tables on the PostgreSQL DB')

    parser.add_argument('-r', '--reindex', action="store_true", dest="reindex", help='Will reindex existing '
                                                                                     'indexes instead of '
                                                                                     'creating new')

    parser.add_argument('-m', '--multi-bot', action="store_true", dest="multi_bot",
                        help='Whether to setup both bot databases')

    args = parser.parse_args()

    multi_bot = args.multi_bot

    create_connection = ConnectionCreator()

    connection = create_connection.get_connection()

    print(text_color("Creating tables on DB bot 1", UNDERLINE))

    sleep(0.1)

    create_tables_db(connection)

    if multi_bot:
        create_connection_2 = ConnectionCreator(dbname="words_database_2")

        connection_2 = create_connection_2.get_connection()

        print(text_color("\nCreating tables on DB bot 2", UNDERLINE))

        sleep(0.1)

        create_tables_db(connection_2)
