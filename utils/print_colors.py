"""All colours for changing font colours are stored here, as well as the loading bar animation characters """

RED = "\033[1;31m"
ORANGE = "\033[01;38;5;202m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
LIGHT_BLUE = "\033[1;94m"
PURPLE = "\033[1;35m"
BIPur = '\033[1;95m'
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"
HEADER = '\033[95m'
OK_BLUE = '\033[94m'
OK_CYAN = '\033[96m'
OK_GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
END_C = '\033[0m'
UNDERLINE = '\033[4m'
LOAD_BAR = " ░▒▓█"


def text_color(text_to_color, color):
    """Changes a string to a specified colour for the terminal """
    return f'{color}{text_to_color}{RESET}'
