import argparse
import logging
import os

from config.markovify_config import *

logger = logging.getLogger("markovify-model-deletion-logger")


def mk_model_delete(bot_model="bot_1"):
    if os.path.exists(f'{models_dir}/{bot_model}/model.json'):
        os.remove(f'{models_dir}/{bot_model}/model.json')
    else:
        logger.debug(f'Model: {models_dir}/{bot_model}/model.json does not currently exist, no deletion required.')


if __name__ == "__main__":
    """When called directly can be used to delete one or both MK models """
    parser = argparse.ArgumentParser(description='Start training a chatbot with .txt files from /training')

    parser.add_argument('-l', '--log-level', action="store", dest="log_level", type=str, default='INFO',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], help='Logging level')

    parser.add_argument('-m', '--multi-bot', action="store_true", dest="multi_bot",
                        help='Whether to train two bots (second bot uses txt files under training_2')

    args = parser.parse_args()

    log_level = args.log_level

    multi_bot = args.multi_bot

    logging.basicConfig(level=log_level)

    mk_model_delete()

    if multi_bot:
        mk_model_delete(bot_model="bot_2")
