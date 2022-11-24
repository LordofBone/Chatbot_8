from bootstrap.container_functions import *


def run_all():
    """
    Run the portainer container and the chatbot container
    :return:
    """
    update_portainer()
    run_portainer()
    run_chatbot()


if __name__ == '__main__':
    """
    This automates the process of running portainer and running the chatbot container
    """
    run_all()
