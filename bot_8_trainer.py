import argparse
import logging
import os
from pathlib import Path
from time import sleep

from tqdm.auto import tqdm

from bot_8 import BotLoop
from database.setup_db import fresh_db_setup, existing_db_setup
from ml.markovify.markovify_trainer import mk_trainer
from utils.db_connection import ConnectionCreator
from utils.print_colors import *

logger = logging.getLogger("bot-trainer-logger")

load_bar_mode = LOAD_BAR
load_bar_colour = '#009CDF'


# todo need to figure out a way to make the folders here be able to work in the root folder of another project if
#  installed via pip install (rather than -e for editable) or imported.

def bot_trainer(dbname="words_database", fresh_db=False, directory=r'training', bot_id_mk="bot_1"):
    """This will train a bot using all .txt files under the training folders (data/training and data/training_2) """
    if fresh_db:
        connection = fresh_db_setup(dbname=dbname, keep_connection=False)
    else:
        create_connection = ConnectionCreator(dbname=dbname)

        connection = create_connection.get_connection()

    bot = BotLoop(train_mode=True, bot_select=bot_id_mk)

    training_path = Path(__file__).parent / f"data/{directory}/"

    # This determines the line count of all the training files in the training folder.
    line_count_total = 0
    training_file_names = []
    for filename in os.listdir(f'{training_path}'):
        if filename.endswith(".txt"):
            training_file_names.append(filename)
            with open(f'{training_path}/{filename}', encoding="ISO-8859-1") as f:
                line_count_file = sum(1 for _ in f)
                line_count_total = line_count_total + line_count_file
        else:
            continue

    if not training_file_names:
        raise Exception(f"No files in the {directory} folder, please add .txt files with line-by-line conversations")

    # Begin training with a loading bar to indicate the status of the DB and training.
    with tqdm(total=line_count_total, postfix=text_color("Training", CYAN), leave=True, ascii=load_bar_mode,
              colour=load_bar_colour, dynamic_ncols=True) as progress_bar:
        for filename in training_file_names:
            training_file = open(f'{training_path}/{filename}', "r", encoding="ISO-8859-1")

            for sentence_in in training_file:
                progress_bar.update(1)
                # If the start of a sentence is not alphanumeric then skip it.
                if not sentence_in[0].isalnum():
                    continue
                # Split sentences via ':' and get the last item; this is handy for parsing movie scripts and avoiding
                # character names.
                try:
                    sentence_in = str(sentence_in.split(": ")[-1])
                except IndexError:
                    pass
                # Pass the line into the bot to train it.
                bot.conversation(input_words=sentence_in)

            training_file.close()

    existing_db_setup(connection)
    connection.close()

    mk_trainer(bot_data=directory, bot_model=bot_id_mk)


if __name__ == "__main__":
    """When called directly can be used to train one or both DB's and whether to erase the DB's beforehand """
    parser = argparse.ArgumentParser(description='Start training a chatbot with .txt files from /training')

    parser.add_argument('-f', '--fresh-db', action="store_true", dest="fresh_database",
                        help='Whether to create a clean DB')

    parser.add_argument('-l', '--log-level', action="store", dest="log_level", type=str, default='INFO',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], help='Logging level')

    parser.add_argument('-m', '--multi-bot', action="store_true", dest="multi_bot",
                        help='Whether to train two bots (second bot uses txt files under training_2')

    parser.add_argument('-n', '--no-prints', action="store_true", dest="no_prints",
                        help='Whether to print updates (seems to conflict with loading bars when run from shell files)')

    args = parser.parse_args()

    wipe_db = args.fresh_database

    log_level = args.log_level

    multi_bot = args.multi_bot

    no_prints = args.no_prints

    logging.basicConfig(level=log_level)

    if not no_prints:
        print(text_color("Training bot 1", UNDERLINE))

    bot_trainer(fresh_db=wipe_db)

    if multi_bot:
        if not no_prints:
            print(text_color("\nTraining bot 2", UNDERLINE))

            sleep(0.1)

        bot_trainer(dbname="words_database_2", fresh_db=wipe_db, directory=r'training_2', bot_id_mk="bot_2")
