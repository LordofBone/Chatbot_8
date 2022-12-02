import argparse
import collections
import logging
import random
import sys
from random import randint
from time import sleep

import psycopg2

from run_container_stack import run_all
from config.bot_defaults import *
from ml.markovify.markovify_sentence_generator import MKGenerator
from utils.db_connection import ConnectionCreator
from utils.postgres_command_processor import command_processor
from utils.print_colors import *

logger = logging.getLogger("bot-logger")

name_dict = {}
prev_person = {"prev_person": ""}


def quote_fixer(text_in):
    """
    Fixes quotes in text to prevent SQL injection and other weird things
    :param text_in:
    :return:
    """
    """Escapes quotes in a string or removes newlines for insertion into the DB, to prevent errors"""
    if type(text_in) == str:
        text_in = text_in.translate({ord("'"): "''", ord("`"): "", ord("’"): ""}).rstrip()

    return text_in


def insert_db_single_field_text(connection, table, field_1, value_1, return_value_1):
    """
    Inserts a single field of text into the DB
    :param connection:
    :param table:
    :param field_1:
    :param value_1:
    :param return_value_1:
    :return:
    """
    value_1 = quote_fixer(value_1)

    logger.debug(f'Inserting text value: {value_1} into field {field_1} in table {table}')

    command = ["""WITH INPUT_ROWS({1}) AS ( 
                VALUES
                (TEXT '{2}') , ('{2}') ) , INS AS ( INSERT 
                INTO
                    {0}
                    ( {1} ) SELECT
                        * 
                    FROM
                        INPUT_ROWS 
                            ON CONFLICT ({1}) DO NOTHING RETURNING {3} ) SELECT
                            'i' AS SOURCE ,
                            {3} 
                    FROM
                        INS 
                    UNION
                    ALL SELECT
                        's' AS SOURCE ,
                        c.{3} 
                    FROM
                        INPUT_ROWS 
                    JOIN
                        {0} c USING  ({1})""".format(table, field_1, value_1, return_value_1)]

    cursor_return = command_processor(connection, command, False)

    return cursor_return


def insert_db_array(connection, table, field_1, field_2, value_1, value_2):
    """
    Inserts a array into the DB
    :param connection:
    :param table:
    :param field_1:
    :param field_2:
    :param value_1:
    :param value_2:
    :return:
    """
    value_2 = quote_fixer(value_2)

    logger.debug(
        f'Inserting array value: {value_2} into field {field_2} in table {table} with field: {field_1} as {value_1}')

    command = ["""INSERT 
                INTO
                    {0}
                    (
                        {1}, {2} 
                    ) 
                VALUES
                    ( '{3}', ARRAY [ '{4}' ] ) 
                        ON CONFLICT ( {1} ) DO UPDATE
                            
                    SET
                        {2} = ARRAY ( SELECT
                            DISTINCT UNNEST({0}.{2} || EXCLUDED.{2}))""".format(table, field_1, field_2, value_1,
                                                                                value_2)]

    command_processor(connection, command, False)


def search_db_one(connection, table, field, value):
    """
    Searches the DB for a single field
    :param connection:
    :param table:
    :param field:
    :param value:
    :return:
    """

    value = quote_fixer(value)

    command = ["""SELECT
                    * 
                FROM
                    {0} 
                WHERE
                    {0}.{1}='{2}'""".format(table, field, value)]

    cursor_return = command_processor(connection, command, True)

    return cursor_return


