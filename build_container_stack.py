from bootstrap.container_functions import *


def build_all():
    """
    Build the portainer container and the chatbot container
    :return:
    """
    install_docker()
    build_portainer()
    run_portainer()
    build_chatbot()


if __name__ == '__main__':
    """
    This automates the process of building portainer and the chatbot container
    """
    build_all()
