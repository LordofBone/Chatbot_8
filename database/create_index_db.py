import argparse
from time import sleep

from utils.db_connection import ConnectionCreator
from utils.load_bar_non_iterable import progress_bar
from utils.postgres_command_processor import command_processor
from utils.print_colors import *

load_bar_mode = LOAD_BAR
load_bar_colour_1 = '#5EBD3E'
load_bar_colour_2 = '#973999'


@progress_bar(expected_time=1, increments=100, description=text_color("Creating indexes on DB", GREEN),
              ascii_bar=load_bar_mode, colour_bar_set=load_bar_colour_1)
def index_db(postgres_connection, keep_alive=False):
    """Create indexes on the existing database """
    commands = (
        """CREATE INDEX IF NOT EXISTS bot_response_index 
                ON bot_responses USING GIN (to_tsvector('english',
            bot_response))""",

        """CREATE INDEX IF NOT EXISTS human_reply_index 
                ON human_replies (bot_response_id)""",

        """CREATE INDEX IF NOT EXISTS all_words_index 
                ON all_words USING GIN (to_tsvector('english',
            word))"""
    )

    command_processor(postgres_connection, commands, keep_alive)


@progress_bar(expected_time=1, increments=100, description=text_color("Reindexing DB", PURPLE), ascii_bar=load_bar_mode,
              colour_bar_set=load_bar_colour_2)
def reindex_db(postgres_connection, keep_alive=False):
    commands = (
        """REINDEX TABLE bot_responses""",
        """REINDEX TABLE human_replies""",
        """REINDEX TABLE all_words"""
    )

    command_processor(postgres_connection, commands, keep_alive)


if __name__ == "__main__":
    """When called directly this can create indexes on on DB or both """
    parser = argparse.ArgumentParser(description='Create indexes on DB or if DB already exists reindex existing')

    parser.add_argument('-r', '--reindex', action="store_true", dest="reindex", help='Will reindex existing '
                                                                                     'indexes instead of '
                                                                                     'creating new')

    parser.add_argument('-m', '--multi-bot', action="store_true", dest="multi_bot",
                        help='Whether to setup both bot databases')

    args = parser.parse_args()

    multi_bot = args.multi_bot

    create_connection = ConnectionCreator()

    connection = create_connection.get_connection()

    if args.reindex:
        print(text_color("Reindexing DB bot 1", UNDERLINE))

        reindex_db(connection)
        if multi_bot:
            create_connection_2 = ConnectionCreator(dbname="words_database_2")

            connection_2 = create_connection_2.get_connection()

            print(text_color("\nReindexing DB bot 2", UNDERLINE))

            sleep(0.1)

            reindex_db(connection_2)
    else:
        print(text_color("Indexing DB bot 1", UNDERLINE))

        index_db(connection)
        if multi_bot:
            create_connection_2 = ConnectionCreator(dbname="words_database_2")

            connection_2 = create_connection_2.get_connection()

            print(text_color("\nIndexing DB bot 2", UNDERLINE))

            sleep(0.1)

            index_db(connection_2)