# todo: need to figure out how to run a search with the foreign keys setup
def db_search_fuzzy(connection, table, field_1, field_2, value_1, return_limit=1):
    """
    Searches the database for the input string using SMLAR to search for most similar results, a match is not
    found it will try again using Levenshtein, finally; if that fails - returns nothing
    :param connection:
    :param table:
    :param field_1:
    :param field_2:
    :param value_1:
    :param return_limit:
    :return:
    """
    value_1 = quote_fixer(value_1)
    # todo: find a way to add a return limit in for SMLAR? Seems at the moment it's returning many similar responses.
    command = ["""SELECT
                    SIMILARITY({1},
                    '{3}') AS SIMILARITY,
                    {2},
                    {1} 
                FROM
                    {0} 
                WHERE
                    {1} % '{3}' 
                ORDER BY
                    SIMILARITY DESC""".format(table, field_1, field_2, value_1)]

    cursor_return = command_processor(connection, command, True)

    if not cursor_return:
        logger.debug(
            f'No result found with smlar at threshold: {bot_accuracy_smlar_threshold}, performing a levenshtein '
            f'search')

        command = ["""SELECT
                        {1},
                        {3},
                        LEVENSHTEIN(
                    left({1},
                    255),
                    (left('{2}',
                    255)),
                    {5}) FROM
                        {0} 
                    ORDER BY
                        LEVENSHTEIN(
                    left({1},
                    255),
                    left('{2}',
                    255),
                    {5}) ASC LIMIT {4}""".format(table, field_1, value_1, field_2, return_limit,
                                                 bot_accuracy_lev_config)]

        cursor_return_sorter = command_processor(connection, command, True)

        # Levenshtein brings responses back in a different order than SMLAR so need to swap some values around.
        cursor_return = [(cursor_return_sorter[0][2], cursor_return_sorter[0][1], cursor_return_sorter[0][0])]

        logger.debug(
            f'DB fuzzy search (levenshtein): {cursor_return} for table: {table}, field: {field_1}, value: {value_1}')

    return cursor_return


def random_item(connection, table):
    """
    Returns a random item from the DB
    :param connection:
    :param table:
    :return:
    """
    command = ["""SELECT
                    * 
                FROM
                    {0} 
                ORDER BY
                    RANDOM() LIMIT 1""".format(table)]

    cursor_return = command_processor(connection, command, True)

    logger.debug(f'DB random item search: {cursor_return} for table: {table}')

    return cursor_return


def configure_smlar(connection):
    """
    Configures the SMLAR extension
    :param connection:
    :return:
    """
    command = ["""SELECT SET_LIMIT({0})""".format(bot_accuracy_smlar_threshold)]

    command_processor(connection, command, keep_alive=True)


