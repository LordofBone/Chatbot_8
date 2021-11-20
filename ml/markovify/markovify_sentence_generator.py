import json
import logging

import markovify

from config.markovify_config import *

logger = logging.getLogger("markovify-sentence-generator-logger")


class MKGenerator:
    def __init__(self, bot="bot_1"):
        self.bot = bot

        with open(f'{models_dir}/{bot}/model.json') as json_file:
            model_json = json.load(json_file)

        self.loaded_model = markovify.Text.from_json(model_json)

        logger.debug(f'Model loaded: {models_dir}/{bot}/model.json')

    def generate_smart_sentence(self):
        generated_sentence = self.loaded_model.make_sentence()

        logger.debug(f'Testing sentence: {generated_sentence}')

        return generated_sentence


if __name__ == "__main__":
    Test = MKGenerator()
    print(Test.generate_smart_sentence())
