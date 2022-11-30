import argparse
import logging
from time import sleep

from bot_8 import person_manager, get_person_list
from utils.print_colors import *


def bot_conversation(name_1, name_2, fast_mode=False, portainer_boot=False):
    """Two bots are setup, initial replies are stored and then passed into the loop; passing each response from one
    bot into the input of the other """
    reply_1 = person_manager(person_name=name_1)

    person_manager(person_name=name_2, bot="bot_2", portainer_boot=portainer_boot)

    people = get_person_list()

    # todo: parameterize these with argparse
    people[name_1].max_short_term_memory = 100
    people[name_2].max_short_term_memory = 100

    reply_2 = people[name_2].conversation(reply_1)

    while True:
        reply_1 = people[name_1].conversation(reply_2)

        print(text_color(f'{name_1}: {reply_1}', PURPLE))

        if not fast_mode:
            sleep(1)

        reply_2 = people[name_2].conversation(reply_1)

        print(text_color(f'{name_2}: {reply_2}', YELLOW))

        if not fast_mode:
            sleep(1)


if __name__ == "__main__":
    """When called initiate two bots and begin their conversation with each other, this can be sued to configure the 
    names beyond the defaults """
    parser = argparse.ArgumentParser(description='Make 2 bots with different databases talk to each other')

    parser.add_argument('-n1', '--name-1', action="store", dest="name_1", type=str, default="Joe", help='Name of Bot 1')

    parser.add_argument('-n2', '--name-2', action="store", dest="name_2", type=str, default="Bob", help='Name of Bot 2')

    parser.add_argument('-f', '--fast-mode', action="store_true", dest="fast",
                        help='Whether to add a delay between responses')

    parser.add_argument('-l', '--log-level', action="store", dest="log_level", type=str, default='INFO',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], help='Logging level')

    parser.add_argument('-p', '--portainer-run', action="store_false", dest="portainer_run",
                        help='Whether to skip running of portainer/db container on startup')

    args = parser.parse_args()

    log_level = args.log_level
    bot_name_1 = args.name_1
    bot_name_2 = args.name_2
    bot_fast_mode = args.fast
    portainer_run = args.portainer_run

    logging.basicConfig(level=log_level)

    bot_conversation(name_1=bot_name_1, name_2=bot_name_2, fast_mode=bot_fast_mode, portainer_boot=portainer_run)
