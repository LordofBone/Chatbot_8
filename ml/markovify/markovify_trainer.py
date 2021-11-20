import argparse
import json
import logging
import os
from time import sleep

import markovify
from tqdm.auto import tqdm

from config.markovify_config import *
from ml.markovify.markovify_delete_models import mk_model_delete
from utils.print_colors import *

logger = logging.getLogger("markovify-trainer-logger")

load_bar_mode = LOAD_BAR
load_bar_colour = '#FF00FF'


def mk_trainer(bot_data="training", bot_model="bot_1"):
    mk_model_delete(bot_model)

    # This determines the line count of all the training files in the training folder.
    file_count_total = 0
    training_file_names = []
    for filename in os.listdir(f'{dataset_dir}/{bot_data}'):
        if filename.endswith(".txt"):
            training_file_names.append(filename)
            file_count_total += 1
        else:
            continue

    if not training_file_names:
        raise Exception(
            f"No files in the {dataset_dir}/{bot_data} folder, please add .txt files with line-by-line conversations")

    with tqdm(total=file_count_total, postfix=text_color("Training MK Model", BIPur), leave=True, ascii=load_bar_mode,
              colour=load_bar_colour, dynamic_ncols=True) as progress_bar:
        combined_model = None
        for filename in training_file_names:
            with open(f'{dataset_dir}/{bot_data}/{filename}', encoding="ISO-8859-1") as f:
                model = markovify.Text(f, retain_original=False)
                if combined_model:
                    combined_model = markovify.combine(models=[combined_model, model])
                else:
                    combined_model = model

            progress_bar.update(1)

    model_json = combined_model.to_json()

    with open(f'{models_dir}/{bot_model}/model.json', 'w') as outfile:
        json.dump(model_json, outfile)


if __name__ == "__main__":
    """When called directly can be used to train one or both MK models """
    parser = argparse.ArgumentParser(description='Start training a chatbot with .txt files from /training')

    parser.add_argument('-l', '--log-level', action="store", dest="log_level", type=str, default='INFO',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], help='Logging level')

    parser.add_argument('-m', '--multi-bot', action="store_true", dest="multi_bot",
                        help='Whether to train two bots (second bot uses txt files under training_2')

    parser.add_argument('-n', '--no-prints', action="store_true", dest="no_prints",
                        help='Whether to print updates (seems to conflict with loading bars when run from shell files)')

    args = parser.parse_args()

    log_level = args.log_level

    multi_bot = args.multi_bot

    no_prints = args.no_prints

    logging.basicConfig(level=log_level)

    mk_trainer()

    if multi_bot:
        if not no_prints:
            print(text_color("\nTraining bot 2", UNDERLINE))

            sleep(0.1)

        mk_trainer(bot_data="training_2", bot_model="bot_2")