class BotLoop:
    """
    The main bot loop
    """
    def __init__(self, previous_response="hello", train_mode=False, short_term_memory_limit=max_short_term_memory,
                 enable_short_term_memory=True, include_possible_replies=False,
                 bot_select="bot_1", portainer_boot=False):
        """Instantiating this bot class also allows for customisation of the short term memory, training mode (no
        replies) """

        if portainer_boot:
            run_all()

        self.words_in = ""
        self.previous_response = previous_response
        self.reply_list = []
        self.bot_reply = ""
        self.short_term_memory = collections.deque(maxlen=short_term_memory_limit)
        self.train_mode = train_mode
        self.enable_short_term_memory = enable_short_term_memory
        self.include_possible_replies = include_possible_replies
        self.mk_generator = None
        self.smart_sentence_gen = smart_reply_generation
        self.bot_select = bot_select
        self.no_db = False
        self.number_of_sentence_gen = number_of_sentence_gen
        self.db_connection = None

        self.establish_connection()

        self.mk_setup()

    def establish_connection(self):
        """
        Establishes a connection to the DB
        :return:
        """
        # Try to connect to the DB - if not DB available but a markovify model is then the bot will switch to just
        # using dynamically generated replies from the model
        try:
            logger.debug(f'Attempting to connect to DB.')

            logger.debug(f'Creating connection for {self.bot_select}.')
            if self.bot_select == "bot_1":
                create_connection = ConnectionCreator()
            elif self.bot_select == "bot_2":
                create_connection = ConnectionCreator(dbname="words_database_2")
            else:
                create_connection = ConnectionCreator()

            self.db_connection = create_connection.get_connection()
            logger.debug(f'Connection successful.')

            logger.debug(f'Configuring smlar on connection: {self.db_connection}')
            configure_smlar(self.db_connection)
            self.no_db = False
        except psycopg2.OperationalError:
            logger.debug(f'No DB found online, setting "no DB" mode.')
            self.no_db = True

    def mk_setup(self):
        """
        Sets up the markovify model
        :return:
        """
        if self.mk_generator is None:
            if not self.train_mode:
                if self.smart_sentence_gen:
                    logger.debug(f'Smart sentence generation ON, attempting to initialise markovify model')
                    try:
                        self.mk_generator = MKGenerator(self.bot_select)
                        logger.debug(f'Markovify model for {self.bot_select} initialised.')
                    except FileNotFoundError:
                        if self.no_db:
                            logger.debug(f'Markovify model for {self.bot_select} not found and no DB connection '
                                         f'available, throwing exception as bot has no ability to construct a reply.')
                            print(
                                "No Markovify model or DB found, ensure you have a PostgreSQL container/install and "
                                "that it is setup and running and ensure there is a trained Markovify model to enable "
                                "smart sentence generation.")
                        logger.debug(f'Markovify model for {self.bot_select} not found, turning smart sentence '
                                     f'generation OFF')
                        self.smart_sentence_gen = False
                else:
                    if self.no_db:
                        logger.debug(
                            f'Smart sentence generation OFF and no DB connection available, throwing exception as bot '
                            f'has no ability to construct a reply.')
                        print("No DB found, ensure you have a PostgreSQL container/install and that it is setup and "
                              "running.")
                        raise psycopg2.OperationalError

                    logger.debug(f'Smart sentence gen set to OFF but DB online, continuing on with random sentence '
                                 f'generation.')

    # todo: within a container the previous prints are not erased (probably linux issue), worked around with a long set
    #  of spaces
    def human_typing_emulator(self):
        """
        Emulates human typing, if enabled this function makes it look like another person is typing, the length of
        the string determines how long the 'typing' will happen
        :return:
        """
        sentence_words = (self.bot_reply.split())

        is_typing_name = ("\r{0} {1}".format(bot_name, "is typing..."))
        is_typing_blank = "                                                                                            "

        sleep(randint(1, 30))

        logger.debug(f'Sentence length for typing emulation: {len(sentence_words)}')
        for word in sentence_words:
            # time to type configured in config/bot_defaults.py (default: 2.7kps)
            time_to_type_word = len(word) / bot_typing_speed
            print(text_color(text_to_color=is_typing_name, color=OK_BLUE), end="")
            sleep(time_to_type_word)
            if randint(0, 100) < 5:
                print("\r{}".format(is_typing_blank), end="")
                print("\r{}".format(""), end="")
                sleep(randint(1, 3))
        print("\r{}".format(is_typing_blank), end="")
        print("\r{}".format(""), end="")

    def short_term_memory_insert(self, sentence):
        """
        Inserts a sentence into the short term memory, the bot can have a short term memory enabled, to prevent it
        from saying the same thing again too quickly and repeating itself, this is called to add the last boy reply
        into the queue :param sentence: :return:
        """
        self.short_term_memory.append(sentence)

    def short_term_memory_checker(self, sentence):
        """
        Checks the short term memory to see if the sentence is in there, if it is then it returns false, if it is not
        :param sentence:
        :return:
        """
        logger.debug(f'recent replies: {self.short_term_memory}')
        if [item for item in sentence if item in self.short_term_memory]:
            logger.debug(f'{sentence} found in replies')
            return True
        else:
            logger.debug(f'{sentence} not found in replies')
            return False

    def short_term_memory_reply_cleaner(self, list_in):
        """
        Cleans all recent replies from a reply list that was taken from a DB search
        :param list_in:
        :return:
        """
        short_term = list(self.short_term_memory)

        list_cleaned = [x for x in list_in if x not in short_term]

        return list_cleaned

    def sentence_gen(self):
        """
        Gets a result from the random sentence generator, or if smart sentence generation is True uses markovify
        to generate a sentence
        :return:
        """
        if self.smart_sentence_gen:
            logger.debug(f'Smart sentence gen ON generating sentence with markovify model')
            return self.mk_generator.generate_smart_sentence()
        else:
            logger.debug(f'Smart sentence gen OFF generating random sentence')
            return self.random_sentence_processor()

    def random_sentence_processor(self):
        """
        This creates a random sentence, by picking a random whole sentence from the database, with a 35% chance of a
        randomly generated sentence
        :return:
        """
        result = ''

        if random.randrange(100) <= 35:
            length = random.randint(1, 10)
            logger.debug(f'Generating random sentence with length: {length}')

            for i in range(length):
                word = random_item(self.db_connection, "all_words")[0][1]
                result += word
                result += ' '
        else:
            logger.debug(f'Picking random sentence from database')
            if random.randrange(100) <= 50:
                result = random_item(self.db_connection, "bot_responses")[0][1]
            else:
                result = random_item(self.db_connection, "human_replies")[0][2][0]

        return result

    def sentence_splitter(self):
        """
        Splits the sentence into a list of words and stores each word in the database
        :return:
        """
        words_in_db = self.words_in.split(' ')
        for word in words_in_db:
            insert_db_single_field_text(self.db_connection, table="all_words", field_1="word", value_1=str(word),
                                        return_value_1="word_id")

    def reply_processor(self):
        """
        This splits the sentence inputted and stores each word individually into the DB so the bot has more of a
        word pool to work with for random sentences etc. It then runs a fuzzy search on what the user inputted to
        find a similar response it has seen before. If one is found it then searches for a human reply to that
        sentence and picks it at random. If nothing is found it will generate a random sentence. If short-term memory
        is on it will store the reply into recent replies.
        :return:
        """
        recent_sentence = True
        chosen_reply = ""
        self.reply_list = []
        pre_reply_list = []

        if not self.no_db:

            self.sentence_splitter()

            search_result_all = db_search_fuzzy(self.db_connection, table="bot_responses", field_1="bot_response",
                                                field_2="bot_response_id",
                                                value_1=self.words_in)

            if not search_result_all:
                logger.debug(f'No result for fuzzy search on: {self.words_in}')

                for i in range(self.number_of_sentence_gen):
                    pre_reply_list.append(self.sentence_gen())
            elif search_result_all[0][0] > bot_accuracy_lev_threshold:
                logger.debug(
                    f'Result for fuzzy levenshtein search on: {self.words_in} with score: {search_result_all[0][0]} '
                    f'was over threshold: {bot_accuracy_lev_threshold}')
                for i in range(self.number_of_sentence_gen):
                    pre_reply_list.append(self.sentence_gen())
            else:
                logger.debug(f'Search result top match: {search_result_all[0][2]}')

                # Pass the response into the database to find prior human responses to the above sentence
                pre_reply_list = \
                    search_db_one(self.db_connection, "human_replies", "bot_response_id", search_result_all[0][1])[0][2]
                logger.debug(f'Reply list: {pre_reply_list}')
        else:
            for i in range(self.number_of_sentence_gen):
                pre_reply_list.append(self.sentence_gen())

        # Clean potential reply list of all recently said replies to prevent too often repeats.
        self.reply_list = self.short_term_memory_reply_cleaner(pre_reply_list)

        logger.debug(f'Reply list post short term memory check: {self.reply_list}')

        # If no replies left after recent reply cleaning then generate a random sentence until a new one not in
        # recent memory has been created. todo: (semi-jokey todo) unlikely but may need a workaround here to prevent
        #  a forever loop in case everything ever has been said and the short term memory is set to infinite?
        if self.reply_list:
            chosen_reply = random.choice(self.reply_list)
        else:
            while recent_sentence:
                chosen_reply = self.sentence_gen()

                recent_sentence = self.short_term_memory_checker(chosen_reply)

        if self.enable_short_term_memory:
            self.short_term_memory_insert(chosen_reply)

        return chosen_reply

    def update_db(self):
        """
        This updates the database with the inputted sentence and the reply generated by the bot
        :return:
        """
        insert_id = insert_db_single_field_text(self.db_connection, table="bot_responses", field_1="bot_response",
                                                value_1=self.previous_response,
                                                return_value_1="bot_response_id")

        # Part of the workaround for strings that are too long for unique indexes - just skip them.
        # todo: find a way to fix this with a different index that can handle it?
        if insert_id == "string_too_long":
            return

        insert_db_array(self.db_connection, table="human_replies", field_1="bot_response_id", field_2="human_reply",
                        value_1=insert_id[1],
                        value_2=self.words_in)

        self.previous_response = self.words_in

    def conversation(self, input_words):
        """
        This is the main function that runs the conversation. It takes the inputted sentence and processes it
        :param input_words:
        :return:
        """
        if not self.no_db:
            self.words_in = input_words

            self.update_db()

            # If the bot is being trained then skip the rest to save time, training only needs to insert sentences and
            # replies
            if self.train_mode:
                return

        self.bot_reply = self.reply_processor()

        if typing_emulation:
            self.human_typing_emulator()

        self.previous_response = self.bot_reply

        # This is to allow external programs importing the bot to work with all possible replies found for further
        # processing
        if self.include_possible_replies:
            return self.bot_reply, self.reply_list
        else:
            return self.bot_reply


def person_manager(person_name, bot="bot_1", portainer_boot=False):
    """
    A function for handling different people talking to the bot, when a new name is passed in a new class gets
    instantiated with their name so that the bot can keep track of different conversations between different people
    :param person_name:
    :param bot:
    :param portainer_boot:
    :return:
    """
    if person_name in name_dict:
        bot_reply = name_dict[person_name].bot_reply
        return bot_reply
    else:
        name_dict.update(
            {person_name: BotLoop(previous_response=person_name, bot_select=bot, portainer_boot=portainer_boot)})
        bot_reply = name_dict[person_name].conversation("hello")
        return bot_reply


def get_person_list():
    """
    When being imported into another system this is handy to retrieve all classes that have been instantiated
    :return:
    """
    return name_dict


if __name__ == '__main__':
    """
    When the module is called directly allow for configuration of fuzzy search thresholds etc. 
    """
    parser = argparse.ArgumentParser(description='Start a chat bot with accuracy parameters')

    parser.add_argument('-l', '--log-level', action="store", dest="log_level", type=str, default='INFO',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], help='Logging level')

    parser.add_argument('-s', '--set-smlr-threshold', action="store", dest="bot_accuracy_smlar_threshold", type=int,
                        default=0.4,
                        help='Base accuracy of responses bot should look for when using the initial smlr search ('
                             'response would need to be higher than this number)')

    parser.add_argument('-lt', '--set-lev-threshold', action="store", dest="bot_accuracy_lev_threshold", type=int,
                        default=20,
                        help='Base accuracy of responses bot should look for when using the secondary levenshtein '
                             'search (response would need to be lower than this number)')

    parser.add_argument('-lc', '--lev-config', action="store", dest="levenshtein_config", type=str, default="6, 1, 5",
                        help='Configuration of the levenshtein insertions, deletions and substitutions')

    parser.add_argument('-b', '--bot-name', action="store", dest="bot_name", type=str, default="Bot",
                        help='Name of the bot')

    parser.add_argument('-t', '--typing-emulation', action="store_true", dest="typing_emulation",
                        help='Whether to make it seem like the bot is typing replies')

    parser.add_argument('-a', '--alternate-bot', action="store_true", dest="alternate_bot",
                        help='Whether to run against words_database_2 (2nd bot)')

    parser.add_argument('-p', '--portainer-run', action="store_false", dest="portainer_run",
                        help='Whether to skip running of portainer/db container on startup')

    args = parser.parse_args()

    log_level = args.log_level
    bot_accuracy_smlar_threshold = args.bot_accuracy_smlar_threshold
    bot_accuracy_lev_threshold = args.bot_accuracy_lev_threshold
    bot_accuracy_lev_config = args.levenshtein_config
    bot_name = args.bot_name
    typing_emulation = args.typing_emulation
    alternate_bot = args.alternate_bot
    portainer_run = args.portainer_run

    logging.basicConfig(level=log_level)

    # When loading this module directly you can pass in whether to use the main DB or the alternate DB (used for
    # getting 2 different bots to converse).
    if not alternate_bot:
        bot_main = "bot_1"
    else:
        bot_main = "bot_2"

    # Request name and setup initial person to interact with the bot.
    name = input(text_color("Your name: ", GREEN))

    reply = person_manager(person_name=name, bot=bot_main, portainer_boot=portainer_run)
    print(text_color(f'{bot_name}: {reply}', OK_CYAN))

    while True:
        user_input = input(text_color(f'{name}:	', GREEN))
        # If response is blank, rerun loop.
        if user_input == "":
            continue
        # With 'change_name' typed in it will request new name, calling person_manager to handle it.
        if user_input == "change_name":
            name = input(text_color("Your name:	", GREEN))
            reply = person_manager(person_name=name, bot=bot_main)
            print(text_color(f'{bot_name}: {reply}', OK_CYAN))
            # Re-run the conversation loop with new name
            continue
        if user_input == "bye":
            # Upon typing "bye" the system will return a response and exit out after a few seconds.
            reply = name_dict[name].conversation(input_words=user_input)
            print(text_color(f'{bot_name}: {reply}', OK_CYAN))
            # main_connection.close()
            sleep(3)
            sys.exit()

        # Standard response will pass into the conversation function and print the reply.
        reply = name_dict[name].conversation(input_words=user_input)
        print(text_color(f'{bot_name}: {reply}', OK_CYAN))
